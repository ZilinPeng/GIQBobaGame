import random

def can_make(drink, stock):
    return all(stock.get(ing, 0) >= qty for ing, qty in drink.recipe.items())

def deduct_ingredients(drink, stock):
    for ing, qty in drink.recipe.items():
        stock[ing] -= qty

def generate_offers(ingredients):
    """
    Create bulk & retail offers for every ingredient for this morning.
    Returns a dict: {ingredient: {"bulk": {...}, "retail": {...}}}
    """
    offers = {}
    for ing in ingredients:
        base = ing.unit_cost
        offers[ing] = {
            "bulk":   {
                "min": 200,
                "unit": round(base * random.uniform(0.7, 0.85), 3)
            },
            "retail": {
                "min": 1,
                "unit": round(base * random.uniform(1.05, 1.20), 3)
            }
        }
    return offers

