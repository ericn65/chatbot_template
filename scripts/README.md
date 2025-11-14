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

## WORKING

If it tells you something like "chatbot_template not found", you must install the correct project in the repo using the following commands:

`uv pip install -e .`

Which will install everything.

Afterwards, just run the command by usign:

`uv run python -m scripts.<your-main>`

alwasy do it without the `.py` whenever you use the `-m` thing.

To run a Dashboard use the following command:

`uv run streamlit run scripts/run_dashboard.py`

or

`uv run streamlit run scripts/run_correlations_dashboard.py`

And ensure that in the desired folders are the data and the things to add.
