import asyncio

from chatbot_template.utils.workflow import WorkflowEngine


async def trial():
    """Simulate the default questionnaire without connecting to a messaging service."""
    engine = WorkflowEngine()
    state = {"lang": "es", "phase": "presentation", "step": 0}
    print("BOT:", engine.get_step())
    for text in ["ES", "Ana", "gato", "11", "8", "lunes", "mañana"]:
        print("USER:", text)
        state, response = await engine.process_message(
            "user123", {"type": "text", "text": {"body": text}}, state
        )
        print("BOT:", response)
    for duration in [10, 25]:
        print("USER: audio de", duration, "segundos")
        state, response = await engine.process_message(
            "user123",
            {"type": "audio", "audio": {"id": "demo", "duration": duration}},
            state,
        )
        print("BOT:", response)


if __name__ == "__main__":
    asyncio.run(trial())
