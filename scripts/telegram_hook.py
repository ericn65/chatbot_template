import os

import httpx
from fastapi import FastAPI, Request

from chatbot_template.utils.workflow import WorkflowEngine

app = FastAPI()
engine = WorkflowEngine("mh_chatbot_dialogue/config/workflow.yml")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
user_states = {}
fake_db: list[dict] = []  # For testing purposes


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Webhook to receive messages from Telegram."""
    data = await request.json()
    print("Received Payload: ", data)

    if "message" not in data:
        return {"status": "ok"}

    message = data.get("message", {})
    text = message.get("text", "")
    user_id = message["from"]["id"]
    # msg_type = "text" if text else "audio" if "voice" in message else None

    if "text" in message:
        entry = {"type": "text", "text": {"body": message["text"]}}
    elif "voice" in message:
        entry = {
            "type": "audio",
            "audio": {
                "id": message["voice"]["file_id"],
                "duration": message["voice"]["duration"],
            },
        }
    else:
        entry = {"type": "unsupported"}

    if user_id not in user_states:
        user_states[user_id] = {"lang": "es", "phase": "presentation", "step": 0}
        text = engine.get_step("es", "presentation", 0) or ""
        await send_message(user_id, text)
        return {"status": "ok"}

    state = user_states[user_id]
    # entry = (
    #     {"type": msg_type, "text": {"body": text}}
    #     if text
    #     else {"type": "audio", "audio": {"id": message["voice"]["file_id"]}}
    # )

    new_state, response = await engine.process_message(user_id, entry, state)
    user_states[user_id] = new_state

    if isinstance(response, tuple) and response[0] == "AUDIO":
        await send_message(user_id, "🎙️ Audio recibido")
    else:
        await send_message(user_id, response)

    return {"status": "ok"}


async def send_message(chat_id: int, text: str):
    """Send a message to a Telegram user."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
