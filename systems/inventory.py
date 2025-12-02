def can_make(drink, stock):
    return all(stock.get(ing, 0) >= qty for ing, qty in drink.recipe.items())

def deduct_ingredients(drink, stock):
    for ing, qty in drink.recipe.items():
        stock[ing] -= qty