import random
from ..utils.math_utils import poisson
from ..models.customer import Customer

def generate_arrivals(venue, multiplier):
    lam = venue.footTraffic * (1 + multiplier)
    return poisson(lam)

def enqueue_customers(game, arrivals):
    for _ in range(arrivals):
        cust = Customer(game.venue.basePatience)
        drink = game.pickDrink(cust)
        if drink is None:
            continue
        cust.desiredDrink = drink

        if len(game.venue.line) < game.venue.maxLine:
            game.venue.line.append(cust)
        else:
            game.lostQueue += 1