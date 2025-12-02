from systems.inventory import can_make, deduct_ingredients

def process_turn(game):
    served = 0
    lostStock = 0
    lostPat = 0

    capacity = sum(e.capacity for e in game.employees)
    for _ in range(min(capacity, len(game.venue.line))):
        cust = game.venue.line.popleft()

        if not can_make(cust.desiredDrink, game.stock):
            lostStock += 1
            continue

        deduct_ingredients(cust.desiredDrink, game.stock)
        game.cash += cust.desiredDrink.basePrice
        served += 1

    # patience decay
    new_queue = []
    for cust in game.venue.line:
        cust.patience -= 1
        if cust.patience > 0:
            new_queue.append(cust)
        else:
            lostPat += 1

    game.venue.line = new_queue
    return served, lostStock, lostPat