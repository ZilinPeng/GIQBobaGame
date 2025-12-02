from .ingredient import Ingredient
from utils.constants import CUP_REGULAR, CUP_TALL, STRAW, SEAL
from .recipe import Recipe

class Drink:
    """
    Represents a drink sold in the shop.
    Uses a Recipe object for all ingredient logic.
    """
    def __init__(self, name, recipe: dict, basePrice, baseDesirability, size = 'regular'):
        self.name = name
        self.basePrice = basePrice
        self.recipe = Recipe(recipe, size)

        # Calculate final desirability
        self.desirability = baseDesirability + self.recipe.total_desirability()

        # Add size bonus
        if size == "tall":
            self.desirability += 0.30

    def setPrice(self, price: float):
        self.basePrice = price
