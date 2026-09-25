# chatbot_template

Project to integrate and develop chatbots.

Para configurar, ejecutar y modificar el bot de Telegram: [guía rápida con ejemplos](TELEGRAM_GUIA_RAPIDA.md).

---

## 🚀 Installation

You can install this project using [`uv`](https://github.com/astral-sh/uv):

```sh
uv sync --no-dev
```

## 📂 Project Structure

```
mh-chatbot-dialogue/
├── scripts/                 # Executable scripts to run package functionalities
├── mh_chatbot_dialogue/      # Main package
│   ├── __init__.py
│   └── utils                # Sub-package for utils modules
│       ├── env.py           # Environment related utils
│       └── random.py        # Seeding and random generation utils
├── tests/                   # Pytest suite
├── pyproject.toml           # Package configuration
└── README.md                # This file
```

## 💻 Development

To start developing some new stuff, first install all dependencies and pre-commit hooks:

```sh
uv sync
uv run pre-commit install
```

In order to add a new dependency be sure to do so with `uv` by running:

```sh
uv add <python-package-name>
```

to add it to a specific dependency-group there is the `--group` option, e.g. for development only:

```sh
uv add --group dev <python-package-name>
```

And to run a python script or module, you can simply use:

```sh
uv run <path-to-python-file>
```

## 🧪 Running Tests

To run the test suite:

```sh
uv run pre-commit run --all-files
uv run mypy
uv run pytest
```

---

## 👤 Maintainers

- **Èric Quintana Aguasca** - [eric@accexible.com](mailto:eric@accexible.com)
