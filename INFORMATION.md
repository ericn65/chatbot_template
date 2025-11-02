# 🧠 Getting Started with `chatbot_template`

This short guide will help you **clone the repository**, **set up development tools**, and **run** the chatbot locally — perfect for students learning Python and clean coding.

---

## 🚀 1. Clone the repository

First, get the project onto your computer:

```bash
git clone https://github.com/ericn65/chatbot_template.git
cd chatbot_template
```

That’s it — now you’re inside the project folder.

---

## 🧰 2. Install `ruff` and `mypy`

We’ll start by installing two important tools for writing **high-quality Python code**:

| Tool        | Purpose                                   | Why it matters                                                                                    |
| ----------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 🧹 **Ruff** | A super-fast **linter** and **formatter** | It helps you keep your code clean, consistent, and PEP-8 compliant.                               |
| 🧠 **Mypy** | A **static type checker**                 | It checks for type errors before running code, making your programs safer and easier to maintain. |

Install both using **uv** (no virtual environment setup needed — uv handles that automatically!):

```bash
uv tool install ruff mypy
```

✅ Confirm installation:

```bash
ruff --version
mypy --version
```

---

## 📦 3. Install project dependencies

Now let’s install everything the project needs:

```bash
uv sync
```

This will:

* Create an isolated environment for the project (handled by `uv` automatically)
* Install all required dependencies from `pyproject.toml`
* Include dev dependencies (like testing or linting tools)

If you only need runtime dependencies:

```bash
uv sync --no-dev
```

---

## 🔍 4. Check your code with Ruff and Mypy

### Run Ruff

```bash
uv run ruff check .
```

This scans all Python files for style issues.

To automatically fix simple ones:

```bash
uv run ruff check . --fix
```

### Run Mypy

```bash
uv run mypy .
```

This checks for type errors (e.g., passing a string when a number was expected).

Keeping both checks clean helps you **catch bugs early** and **learn good habits** as you code.

---

## 🧪 5. Run the chatbot

Once everything looks good, run the project:

```bash
uv run python <path_to_entrypoint.py>
```

For example, if your main script is:

```bash
uv run python scripts/run_bot.py
```

💡 Tip: Check for a `.env.template` file — copy it to `.env` and fill in any required configuration (like API keys).

---

## 🧑‍💻 6. Develop your own features

When adding new code:

* Run `ruff` and `mypy` regularly
* Use `uv add <package>` to add dependencies
  *(e.g. `uv add requests`)*
* Test your code with:

  ```bash
  uv run pytest
  ```
* Commit only when everything passes

---

## 🧾 Example Configuration

Below are sample configurations to help students start clean.

### `pyproject.toml`

```toml
[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "W", "I"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
strict_optional = true
disallow_untyped_defs = true
ignore_missing_imports = true
```

### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.1
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
```

Install and run all hooks:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## 📝 Summary

| Step | Command                                 | Description          |
| ---- | --------------------------------------- | -------------------- |
| 1    | `git clone ...`                         | Get the project      |
| 2    | `uv tool install ruff mypy`             | Install dev tools    |
| 3    | `uv sync`                               | Install dependencies |
| 4    | `uv run ruff check .` / `uv run mypy .` | Code quality checks  |
| 5    | `uv run python ...`                     | Run chatbot          |
| 6    | `uv add <pkg>` / `uv run pytest`        | Develop and test     |

---

Happy coding! 🚀
