from pathlib import Path

import yaml

from chatbot_template.utils.teacher.enums import WorkflowError

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


class WorkflowEngine:
    """Run a questionnaire whose phases and validation rules live in YAML."""

    def __init__(self, yaml_path=None, errors_path=None):
        yaml_path = Path(yaml_path) if yaml_path else CONFIG_DIR / "workflow.yml"
        errors_path = (
            Path(errors_path) if errors_path else yaml_path.with_name("errors.yml")
        )
        with yaml_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
        with errors_path.open(encoding="utf-8") as file:
            self.errors = yaml.safe_load(file).get("ERRORS", {})
        self.questions = config["QUESTIONS"]
        self.order = config["PHASES"]
        if (
            not self.order
            or self.order[0] != "presentation"
            or self.order[-1] != "conclusion"
        ):
            raise ValueError(
                "PHASES must start with presentation and end with conclusion"
            )
        for lang, phases in self.questions.items():
            for phase in self.order:
                if not phases.get(phase):
                    raise ValueError(f"Missing questions: {lang}/{phase}")
                for question in phases[phase]:
                    if not (question.get("question") or question.get("text")):
                        raise ValueError(f"Missing prompt: {lang}/{phase}")
                    if question.get("type", "text") not in {"text", "number", "audio"}:
                        raise ValueError(f"Unsupported question type: {lang}/{phase}")

    def get_step(self, lang="es", phase="presentation", step=0):
        """Return a prompt, or None when the requested step does not exist."""
        section = self.questions.get(lang, {}).get(phase, [])
        if not 0 <= step < len(section):
            return None
        return section[step].get("text") or section[step].get("question")

    def next_phase(self, phase="presentation"):
        """Return the next configured phase."""
        if phase not in self.order or phase == self.order[-1]:
            return None
        return self.order[self.order.index(phase) + 1]

    def get_error_message(self, lang, error_type, **values):
        """Resolve a localized error with a safe fallback."""
        key = str(error_type).upper()
        messages = self.errors.get(lang, self.errors.get("es", {}))
        return messages.get(key, "Estado desconocido. Escribe /start.").format(**values)

    async def process_message(self, user_id, entry, state):
        """Validate an answer and advance without mutating the supplied state."""
        state = {**state, "answers": list(state.get("answers", []))}
        lang = state.get("lang", "es")
        phase = state.get("phase", "presentation")
        step = state.get("step", 0)
        text = entry.get("text", {}).get("body", "").strip()
        if phase == "presentation":
            aliases = {
                "esp": "es",
                "cast": "es",
                "castellano": "es",
                "español": "es",
                "cat": "ca",
                "catalan": "ca",
                "català": "ca",
            }
            selected = aliases.get(text.lower(), text.lower())
            if entry.get("type") != "text" or selected not in self.questions:
                return state, self.get_error_message(
                    lang, WorkflowError.LANG_NOT_SUPPORTED
                )
            state.update(lang=selected, phase=self.order[1], step=0)
            return state, self.get_step(selected, self.order[1], 0)
        if phase == "conclusion":
            return state, self.get_step(lang, "conclusion", 0)
        if phase not in self.order or not self.get_step(lang, phase, step):
            return state, self.get_error_message(lang, WorkflowError.UNKNOWN_STATE)

        question = self.questions[lang][phase][step]
        kind = question.get("type", "text")
        value = text
        if kind == "audio":
            value = entry.get("audio", {})
            if entry.get("type") != "audio" or not value.get("id"):
                return state, self.get_error_message(lang, WorkflowError.NOT_AUDIO)
            minimum = question.get("min_duration", 20)
            if value.get("duration", 0) < minimum:
                return state, self.get_error_message(
                    lang, WorkflowError.AUDIO_TOO_SHORT, min_duration=minimum
                )
        elif kind == "number":
            minimum, maximum = question.get("min", 0), question.get("max", 10)
            try:
                value = int(text) if entry.get("type") == "text" else None
            except ValueError:
                value = None
            if value is None or not minimum <= value <= maximum:
                return state, self.get_error_message(
                    lang, WorkflowError.INVALID_NUMBER, min=minimum, max=maximum
                )
        elif entry.get("type") != "text" or not text:
            return state, self.get_error_message(lang, WorkflowError.INVALID_TEXT)

        state["answers"].append({"phase": phase, "step": step, "value": value})
        step += 1
        if self.get_step(lang, phase, step) is None:
            phase, step = self.next_phase(phase), 0
        state.update(phase=phase, step=step)
        return state, self.get_step(lang, phase, step)
