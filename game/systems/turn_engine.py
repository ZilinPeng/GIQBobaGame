from .inventory import can_make, deduct_ingredients
from collections import deque

def process_turn(game):
    """
    Handles serving and patience decay.
    
    Returns:
        served_count, lostStock, lostPatience, drinks_served_list
    """
    served = 0
    lostStock = 0
    lostPatience = 0
    drinks_served_list = []   # NEW — track each drink sold

    # 1. SERVING
    capacity = sum(e.capacity for e in game.employees)
    to_serve = min(capacity, len(game.venue.line))

    for _ in range(to_serve):
        cust = game.venue.line.popleft()
        drink = cust.desiredDrink

        # Check inventory
        canMake = True
        for ing, qty in drink.recipe.items():
            if game.stock.get(ing, 0) < qty:
                canMake = False
                break

        if not canMake:
            lostStock += 1
            continue

        # Deduct ingredients
        for ing, qty in drink.recipe.items():
            game.stock[ing] -= qty

        # Register sale
        game.cash += drink.basePrice
        served += 1
        drinks_served_list.append(drink)   # NEW

    # 2. PATIENCE DECAY
    new_line = deque()

    for cust in game.venue.line:
        cust.patience -= 1
        if cust.patience > 0:
            new_line.append(cust)
        else:
            lostPatience += 1

    game.venue.line = new_line

    # NEW — return drinks_served_list
    return served, lostStock, lostPatience, drinks_served_list
