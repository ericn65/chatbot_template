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

Consulta la [guía rápida de Telegram](../TELEGRAM_GUIA_RAPIDA.md).

```sh
uv run uvicorn scripts.telegram_hook:app --reload --port 8000
```

Requiere configurar `.env` y registrar el webhook HTTPS como explica la guía.

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

or

`uv run streamlit run scripts/run_training_dashboard.py`

And ensure that in the desired folders are the data and the things to add.
