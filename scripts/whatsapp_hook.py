import os
import uuid

import aiofiles
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from chatbot_template.utils.workflow import WorkflowEngine

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATAA¡BASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
WORKFLOW_YAML_PATH = "/mh_chatbot_dialogue/config/workflow.yaml"

# Engine used
engine = WorkflowEngine(WORKFLOW_YAML_PATH)

# Memory Status
user_states = {}

# TEST PURPOSES
MEDIA_FOLDER = "/audios"
os.makedirs(MEDIA_FOLDER, exist_ok=True)
fake_db: list[dict] = []


# cosmos_client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
# db = cosmos_client.create_database_if_not_exists(DATABASE_NAME)
# container = db.create_container_if_not_exists(
#     id=CONTAINER_NAME,
#     partition_key="/user_id"
# )

app = FastAPI()


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Webhook to receive messages from WhatsApp."""
    data = await request.json()
    print("Received Payload: ", data)

    entry = data["entry"][0]["changes"][0]["value"]["messages"][0]
    user_id = entry["from"]
    # msg_type = entry["type"]

    if user_id not in user_states:
        user_states[user_id] = {"lang": "es", "phase": "presentation", "step": 0}
        text = engine.get_step("es", "presentation", 0) or ""
        await send_message(user_id, text)
        return {"status": "ok"}

    state = user_states[user_id]
    new_state, response = await engine.process_message(user_id, entry, state)

    user_states[user_id] = new_state

    if isinstance(response, tuple) and response[0] == "AUDIO":
        audio_id = response[1]
        audio_url = await get_media_url(audio_id)
        audio_path = os.path.join(MEDIA_FOLDER, f"{uuid.uuid4()}.ogg")
        await download_file(audio_url, audio_path)

        state["step"] += 1
        next_msg = engine.get_step(state["lang"], state["phase"], state["step"])
        if next_msg:
            await send_message(user_id, next_msg)
        else:
            state["phase"] = "conclusion"
            msg = engine.get_step(state["lang"], "conclusion", 0)
            await send_message(user_id, msg)

    else:
        await send_message(user_id, response)

    return {"status": "ok"}


async def get_media_url(media_id: str):
    """Gets the direct URL of a media file from WhatsApp."""
    url = f"https://graph.facebook.com/v20.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        return r.json()["url"]


async def download_file(url: str, dest_path: str):
    """Downloads a file from a URL to a local path."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 200:
            async with aiofiles.open(dest_path, "wb") as f:
                await f.write(r.content)


async def send_message(to: str, text: str):
    """Sends a text message to a Whatsapp user."""
    url = "https://graph.facebook.com/v20.0/me/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verification endpoint required by WhatsApp Cloud API."""
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get(
        "hub.verify_token"
    ) == os.getenv("VERIFY_TOKEN"):
        challenge = params.get("hub.challenge")
        if challenge is not None:
            return int(challenge)
        return {"status": "forbidden"}
    return {"status": "forbidden"}
