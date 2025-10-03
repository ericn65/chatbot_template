import yaml

from chatbot_template.utils.enums import WorkflowError


class WorkflowEngine:
    """
    Defines the workflow engine for managing the chatbot dialogues.

    Parameters
    ----------
    yaml_path : str
        Path to the YAML file defining the workflow.
        Default = /mh_chatbot_dialogue/config/workflow.yaml.

    Functions
    ---------
    get_step : (str, str, int) -> Optional[str]
        Retrieves the details of a specific step in the workflow.
    next_phase : (str) -> str | None
        Determines the next phase in the workflow based on the current step and
        user input.
    get_error_message : (str, WorkflowError) -> str
        Retrieves the error message corresponding to a specific error type and language.
    process_message : (str, dict, dict) -> tuple[dict, str]
        Processes a single message from a user and updates the state accordingly.
    """

    def __init__(self, yaml_path: str = "/mh_chatbot_dialogue/config/workflow.yaml"):
        with open(yaml_path) as file:
            config = yaml.safe_load(file)

        self.questions = config.get("QUESTIONS", {})
        self.errors = config.get("ERRORS", {})

    def get_step(
        self, lang: str = "es", phase: str = "presentation", step: int = 1
    ) -> str | None:
        """
        Retrieves the details of a specific step in the workflow.

        Parameters
        ----------
        lang : str
            The language of the flux (e.g., "es", "cat"). Default = "es".
        phase : str
            The current phase of the workflow. Default = "presentation".
        step : int
            The current step within the phase. Default = 1.

        Returns
        -------
        str | None
            The corresponding message to the step needed.
            Returns None if the step does not exist.
        """
        try:
            section = self.questions[lang][phase]

            if step < len(section):
                current = section[step]

                if "text" in current:
                    return current["text"]
                if "question" in current:
                    return current["question"]

            return None

        except KeyError:
            return None

    def next_phase(self, phase: str = "presentation") -> str | None:
        """
        Determines the next phase in the workflow based on the current step and
        user input.

        Parameters
        ----------
        phase : str
            The current phase of the workflow. Default = "presentation".

        Returns
        -------
        str | None
            The next phase in the workflow. Returns None if there is no next phase.
        """
        order = ["presentation", "formulaires", "audio_questions", "conclusion"]

        try:
            current_index = order.index(phase)
            return order[current_index + 1] if current_index + 1 < len(order) else None
        except ValueError:
            return None

    def get_error_message(self, lang: str, error_type: WorkflowError) -> str:
        """
        Retrieves the error message corresponding to a specific error type and language.

        Parameters
        ----------
        lang : str
            The language code (e.g., "es", "cat").
        error_type : WorkflowError
            The type of error (e.g., LANG_NOT_SUPPORTED, INVALID_NUMBER, NOT_AUDIO).

        Returns
        -------
        str
            The corresponding error message. If the language or error type is not found,
            returns a default message in English.
        """
        return self.errors.get(lang, {}).get(
            error_type.upper(), WorkflowError.UNKNOWNN_STATE
        )

    async def process_message(
        self, user_id: str, entry: dict, state: dict
    ) -> tuple[dict, str]:
        """
        Processes a single message from a user and updates the state accordingly.

        Parameters
        ----------
        user_id : str
            The unique identifier of the user.
        entry : dict
            The message entry containing the message type and content.
        state : dict
            The current state of the user in the workflow.

        Returns
        -------
        tuple[dict, str]
            (New state of the user, Response message or action)
        """
        lang: str = state.get("lang", "es")
        phase: str = state.get("phase", "presentation")
        msg_type = entry["type"]

        # ------ PRESENTATION PHASE ------
        if phase == "presentation":
            if msg_type == "text":
                text: str = entry["text"]["body"].strip().upper()
                if text in ["ES", "CAST", "CASTELLANO", "ESPAÑOL", "ESP"]:
                    state["lang"] = "es"
                elif text in ["CAT", "CATALAN", "CATALÀ"]:
                    state["lang"] = "ca"
                else:
                    return state, self.get_error_message(
                        lang, WorkflowError.LANG_NOT_SUPPORTED
                    )

                state["phase"] = "formulaires"
                state["step"] = 0
                msg = self.get_step(state["lang"], "formulaires", 0)
                if msg is not None:
                    return state, msg
                else:
                    return state, self.get_error_message(
                        lang, WorkflowError.UNKNOWNN_STATE
                    )
            else:
                return state, self.get_error_message(
                    lang, WorkflowError.LANG_NOT_SUPPORTED
                )

        # ------ FORMULAIRES PHASE ------
        elif phase == "formulaires":
            if msg_type == "text":
                text_formulaire: str = entry["text"]["body"].strip()
                if text_formulaire.isdigit() and 0 <= int(text_formulaire) <= 4:
                    state["step"] += 1
                    next_msg = self.get_step(lang, "formulaires", state["step"])

                    if next_msg:
                        return state, next_msg
                    else:
                        state["phase"] = "audio_questions"
                        state["step"] = 0
                        next_msg = self.get_step(lang, "audio_questions", 0)
                        if next_msg is not None:
                            return state, next_msg
                        else:
                            return state, self.get_error_message(
                                lang, WorkflowError.UNKNOWNN_STATE
                            )
                else:
                    return state, self.get_error_message(
                        lang, WorkflowError.INVALID_NUMBER
                    )
            else:
                return state, self.get_error_message(lang, WorkflowError.INVALID_NUMBER)

        # ------ AUDIO QUESTIONS PHASE ------
        elif phase == "audio_questions":
            audio_obj = entry.get("audio") or entry.get("voice")
            if audio_obj:
                audio_id = audio_obj.get("id") or audio_obj.get("file_id")
                audio_duration = audio_obj.get("duration", 0)

                if audio_duration < 20:
                    return state, self.get_error_message(
                        lang, WorkflowError.AUDIO_TOO_SHORT
                    )

                print(f"AUDIO:{audio_id}")

                state["step"] += 1
                next_msg = self.get_step(lang, "audio_questions", state["step"])

                if next_msg:
                    return state, next_msg
                else:
                    state["phase"] = "conclusion"
                    state["step"] = 0
                    msg = self.get_step(lang, "conclusion", 0)
                    return state, msg if msg is not None else self.get_error_message(
                        lang, WorkflowError.UNKNOWNN_STATE
                    )

            else:
                return state, self.get_error_message(lang, WorkflowError.NOT_AUDIO)

        # ------ CONCLUSION PHASE ------
        elif phase == "conclusion":
            msg = self.get_step(lang, "conclusion", 0)
            state.clear()
            return state, msg if msg is not None else self.get_error_message(
                lang, WorkflowError.UNKNOWNN_STATE
            )

        return state, self.get_error_message(lang, WorkflowError.UNKNOWNN_STATE)
