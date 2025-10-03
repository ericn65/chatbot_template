import pandas as pd
import numpy as np
# import openai

# from Huggingface import transformers


class DataAnalysis:
    """
    It loads the information and has all the functions to work with the workflow.

    Parameters
    ----------
    bbdd_path : str
        The path to the `.csv` file.
    user_path : str
        The path to the `.csv`of information gotten from the user.

    Functions
    ---------

    """

    def __init__(self, bbdd_path: str, user_path: str, random_facts_path: str):
        self.bb_dd_info = pd.read_csv(bbdd_path)
        self.bb_dd_user_actions = pd.read_csv(user_path)
        self.bb_dd_random_facts = pd.read_csv(random_facts_path)
    
    def get_what_am_i_doing(self, day: str = "Never", moment: str = "Vas tarde") -> str:
        """
        Gets the information of the day and moment desired by the user.

        Parameters
        ----------
        day : str
            The day set by the user. Default = Never.
        moment : str
            The moment set by the user. Default = Vas tarde.

        Returns
        -------
        action : str
            The action to perform by the user that day.
        """
        action: str = self.bb_dd_info.loc[day][moment]

        return action
    

    def _get_animal(self, user_id: str) -> str:
        """
        El animal del xaval

        Returns
        -------
        el_animal : str
            El animal del xaval.
        """
        return self.bb_dd_user_actions.loc[user_id]["favourite_animal"]

    def get_animal_random_fact(self, wants_random_fact: bool = True) -> str:
        """
        Function that understands different animals and maths levels
        to get an answer.

        Parameters
        ----------
        wants_random_fact : bool
            The binary answer from the user.
        
        Returns
        -------
        random_fact : str
            The random fact specified for the user.
        """
        if wants_random_fact:
