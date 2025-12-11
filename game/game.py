from game.config import *
from .models.venue import Stand
from .models.drink import Drink
from .models.customer import Customer
from .utils.constants import *
from .systems.arrivals import generate_arrivals
from .systems.turn_engine import process_turn
from .systems.inventory import *
from .systems.hiring import generate_candidates
from .systems.advertising import calculate_ad_factor
from .models.staff import Staff
import random


class Game:
    def __init__(self):
        # --- Core Game State ---
        self.cash = STARTING_CASH
        self.day = 1
        self.venue = Stand()
        self.employees = [Staff("Owner", wage=0, capacity=1, charm=1, reliability=10)]

        # --- Inventory ---
        ingredients = INGREDIENTS

        self.ingredients = ingredients
        self.stock = {
            ing: (100 if ing in {CUP_REGULAR, CUP_TALL, STRAW, SEAL} else 50)
            for ing in ingredients
        }

        # --- Default Menu ---
        self.menu = [
            Drink(
                "Classic Milk Tea",
                {BOBA_PEARLS: 1, CANE_SUGAR: 1, WHOLE_MILK: 1},
                basePrice=4.50,
                baseDesirability=5
            )
        ]

        # --- Daily Parameters ---
        self.adBudget = 0
        self.adFactor = 0
        self.dailyIngredientCost = 0
        self.dailyAdSpend = 0

    # -------------------------------------------------------
    # Drink Selection Logic
    # -------------------------------------------------------
    def pickDrink(self, customer):
        affordable = [d for d in self.menu if d.basePrice <= customer.maxAfford]
        if not affordable:
            return None

        # Add charm influence
        total_charm = sum(e.charm for e in self.employees)
        weights = [d.desirability * (1 + 0.05 * total_charm) for d in affordable]

        return random.choices(affordable, weights=weights, k=1)[0]

    # -------------------------------------------------------
    # Single Turn Simulation
    # -------------------------------------------------------
    def single_turn(self):
        """
        Runs ONE turn.
        Returns:
            served_count, lost_queue, lost_stock, lost_patience, drinks_served_list
        """

        # 1. Customer arrivals
        arrivals = generate_arrivals(self.venue, self.adFactor)

        lost_queue = 0
        for _ in range(arrivals):
            cust = Customer(self.venue.basePatience)
            drink = self.pickDrink(cust)
            if drink is None:
                continue

            cust.desiredDrink = drink

            if len(self.venue.line) < self.venue.maxLine:
                self.venue.line.append(cust)
            else:
                lost_queue += 1

        # 2. Serve customers + track drinks served
        # process_turn MUST return: served_count, lost_stock, lost_patience, drinks_list
        served_count, lost_stock, lost_patience, drinks_served_list = process_turn(self)

        return served_count, lost_queue, lost_stock, lost_patience, drinks_served_list
    
    # -------------------------------------------------------
    # Multi-Day Simulator (console / backend use)
    # -------------------------------------------------------
    def run_days(self, num_days=3, turns=60):
        total_profit = 0
        total_revenue = 0
        opening_cash = self.cash

        for _ in range(num_days):
            print(f"\n=== Day {self.day} ===")
            start_cash = self.cash

            served_total = 0
            lost_queue = 0
            lost_stock = 0
            lost_pat = 0

            for _ in range(turns):
                served, lostQ, lostS, lostP = self.single_turn()
                served_total += served
                lost_queue += lostQ
                lost_stock += lostS
                lost_pat += lostP

            # --- End of Day ---
            wages = sum(e.wage for e in self.employees)
            rent = self.venue.rent

            revenue_this_day = self.cash - start_cash
            profit = revenue_this_day - wages - rent

            # Deduct expenses
            self.cash -= wages + rent

            total_profit += profit
            total_revenue += max(revenue_this_day, 0)

            print(f"Day {self.day} Summary")
            print(f"  Revenue        : ${revenue_this_day:.2f}")
            print(f"  Wages          : -${wages:.2f}")
            print(f"  Rent           : -${rent:.2f}")
            print(f"  Profit         : ${profit:.2f}")
            print(f"  Served         : {served_total}")
            print(f"  Lost (queue)   : {lost_queue}")
            print(f"  Lost (stock)   : {lost_stock}")
            print(f"  Lost (patience): {lost_pat}")
            print(f"  Cash end       : ${self.cash:.2f}")

            self.day += 1

        print("\n=== Summary ===")
        print(f"Opening Cash : ${opening_cash:.2f}")
        print(f"Closing Cash : ${self.cash:.2f}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Total Profit : ${total_profit:.2f}")