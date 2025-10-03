import logging
import os
import random

import numpy as np

MAX_SEED_VALUE = np.iinfo(np.uint32).max
MIN_SEED_VALUE = np.iinfo(np.uint32).min

pylogger = logging.getLogger(__name__)


def _get_random_seed(
    min_seed_value: int = MIN_SEED_VALUE, max_seed_value: int = MAX_SEED_VALUE
) -> int:
    """
    Generate a random seed within specified bounds.

    Parameters
    ----------
    min_seed_value : int
        Minimum integer seed value (inclusive).
    max_seed_value : int
        Maximum integer seed value (inclusive).

    Returns
    -------
    int
        Randomly selected seed between min_seed_value and max_seed_value.
    """
    return random.randint(min_seed_value, max_seed_value)  # noqa: S3


def seed_everything(
    seed: int | None = None,
    min_seed_value: int = MIN_SEED_VALUE,
    max_seed_value: int = MAX_SEED_VALUE,
) -> int:
    """
    Set the seed for pseudo-random number generators in Python's `random` module,
    PyTorch and NumPy.

    If the provided seed is out of bounds, a new seed will be selected randomly
    within the valid range.

    Additionally, sets the following environment variable to the same value:
    - `PL_GLOBAL_SEED`: passed to spawned subprocesses (e.g., `ddp_spawn` backend).

    Function based on `seed_everything` from PyTorch Lightning:
    https://github.com/Lightning-AI/lightning/blob/f6a36cf2204b8a6004b11cf0e21879872a63f414/src/lightning/fabric/utilities/seed.py#L19

    Parameters
    ----------
    seed : int, optional
        The integer value to set as the global random state seed.
        If `None`, the seed will be read from the `PL_GLOBAL_SEED` env variable
        when set or selected randomly otherwise.

    Returns
    -------
    int
        The seed value that was set.
    """
    if seed is None:
        env_seed = os.environ.get("PL_GLOBAL_SEED")
        if env_seed is None:
            seed = _get_random_seed()
            pylogger.warning(f"No seed found, seed set to {seed}")
        else:
            try:
                seed = int(env_seed)
            except ValueError:
                seed = _get_random_seed()
                pylogger.warning(
                    f"Invalid seed found: {env_seed!r}, seed set to {seed}"
                )
    elif not isinstance(seed, int):
        seed = int(seed)

    if not (min_seed_value <= seed <= max_seed_value):
        pylogger.warning(
            f"{seed} is out of bounds (must be between {min_seed_value}"
            f"and {max_seed_value}). Selecting a new random seed."
        )
        seed = _get_random_seed()

    os.environ["PL_GLOBAL_SEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pylogger.info("PyTorch not installed; skipping torch seeding.")

    pylogger.info(f"Seed set to {seed}")

    return seed
