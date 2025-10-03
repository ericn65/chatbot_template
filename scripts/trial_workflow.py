import asyncio

from chatbot_template.utils.workflow import WorkflowEngine


async def trial():
    """It is just a trial before using the webhook to WHATSAPP."""
    engine = WorkflowEngine("mh_chatbot_dialogue/config/workflow.yml")

    state = {"lang": "es", "phase": "presentation", "step": 0}
    user_id = "user123"

    # Simular que el usuario elige idioma
    entry = {"type": "text", "text": {"body": "ES"}}
    new_state, response = await engine.process_message(user_id, entry, state)
    print("BOT:", response)
    print("NEW STATE:", new_state)

    # Simular respuesta numérica
    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    # Simular respuesta inválida
    entry = {"type": "text", "text": {"body": "9"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "4"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {"type": "text", "text": {"body": "2"}}
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 25,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 10,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 30,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 22,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 25,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)

    entry = {
        "type": "audio",
        "audio": {
            "id": "fake-audio-id-123",
            "mime_type": "audio/ogg",
            "voice": True,
            "duration": 21,
        },
    }
    new_state, response = await engine.process_message(user_id, entry, new_state)
    print("BOT:", response)


asyncio.run(trial())
