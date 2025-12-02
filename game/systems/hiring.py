import random
from models.staff import Staff
from game.config import WAGE_MULTIPLIER

NAMES = ["Alex", "Jordan", "Casey", "Riley", "Taylor",
         "Morgan", "Jamie", "Avery", "Sam", "Devon"]

def generate_candidates(n=3):
    candidates = []
    for _ in range(n):
        capacity = random.randint(1, 3)
        charm = random.randint(0, 3)
        wage_variation = random.randint(-5, 5)
        wage = capacity * WAGE_MULTIPLIER + charm * 3 + wage_variation
        candidates.append(Staff(random.choice(NAMES), wage, capacity, charm))
    return candidates