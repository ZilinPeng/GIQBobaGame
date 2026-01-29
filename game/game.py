from game.config import *
from .models.venue import Stand, Truck, Store
from .models.drink import Drink
from .models.customer import Customer
from .utils.constants import *
from .systems.arrivals import generate_arrivals
from .systems.turn_engine import process_turn
from .systems.inventory import *
from .systems.hiring import generate_candidates
from .systems.advertising import calculate_ad_factor
from .models.staff import Staff
from game.models.loan import Loan
import random


class Game:
    def __init__(self):
        # --- Core Game State ---
        self.cash = STARTING_CASH
        self.day = 1
        self.venue = Stand()
        self.employees = [Staff("Owner", wage=0, capacity=1, charm=1, reliability=10)]

        # --- Loans ---
        self.loans: list[Loan] = []
        self.dailyLoanPayments = 0.0

        # --- Inventory ---
        self.ingredients = INGREDIENTS
        self.stock = {
            ing: (100 if ing in {CUP_REGULAR, CUP_TALL, STRAW, SEAL} else 50)
            for ing in self.ingredients
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

        total_charm = sum(e.charm for e in self.employees)
        weights = [d.desirability * (1 + 0.05 * total_charm) for d in affordable]
        return random.choices(affordable, weights=weights, k=1)[0]

    # -------------------------------------------------------
    # Loan Handling (PER TURN)
    # -------------------------------------------------------
    def process_loans_per_day(self):
        if not self.loans:
            return

        for loan in self.loans[:]:
            if loan.remaining_balance <= 0:
                self.loans.remove(loan)
                continue
            
            # Fixed principal payment
            principal_payment = loan.principal * loan.payback_rate
            principal_payment = min(principal_payment, loan.remaining_balance)
            print('principle',principal_payment)
            self.cash -= principal_payment
            self.dailyLoanPayments += principal_payment
            loan.remaining_balance -= principal_payment

            # Compound interest AFTER payment
            if loan.remaining_balance > 0:
                loan.remaining_balance *= (1 + loan.interest_rate)

            if loan.remaining_balance <= 0:
                self.loans.remove(loan)

    # -------------------------------------------------------
    # Single Turn Simulation
    # -------------------------------------------------------
    def single_turn(self):
        # 1. Customer arrivals
        arrivals = generate_arrivals(self.venue, self.adFactor)

        lost_queue = 0
        for _ in range(arrivals):
            cust = Customer(self.venue.basePatience)
            drink = self.pickDrink(cust)
            if not drink:
                continue

            cust.desiredDrink = drink

            if len(self.venue.line) < self.venue.maxLine:
                self.venue.line.append(cust)
            else:
                lost_queue += 1

        # 2. Serve customers
        served_count, lost_stock, lost_patience, drinks_served = process_turn(self)

        return served_count, lost_queue, lost_stock, lost_patience, drinks_served

    # -------------------------------------------------------
    # Venue Upgrade
    # -------------------------------------------------------
    def get_next_venue_upgrade(self):
        if isinstance(self.venue, Stand):
            return Truck(), 300
        elif isinstance(self.venue, Truck):
            return Store(), 800
        return None, None

    def upgrade_venue(self):
        next_venue, cost = self.get_next_venue_upgrade()
        if not next_venue:
            return False, "Already at max venue"
        if self.cash < cost:
            return False, "Not enough cash"

        self.cash -= cost
        self.venue = next_venue
        return True, f"Upgraded to {next_venue.name}"

    # -------------------------------------------------------
    # Loans API
    # -------------------------------------------------------
    def has_active_loan(self, option_name: str) -> bool:
        return any(l.name == option_name for l in self.loans)

    def take_loan(self, loan_option):
        if self.has_active_loan(loan_option.name):
            return False

        loan = Loan(loan_option)
        self.loans.append(loan)
        self.cash += loan.principal
        return True

    # -------------------------------------------------------
    # Day Transition (IMPORTANT)
    # -------------------------------------------------------
    def start_new_day(self):
        self.dailyLoanPayments = 0.0
        self.dailyIngredientCost = 0.0
        self.dailyAdSpend = 0.0