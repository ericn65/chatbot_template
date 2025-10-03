import logging
import os
from contextlib import contextmanager

import dotenv

pylogger = logging.getLogger(__name__)


def get_env(env_name: str, default: str | None = None) -> str:
    """
    Safely retrieves the value of an environment variable.

    If the environment variable is not defined or is empty, raises an error unless
    a default value is provided.

    Parameters
    ----------
    env_name : str
        The name of the environment variable to retrieve.
    default : Optional[str], optional
        The default value to return if the environment variable is not set or is empty.
        If not provided, an error will be raised in such cases.

    Returns
    -------
    str
        The value of the environment variable, or the default value if provided.

    Raises
    ------
    KeyError
        If the environment variable is not defined and no default value is provided.
    ValueError
        If the environment variable is empty and no default value is provided.
    """
    if env_name not in os.environ:
        if default is None:
            message = f"{env_name} not defined and no default value is present!"
            pylogger.error(message)
            raise KeyError(message)
        return default

    env_value: str = os.environ[env_name]
    if not env_value:
        if default is None:
            message = (
                f"{env_name} has yet to be configured and no default value is present!"
            )
            pylogger.error(message)
            raise ValueError(message)
        return default

    return env_value


def load_envs(env_file: str | None = None) -> None:
    """
    Load environment variables from a file.

    This is equivalent to sourcing the file in a shell.

    It is possible to define all the system specific variables in the `env_file`.

    Parameters
    ----------
    env_file : str, optional
        The file that defines the environment variables to use.
        If None, it searches for a `.env` file in the project.
    """
    if env_file is None:
        env_file = dotenv.find_dotenv(usecwd=True)
    dotenv.load_dotenv(dotenv_path=env_file, override=True)


@contextmanager
def environ(**kwargs):
    """
    Temporarily set the process environment variables.

    This function allows to temporarily modify the environment variables
    within a context. Once the context is exited, the original environment
    variables are restored.

    Based on: https://stackoverflow.com/a/34333710

    Parameters
    ----------
    **kwargs : dict of str
        Environment variables to set, where the key is the variable name
        and the value is the variable value.

    Examples
    --------
    >>> with environ(PLUGINS_DIR='test/plugins'):
    ...     "PLUGINS_DIR" in os.environ
    True
    >>> "PLUGINS_DIR" in os.environ
    False
    """
    # Use a copy of os.environ to ensure we have an independent backup.
    old_environ = os.environ.copy()
    os.environ.update(kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
