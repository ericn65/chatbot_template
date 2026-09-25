import asyncio
import hmac
import json
import logging
import os
import re
import sqlite3
from contextlib import asynccontextmanager, closing
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from chatbot_template.utils.workflow import WorkflowEngine

# HTTP client logs include request URLs, which contain the bot token.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class Chat(BaseModel):
    """Fields used to route a Telegram message."""

    id: int
    type: str


class Voice(BaseModel):
    """Metadata needed to validate and retrieve a voice note."""

    file_id: str
    duration: int = Field(ge=0)


class Message(BaseModel):
    """Supported incoming message fields."""

    chat: Chat
    text: str | None = None
    voice: Voice | None = None


class Update(BaseModel):
    """Ignore update kinds other than ordinary messages."""

    update_id: int
    message: Message | None = None


class ConversationStore:
    """Persist conversation snapshots and reply delivery status in SQLite."""

    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "conversations.sqlite3"
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS states "
                "(chat_id INTEGER PRIMARY KEY, state TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS updates "
                "(update_id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, "
                "response TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0)"
            )

    def load(self, chat_id):
        """Load the last committed conversation, including its answers."""
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute(
                "SELECT state FROM states WHERE chat_id = ?", (chat_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def reply(self, update_id):
        """Return a previously prepared reply to avoid processing an update twice."""
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute(
                "SELECT chat_id, response, sent FROM updates WHERE update_id = ?",
                (update_id,),
            ).fetchone()

    def save(self, update_id, chat_id, state, response):
        """Commit the new state and pending reply in one transaction."""
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                "INSERT OR REPLACE INTO states VALUES (?, ?)",
                (chat_id, json.dumps(state)),
            )
            db.execute(
                "INSERT INTO updates (update_id, chat_id, response) VALUES (?, ?, ?)",
                (update_id, chat_id, response),
            )

    def mark_sent(self, update_id):
        """Record that Telegram accepted the reply."""
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE updates SET sent = 1 WHERE update_id = ?", (update_id,))


async def telegram_call(client, token, method, payload):
    """Call Telegram without exposing credential-bearing URLs in errors."""
    try:
        response = await client.post(
            f"https://api.telegram.org/bot{token}/{method}", json=payload
        )
        response.raise_for_status()
        data = response.json()
        if data.get("ok") is not True:
            raise ValueError("Telegram rejected the request")
        return data["result"]
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(
            502, "No se pudo completar la petición a Telegram"
        ) from None


async def download_voice(app, file_id, update_id):
    """Download an accepted voice note under a locally generated filename."""
    result = await telegram_call(
        app.state.client, app.state.token, "getFile", {"file_id": file_id}
    )
    remote_path = result.get("file_path")
    if not remote_path:
        raise HTTPException(502, "Telegram no devolvió la ruta del audio")
    destination = app.state.directory / "audios" / f"{update_id}.ogg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".part")
    try:
        async with app.state.client.stream(
            "GET", f"https://api.telegram.org/file/bot{app.state.token}/{remote_path}"
        ) as response:
            response.raise_for_status()
            with temporary.open("wb") as file:
                async for chunk in response.aiter_bytes():
                    file.write(chunk)
        temporary.replace(destination)
    except httpx.HTTPError:
        temporary.unlink(missing_ok=True)
        raise HTTPException(502, "No se pudo descargar el audio") from None
    return str(destination)


def create_app():
    """Create an application with configuration checked on server startup."""

    @asynccontextmanager
    async def lifespan(app):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()
        if not token:
            raise RuntimeError("Configura TELEGRAM_BOT_TOKEN en .env")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", secret):
            raise RuntimeError(
                "Configura TELEGRAM_WEBHOOK_SECRET: 1-256 letras, números, _ o -"
            )
        app.state.token, app.state.secret = token, secret
        app.state.directory = Path(
            os.getenv("TELEGRAM_DATA_DIR", "data/telegram")
        ).resolve()
        app.state.store = ConversationStore(app.state.directory)
        app.state.engine = WorkflowEngine()
        app.state.lock = asyncio.Lock()
        async with httpx.AsyncClient(timeout=30) as client:
            app.state.client = client
            yield

    app = FastAPI(lifespan=lifespan)

    @app.post("/webhook")
    async def telegram_webhook(request: Request):
        supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(supplied.encode(), app.state.secret.encode()):
            raise HTTPException(403, "Secreto del webhook incorrecto")
        try:
            update = Update.model_validate(await request.json())
        except ValueError:
            raise HTTPException(422, "Update de Telegram inválido") from None
        message = update.message
        if message is None or message.chat.type != "private":
            return {"status": "ok"}

        async with app.state.lock:
            store = app.state.store
            previous = store.reply(update.update_id)
            if previous:
                chat_id, response, sent = previous
                if sent:
                    return {"status": "ok"}
            else:
                chat_id = message.chat.id
                state = store.load(chat_id)
                words = (message.text or "").split()
                command = words[0].split("@")[0].lower() if words else ""
                if not state or command in {"/start", "/reset"}:
                    state = {
                        "lang": "es",
                        "phase": "presentation",
                        "step": 0,
                        "answers": [],
                    }
                    response = app.state.engine.get_step()
                else:
                    entry: dict[str, Any] = {"type": "unsupported"}
                    if message.text is not None:
                        entry = {"type": "text", "text": {"body": message.text}}
                    elif message.voice is not None:
                        entry = {
                            "type": "audio",
                            "audio": {
                                "id": message.voice.file_id,
                                "duration": message.voice.duration,
                            },
                        }
                    new_state, response = await app.state.engine.process_message(
                        str(chat_id), entry, state
                    )
                    if (
                        len(new_state["answers"]) > len(state.get("answers", []))
                        and entry["type"] == "audio"
                        and message.voice is not None
                    ):
                        audio_path = await download_voice(
                            app, message.voice.file_id, update.update_id
                        )
                        new_state["answers"][-1]["value"]["path"] = audio_path
                    state = new_state
                store.save(update.update_id, chat_id, state, response)
            await telegram_call(
                app.state.client,
                app.state.token,
                "sendMessage",
                {"chat_id": chat_id, "text": response},
            )
            store.mark_sent(update.update_id)
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
