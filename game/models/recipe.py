from utils.constants import CUP_TALL, CUP_REGULAR, STRAW, SEAL

class Recipe:
    """
    Represents a drink recipe including ingredients and packaging.
    Automatically injects required packaging based on size.
    """
    def __init__(self, ingredients: dict, size):
        # Copy to avoid mutating the input dictionary
        self.ingredients = dict(ingredients)
        self.size = size

        # Add packaging
        cup = CUP_TALL if size == "tall" else CUP_REGULAR
        self.ingredients[cup] = self.ingredients.get(cup, 0) + 1
        self.ingredients[STRAW] = self.ingredients.get(STRAW, 0) + 1
        self.ingredients[SEAL] = self.ingredients.get(SEAL, 0) + 1

    def total_desirability(self):
        """
        Sum desirability contributions of all ingredients.
        Does NOT include base drink desirability (Drink handles that).
        """
        return sum(ing.addedDesirability * qty for ing, qty in self.ingredients.items())

    def items(self):
        """Shorthand to iterate ingredients like a dict."""
        return self.ingredients.items()