from ingredient import Ingredient
from constants import CUP_REGULAR, CUP_TALL, STRAW, SEAL

class Drink:
    def __init__(self, name, recipe, basePrice, baseDesirability, size="regular"):
        self.name = name
        self.recipe = recipe
        self.basePrice = basePrice
        self.size = size

        # Add packaging automatically
        cup = CUP_TALL if size == "tall" else CUP_REGULAR
        recipe[cup] = recipe.get(cup, 0) + 1
        recipe[STRAW] = recipe.get(STRAW, 0) + 1
        recipe[SEAL] = recipe.get(SEAL, 0) + 1

        # Calculate desirability
        self.desirability = baseDesirability
        for ing, qty in recipe.items():
            self.desirability += ing.addedDesirability * qty

        if size == "tall":
            self.desirability += 0.30  # tall size bonus

    def setPrice(self, price):
        self.basePrice = price