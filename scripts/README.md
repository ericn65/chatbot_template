# How to run?

First remember to:

`uv sync`

And then:

`uv run scripts/trial_workflow.py`

or

`uv run scripts/whatsapp_hook.py`

Finally, to run it locally:

`uv run uvicorn scripts.{social_network}_hook:app --reload --port 8000`

## Telegram

We have developed this bot just to test locally interactions and it might have been removed. However, to find the bot look for:

`t.me/accexible_bot`

Ask `eric@accexible.com` for a token and just have fun by:

`uv run scripts/telegram_hook.py`

It is really useful to test any new change done here without breaking the system.

## DISCLAIMER

It is still under development and it might not work correctly.

curl -X POST "https://api.telegram.org/bot7934142036:AAHmX9QSskQorXz9B4dAvZ3I6kIxg7rf1KE/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://uncurbable-hortense-comedically.ngrok-free.dev/webhook"}'
