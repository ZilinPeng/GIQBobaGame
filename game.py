from config import *
from models.venue import Stand
from models.drink import Drink
from utils.constants import *
from systems.arrivals import generate_arrivals
from systems.turn_engine import process_turn
from systems.inventory import *
from systems.hiring import generate_candidates
from systems.advertising import calculate_ad_factor
import random

class Game:
    def __init__(self):
        self.cash = STARTING_CASH
        self.day = 1
        self.venue = Stand()
        self.employees = []
        self.stock = {ing: (100 if "Cup" in ing.name or ing.name in ("Straw","Seal") else 50)
                      for ing in [BOBA_PEARLS, CANE_SUGAR, REFINED_SUGAR, MILK, STRAWBERRY,
                                  LYCHEE, FRUIT_TEA, CUP_REGULAR, CUP_TALL, STRAW, SEAL]}
        self.menu = [
            Drink("Classic Milk Tea",
                  {BOBA_PEARLS: 1, CANE_SUGAR: 1, MILK: 1},
                  basePrice=4.50, baseDesirability=5)
        ]

        self.adFactor = 0
        self.dailyIngredientCost = 0
        self.dailyAdSpend = 0

    def pickDrink(self, customer):
        affordable = [d for d in self.menu if d.basePrice <= customer.maxAfford]
        if not affordable:
            return None
        weights = [d.desirability for d in affordable]
        return random.choices(affordable, weights=weights, k=1)[0]

    def single_turn(self):
        arrivals = generate_arrivals(self.venue, self.adFactor)
        served, lostStock, lostPat = process_turn(self)
        return served, arrivals, lostStock, lostPat