import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from chatbot_template.utils.workflow import WorkflowEngine
from scripts.telegram_hook import ConversationStore, create_app


def answer(engine, text, state):
    """Run a text answer through the asynchronous engine."""
    return asyncio.run(
        engine.process_message("1", {"type": "text", "text": {"body": text}}, state)
    )


def test_questionnaire_validation_and_completion():
    """Reject invalid inputs and finish the configured questionnaire."""
    engine = WorkflowEngine()
    state = {"lang": "es", "phase": "presentation", "step": 0}
    invalid, reply = answer(engine, "CAT", state)
    assert invalid["phase"] == "presentation"
    assert "ES" in reply
    state, _ = answer(engine, "ES", state)
    for text in ["Ana", "gato"]:
        state, _ = answer(engine, text, state)
    original = json.dumps(state)
    invalid, reply = answer(engine, "11", state)
    assert invalid == state
    assert "0 y 10" in reply
    state, _ = answer(engine, "10", state)
    assert json.dumps(invalid) == original
    for text in ["lunes", "mañana"]:
        state, _ = answer(engine, text, state)
    assert state["phase"] == "audio_questions"
    unchanged, _ = answer(engine, "hola", state)
    assert unchanged == state
    for duration in [19, 20]:
        result, reply = asyncio.run(
            engine.process_message(
                "1",
                {"type": "audio", "audio": {"id": "voice", "duration": duration}},
                state,
            )
        )
        if duration == 19:
            assert result == state
            assert "20 segundos" in reply
        else:
            assert result["phase"] == "conclusion"
            assert len(result["answers"]) == 6
    again, reply = answer(engine, "hola", result)
    assert again == result
    assert "/start" in reply


@pytest.fixture
def bot(tmp_path, monkeypatch):
    """Create an isolated server backed by mocked Telegram responses."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("TELEGRAM_DATA_DIR", str(tmp_path))
    app = create_app()
    calls = []

    def transport(request):
        calls.append(request)
        if request.url.path.endswith("getFile"):
            return httpx.Response(
                200, json={"ok": True, "result": {"file_path": "voice/file.oga"}}
            )
        if request.method == "GET":
            return httpx.Response(200, content=b"fake-ogg")
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    with TestClient(app) as client:
        original = app.state.client
        app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
        yield app, client, calls
        asyncio.run(app.state.client.aclose())
        app.state.client = original


def post(client, update_id, text=None, voice=None, chat_id=42, chat_type="private"):
    """Send a Telegram-shaped update with the configured webhook secret."""
    message = {"chat": {"id": chat_id, "type": chat_type}, "from": {"id": 999}}
    if text is not None:
        message["text"] = text
    if voice is not None:
        message["voice"] = voice
    return client.post(
        "/webhook",
        json={"update_id": update_id, "message": message},
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )


def test_webhook_complete_persistent_conversation_and_reset(bot):
    """Persist answers and audio, deduplicate updates and reset on command."""
    app, client, calls = bot
    for number, text in enumerate(
        ["/start", "ES", "Ana", "gato", "8", "lunes", "mañana"]
    ):
        assert post(client, number, text).status_code == 200
    assert (
        post(client, 7, voice={"file_id": "voice", "duration": 20}).status_code == 200
    )
    state = ConversationStore(app.state.directory).load(42)
    assert state["phase"] == "conclusion"
    assert len(state["answers"]) == 6
    assert (app.state.directory / "audios/7.ogg").read_bytes() == b"fake-ogg"
    assert all(
        json.loads(r.content)["chat_id"] == 42
        for r in calls
        if r.url.path.endswith("sendMessage")
    )
    count = len(calls)
    assert (
        post(client, 7, voice={"file_id": "voice", "duration": 20}).status_code == 200
    )
    assert len(calls) == count
    assert post(client, 8, "/reset").status_code == 200
    assert app.state.store.load(42)["answers"] == []


def test_authentication_ignored_updates_and_invalid_payload(bot):
    """Reject unauthorized or malformed updates and ignore unsupported chats."""
    app, client, calls = bot
    assert client.post("/webhook", json={}).status_code == 403
    headers = {"X-Telegram-Bot-Api-Secret-Token": "test-secret"}
    assert client.post("/webhook", json={}, headers=headers).status_code == 422
    assert (
        client.post("/webhook", json={"update_id": 1}, headers=headers).status_code
        == 200
    )
    assert post(client, 2, "hola", chat_type="group").status_code == 200
    assert not calls
    assert app.state.store.load(42) is None


@pytest.mark.parametrize("failure", ["http", "api", "network"])
def test_failed_send_retries_without_advancing_twice(bot, failure):
    """Retry pending replies without recording an answer twice."""
    app, client, calls = bot
    post(client, 0, "/start")
    post(client, 1, "ES")
    good_client = app.state.client

    def fail(request):
        if failure == "network":
            raise httpx.ConnectError("fake", request=request)
        return httpx.Response(500 if failure == "http" else 200, json={"ok": False})

    app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    response = post(client, 2, "Ana")
    assert response.status_code == 502
    assert "test-token" not in response.text
    asyncio.run(app.state.client.aclose())
    app.state.client = good_client
    assert post(client, 2, "Ana").status_code == 200
    assert len(app.state.store.load(42)["answers"]) == 1
    assert app.state.store.reply(2)[2] == 1


def test_restart_resumes_state(bot):
    """Resume a conversation after creating another server instance."""
    app, client, calls = bot
    post(client, 0, "/start")
    post(client, 1, "ES")
    post(client, 2, "Ana")
    with TestClient(create_app()) as restarted:
        original = restarted.app.state.client
        restarted.app.state.client = app.state.client
        assert post(restarted, 3, "gato").status_code == 200
        assert restarted.app.state.store.load(42)["step"] == 2
        restarted.app.state.client = original


def test_missing_configuration(monkeypatch):
    """Fail at startup when the token is absent."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with (
        pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"),
        TestClient(create_app()),
    ):
        pass


def test_download_failure_does_not_accept_answer(bot):
    """Keep the current audio question pending when downloading fails."""
    app, client, calls = bot
    for number, text in enumerate(
        ["/start", "ES", "Ana", "gato", "8", "lunes", "mañana"]
    ):
        post(client, number, text)
    original_state = app.state.store.load(42)
    good_client = app.state.client

    def fail(request):
        if request.method == "GET":
            return httpx.Response(500)
        return httpx.Response(
            200, json={"ok": True, "result": {"file_path": "voice/f.oga"}}
        )

    app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    assert (
        post(client, 7, voice={"file_id": "voice", "duration": 20}).status_code == 502
    )
    assert app.state.store.load(42) == original_state
    assert app.state.store.reply(7) is None
    assert not list((app.state.directory / "audios").glob("*.part"))
    asyncio.run(app.state.client.aclose())
    app.state.client = good_client
    assert (
        post(client, 7, voice={"file_id": "voice", "duration": 20}).status_code == 200
    )


def test_invalid_state_returns_configured_error():
    """Handle stale phases without an enum or missing-key exception."""
    engine = WorkflowEngine()
    state, response = answer(engine, "hola", {"phase": "missing", "lang": "es"})
    assert "/start" in response


@pytest.mark.parametrize("secret", ["", "invalid secret", "a" * 257])
def test_invalid_secret_prevents_startup(monkeypatch, secret):
    """Require a secret compatible with Telegram before exposing the webhook."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", secret)
    with (
        pytest.raises(RuntimeError, match="TELEGRAM_WEBHOOK_SECRET"),
        TestClient(create_app()),
    ):
        pass
