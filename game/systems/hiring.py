import random
from game.utils.constants import EMPLOYEE_POOL

def generate_candidates(game, n=3):
    """
    Picks n candidates from constant pool.
    Rules:
    - Cannot pick employees already hired.
    - Picks UNIQUE employees each time.
    """
    hired_names = {emp.name for emp in game.employees}

    # Filter out already hired employees
    remaining = [e for e in EMPLOYEE_POOL if e.name not in hired_names]

    # If fewer remaining than needed, reduce n
    n = min(n, len(remaining))

    return random.sample(remaining, k=n)