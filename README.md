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

El `Makefile` usa `uv` para ejecutar las herramientas del proyecto:

```sh
make install              # Dependencias de desarrollo
make test                 # Ruff, mypy y tests sin cobertura
make coverage             # Cobertura: terminal, coverage.xml y htmlcov/index.html
make test TEST_ARGS='tests/utils/teacher/test_training_plots.py'
make test TEST_ARGS='-k forecasting'
make help                 # Todos los comandos disponibles
```

Otros comandos utiles: `make lint` comprueba Ruff y el formato sin modificar
archivos; `make format` aplica correcciones y formato; `make typecheck` ejecuta
mypy; `make check` es un alias de `make test` (Ruff, mypy y tests).
Si falla alguna comprobacion, `make test` termina con error.
`make hooks` instala los hooks y
`make pre-commit` los ejecuta sobre todos los archivos (puede modificarlos).

Para las aplicaciones: `make dashboard`, `make dashboard-training`,
`make dashboard-correlations` y `make telegram PORT=8000`. Telegram requiere
la configuracion descrita en su [guia rapida](TELEGRAM_GUIA_RAPIDA.md).

Tambien puedes ejecutar las herramientas directamente:

```sh
uv run pre-commit run --all-files
uv run mypy
uv run pytest
```

---

## 👤 Maintainers

- **Èric Quintana Aguasca** - [eric@accexible.com](mailto:eric@accexible.com)
