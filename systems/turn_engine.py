from systems.inventory import can_make, deduct_ingredients
from collections import deque

def process_turn(game):
    """
    Handles serving and patience decay.
    Returns (served, lostStock, lostPatience)
    """
    served = 0
    lostStock = 0
    lostPatience = 0

    # 1. SERVING
    capacity = sum(e.capacity for e in game.employees)
    to_serve = min(capacity, len(game.venue.line))

    for _ in range(to_serve):
        cust = game.venue.line.popleft()

        # Check inventory
        canMake = True
        for ing, qty in cust.desiredDrink.recipe.items():
            if game.stock.get(ing, 0) < qty:
                canMake = False
                break

        if not canMake:
            lostStock += 1
            continue

        # Deduct inventory
        for ing, qty in cust.desiredDrink.recipe.items():
            game.stock[ing] -= qty

        game.cash += cust.desiredDrink.basePrice
        served += 1

    # 2. PATIENCE DECAY — THE PART THAT BROKE YOUR GAME
    new_line = deque()     # <-- FIX: MUST be deque()

    for cust in game.venue.line:
        cust.patience -= 1
        if cust.patience > 0:
            new_line.append(cust)
        else:
            lostPatience += 1

    game.venue.line = new_line  # <-- FIX: Do NOT assign list

    return served, lostStock, lostPatience

