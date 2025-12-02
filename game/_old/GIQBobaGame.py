import random
import math
from models.Employee import Employee

# --- Staff subclass with charm trait ---
class Staff(Employee):
    """Extended Employee with a charm trait (0‑3 scale)."""
    def __init__(self, name, wage, capacity, charm):
        super().__init__(name, wage, capacity)
        self.charm = charm  # 0,1,2,3

    def __str__(self):
        return f"{self.name} (capacity {self.capacity}, charm {self.charm}, wage ${self.wage})"
from collections import deque
from game.config import (
    STARTING_CASH,
    WAGE_MULTIPLIER,
    MAX_AD_BUDGET,
    CLEAR_DIVIDER,
    MAX_QUEUE_DISPLAY,
    MINUTES_PER_TURN,
    TURNS_PER_DAY,
)

def poisson(lam: float) -> int:
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

class Ingredient:
    def __init__(self, name, unit_cost, shelf_life, addedDesirability):
        self.name = name 
        self.unit_cost = unit_cost 
        self.shelf_life = shelf_life 
        self.addedDesirability = addedDesirability
        
class Drink:
    def __init__(
        self,
        name,
        recipe: dict['Ingredient', int],
        basePrice,
        baseDesirability,
        size="regular"  # "regular" or "tall"
    ):
        self.name = name
        self.recipe = recipe
        self.basePrice = basePrice
        self.size = size
        # Inject mandatory packaging units
        cup_item = CUP_TALL if self.size == "tall" else CUP_REGULAR
        recipe[cup_item] = recipe.get(cup_item, 0) + 1
        recipe[STRAW]    = recipe.get(STRAW, 0) + 1
        recipe[SEAL]     = recipe.get(SEAL, 0)  + 1
        self.desirability = baseDesirability
        for ing, qty in recipe.items():
            self.desirability += ing.addedDesirability * qty
        if self.size == "tall":
            self.desirability += 0.30   # premium for large size
    def setPrice(self,price):
        self.basePrice = price


class Venue:
    def __init__(self, name, maxLine, footTraffic, rent, basePatience):
        self.name = name
        self.maxLine = maxLine
        self.footTraffic = footTraffic
        self.rent = rent
        self.basePatience = basePatience
        self.line = deque()
        self.drinks = []
        self.ingredients = []

class Stand(Venue):
    def __init__(self, name="Boba Stand", maxLine=5, footTraffic=2, rent=20, basePatience=3):
        super().__init__(name, maxLine, footTraffic, rent, basePatience)

class Truck(Venue):
    def __init__(self):
        super().__init__("Boba Truck", maxLine=12, footTraffic=4, rent=40, basePatience=4)

class Store(Venue):
    def __init__(self):
        super().__init__("Boba Store", maxLine=30, footTraffic=8, rent=80, basePatience=5)

# === Base Ingredients ===
# === Base Ingredients ===
BOBA_PEARLS = Ingredient("Boba Pearls", 0.10, 7, 0.1)
CANE_SUGAR   = Ingredient("Cane Sugar", 0.03, 365, 0.07)
MILK         = Ingredient("Milk", 0.15, 5, 0.1)
STRAWBERRY   = Ingredient("Strawberry", 0.25, 2, 0.2)
# --- New ingredients ---
REFINED_SUGAR = Ingredient("Refined Sugar", 0.02, 365, 0.05)
LYCHEE        = Ingredient("Lychee",        0.30,   2, 0.25)
FRUIT_TEA     = Ingredient("Fruit Tea",     0.12, 365, 0.08)
# Packaging (non‑perishable, shelf_life set very high)
CUP_REGULAR = Ingredient("Cup (Regular)", 0.05, 9999, 0.0)
CUP_TALL    = Ingredient("Cup (Tall)",    0.07, 9999, 0.0)
STRAW       = Ingredient("Straw",         0.01, 9999, 0.0)
SEAL        = Ingredient("Seal",          0.012, 9999, 0.0)

class Customer:
    def __init__(self, basePatience, max_afford=None):
        # How long the customer will wait in turns
        self.patience = basePatience
        self.desiredDrink = None
        # Maximum price the customer is willing to pay
        if max_afford is None:
            # Base range 4–8 dollars plus a small random wiggle
            self.maxAfford = round(random.uniform(4.0, 8.0) + random.uniform(-1.0, 1.0), 2)
        else:
            self.maxAfford = max_afford
        
        
# --- Game class ---
class Game:
    def __init__(self):
        # Starting resources
        self.cash = STARTING_CASH
        self.day = 1
        self.ingredients = [
            BOBA_PEARLS, CANE_SUGAR, REFINED_SUGAR,
            MILK, STRAWBERRY, LYCHEE, FRUIT_TEA,
            CUP_REGULAR, CUP_TALL, STRAW, SEAL
        ]
        # --- Core game state ---
        # Default menu with classic drink
        classic_recipe = {
            BOBA_PEARLS: 1,
            CANE_SUGAR:  1,
            MILK:        1,
        }
        self.menu = [
            Drink(
                "Classic Milk Tea",
                classic_recipe,
                basePrice=4.50,
                baseDesirability=5,
                size="regular"
            )
        ]

        # Employees and venue
        self.employees = [Staff("Owner", 0, 1, charm=1)]
        self.venue = Stand()

        # Start with more generous inventory: 100 packaging units, 50 of each ingredient
        self.stock = {ing: (100 if ing in {CUP_REGULAR, CUP_TALL, STRAW, SEAL} else 50)
                      for ing in self.ingredients}
        self.fresh_left = {ing: ing.shelf_life for ing in self.ingredients}

        # Advertising and daily trackers
        self.adBudget = 0
        self.adFactor = 0
        self.dailyIngredientCost = 0
        self.dailyAdSpend = 0
    # -------- Edit‑drink helper --------
    def editDrink(self):
        """Allow player to change the base price of an existing drink."""
        if not self.menu:
            return
        print("\n-- Current Menu --")
        for idx, d in enumerate(self.menu, 1):
            print(f" {idx}) {d.name} (${d.basePrice:.2f}) [{d.size}]")
        choice = input("Edit a drink price? (enter number or blank to skip): ").strip()
        if not choice:
            return
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.menu):
                print(" Invalid selection.")
                return
        except ValueError:
            print(" Invalid input.")
            return
        drink = self.menu[idx]
        try:
            new_price = float(input(f" New price for {drink.name} (current ${drink.basePrice:.2f}): "))
            if new_price < 0:
                print(" Price must be non‑negative.")
                return
        except ValueError:
            print(" Invalid price.")
            return
        drink.setPrice(new_price)
        print(f" Updated {drink.name} price to ${new_price:.2f}")
    def generate_offers(self):
        """Create bulk & retail offers for every ingredient for this morning."""
        offers = {}
        for ing in self.ingredients:
            base = ing.unit_cost
            offers[ing] = {
                "bulk":   {"min": 200,
                           "unit": round(base * random.uniform(0.7, 0.85), 3)},
                "retail": {"min": 1,
                           "unit": round(base * random.uniform(1.05, 1.20), 3)}
            }
        self.offers = offers
    def generateArrivals(self, venue, multiplier=0.0):
        """
        Return the number of new customers this turn based on a Poisson
        distribution with mean `venue.footTraffic * (1 + multiplier)`.
        """
        lam = venue.footTraffic * (1 + multiplier)
        return poisson(lam) if lam > 0 else 0

    def pickDrink(self, customer):
        """
        Choose a drink for the customer based on desirability weights *and*
        the customer's maxAfford. Returns a Drink or None if nothing is affordable.
        """
        affordable_drinks = [d for d in self.menu if d.basePrice <= customer.maxAfford]
        if not affordable_drinks:
            return None  

        total_charm = sum(getattr(e, "charm", 0) for e in self.employees)
        weights = [d.desirability * (1 + 0.05 * total_charm) for d in affordable_drinks]
        chosen_drink = random.choices(affordable_drinks, weights=weights, k=1)[0]
        return chosen_drink
    # -------- Drink‑creation helper --------
    def createDrink(self):
        """Interactively build a new drink and add it to the menu."""
        add_new = input("Add a new drink to the menu? (y/n): ").strip().lower()
        if add_new != "y":
            return

        name = input("  Drink name: ").strip()
        if not name:
            print("  Name cannot be blank.")
            return

        try:
            base_price = float(input("  Base price ($): "))
            if base_price < 0:
                print("  Price must be non‑negative.")
                return
        except ValueError:
            print("  Invalid price.")
            return

        size_entry = input("  Size (r = regular / t = tall) [r]: ").strip().lower()
        size_flag = "tall" if size_entry == "t" else "regular"

        # Choose ingredients
        print("  Enter ingredients as 'id qty' (blank line to finish):")
        for idx, ing in enumerate(self.ingredients, 1):
            print(f"   {idx}) {ing.name} (${ing.unit_cost})")

        recipe: dict[Ingredient, int] = {}
        while True:
            line = input("   > ").strip()
            if not line:
                break
            try:
                idx, qty = map(int, line.split())
                if idx < 1 or idx > len(self.ingredients):
                    print("   Invalid ID.")
                    continue
                if qty <= 0:
                    print("   Qty must be positive.")
                    continue
                ing = self.ingredients[idx - 1]
                recipe[ing] = recipe.get(ing, 0) + qty
            except (ValueError, IndexError):
                print("   Bad input—use two ints corresponding to list above.")

        if not recipe:
            print("  No ingredients added—drink discarded.")
            return

        self.menu.append(Drink(name, recipe, base_price, baseDesirability=5, size=size_flag))
        print(f"  Added new drink: {name} (${base_price}) with {len(recipe)} ingredients.")
    # -------- Hiring helper --------
    def hireEmployees(self):
        """Interactive loop to hire as many employees as the player wants."""
        wage_multiplier = WAGE_MULTIPLIER  # Base wage per capacity
        hire_again = "y"

        while hire_again.lower() == "y":
            # Fresh pool each round
            candidates = []
            first_names = ["Alex", "Jordan", "Casey", "Riley", "Taylor",
                           "Morgan", "Jamie", "Avery", "Sam", "Devon"]
            for _ in range(3):
                capacity = random.randint(1, 3)
                charm = random.randint(0, 3)
                wage_variation = random.randint(-5, 5)
                wage = capacity * wage_multiplier + charm * 3 + wage_variation
                candidates.append(Staff(random.choice(first_names), wage, capacity, charm))

            print("\n-- Available Applicants --")
            for idx, cand in enumerate(candidates, start=1):
                print(f"{idx}) {cand.name} (capacity {cand.capacity}, charm {cand.charm}, wage ${cand.wage})")
            print("0) Finish hiring")

            choice = input("Choose employee to hire (0 to stop): ")
            while choice not in {"0", "1", "2", "3"}:
                choice = input("Enter 0, 1, 2, or 3: ")

            if choice == "0":
                break

            selected = candidates[int(choice) - 1]
            self.employees.append(selected)
            print(f"Hired: {selected.name} (capacity {selected.capacity}, charm {selected.charm}, wage ${selected.wage})")

            hire_again = input("Hire another employee? (y/n): ")

    def morningMenu(self):
        print("\n=== Morning Planning Phase ===")
        self.generate_offers()
        # Venue upgrade prompt removed for GUI integration.
        self.hireEmployees()  # <-- call the new helper
        # --- Firing employees ---
        if self.employees:
            print("\nCurrent staff:")
            for idx, emp in enumerate(self.employees, 1):
                print(f"  {idx}) {emp}")
            fire_prompt = input("Fire an employee? (enter number or blank to keep all): ").strip()
            if fire_prompt:
                try:
                    fire_idx = int(fire_prompt) - 1
                    if 0 <= fire_idx < len(self.employees):
                        fired = self.employees.pop(fire_idx)
                        print(f"Fired: {fired}")
                    else:
                        print("Invalid index—no one fired.")
                except ValueError:
                    print("Invalid input—no one fired.")
        self.createDrink()
        self.editDrink()
        print("\n— Ingredient purchasing —")
        print("ID | Ingredient | On-hand | Unit Cost")
        for idx, ing in enumerate(self.ingredients, 1):
            print(f"{idx:2} | {ing.name:12} | {self.stock[ing]:3} | ${ing.unit_cost:.2f}")

        print("Enter the ID of the item you want to buy (blank to finish):")
        while True:
            line = input("ID> ").strip()
            if not line:
                break
            try:
                idx = int(line)
                if idx < 1 or idx > len(self.ingredients):
                    print("  Invalid ID.")
                    continue
                ing = self.ingredients[idx - 1]
            except (ValueError, IndexError):
                print("  Invalid ID.")
                continue

            offer = self.offers[ing]
            bulk_min   = offer["bulk"]["min"]
            bulk_price = offer["bulk"]["unit"]
            retail_price = offer["retail"]["unit"]

            bundle_small = bulk_min // 4  # e.g., 50 if bulk_min is 200
            bundle_large = bulk_min        # e.g., 200
            cost_small  = round(bundle_small * retail_price, 2)
            cost_large  = round(bundle_large * bulk_price,   2)

            print(f"  Selected: {ing.name}")
            print(f"   (1) Vendor 1 : {bundle_small} units  – Total ${cost_small:.2f}")
            print(f"   (2) Vendor 2 : {bundle_large} units – Total ${cost_large:.2f}")
            tier = input("   Choose vendor (1/2, blank to cancel): ").strip()
            if tier not in {'1','2'}:
                print("   Cancelled.")
                continue

            bundle_qty  = bundle_large if tier == '2' else bundle_small
            bundle_cost = cost_large  if tier == '2' else cost_small
            if bundle_cost > self.cash:
                print(f"   Not enough cash. You have ${self.cash:.2f}.")
                continue

            # Deduct cash and add stock
            self.cash -= bundle_cost
            self.dailyIngredientCost += bundle_cost
            self.stock[ing] += bundle_qty
            if ing.shelf_life < 9999:
                self.fresh_left[ing] = ing.shelf_life
            print(f"   Bought {bundle_qty} x {ing.name} for ${bundle_cost:.2f}")
        # --- Advertising budget ---
        while True:
            print(f"\nAdvertising budget (current setting: ${self.adBudget:.2f})")
            print("Enter new amount for TODAY (blank = $0):")
            entry = input("> ").strip()
            if entry == "":
                # No ads today
                self.dailyAdSpend = 0
                break
            try:
                amount = float(entry)
                if amount < 0:
                    raise ValueError
                if amount > self.cash:
                    print(f"Not enough cash. You have ${self.cash:.2f} available.")
                    continue
                if amount > MAX_AD_BUDGET:
                    print(f"Capped to maximum daily budget of ${MAX_AD_BUDGET}.")
                    amount = MAX_AD_BUDGET
                self.dailyAdSpend = amount
                self.cash -= amount
                break
            except ValueError:
                print("Please enter a non‑negative number.")

        # Update the ad factor based on today's spend
        self.adBudget = self.dailyAdSpend     # store today's spend
        self.adFactor = self.calculateAdFactor()

        # --- Packaging sufficiency check ---
        expected_customers = int(self.venue.footTraffic * (1 + self.adFactor) * TURNS_PER_DAY)
        total_cups = self.stock.get(CUP_REGULAR, 0) + self.stock.get(CUP_TALL, 0)
        if total_cups < expected_customers:
            print(f"Warning: You have {total_cups} cups but could see ~{expected_customers} customers today.")
            print("    Consider buying more packaging.")

        if self.cash < 0:
            print(f"\nYou have negative cash (${self.cash:.2f}) after morning expenses.")
            print("Reduce ad spend or refund ingredient purchases.")
            self.morningMenu()  # restart planning phase
    def calculateAdFactor(self):
        return self.adBudget / 100

    # ---------- one‑turn simulation ----------
    def single_turn(self):
        """
        Simulate ONE 15‑minute turn. Returns tuple (served, lostQ, lostStock, lostPat).
        Designed for the GUI so it can tick in real time without blocking.
        """
        served = lostQ = lostStock = lostPat = 0

        arrive = self.generateArrivals(self.venue, self.adFactor)
        for _ in range(arrive):
            cust = Customer(self.venue.basePatience)
            drink = self.pickDrink(cust)
            if drink is None:
                continue
            cust.desiredDrink = drink
            if len(self.venue.line) < self.venue.maxLine:
                self.venue.line.append(cust)
            else:
                lostQ += 1

        capacity = sum(e.capacity for e in self.employees)
        for _ in range(min(capacity, len(self.venue.line))):
            cust = self.venue.line.popleft()
            if not all(self.stock.get(ing, 0) >= qty for ing, qty in cust.desiredDrink.recipe.items()):
                lostStock += 1
                continue
            for ing, qty in cust.desiredDrink.recipe.items():
                self.stock[ing] -= qty
            self.cash += cust.desiredDrink.basePrice
            served += 1

        # patience tick
        new_queue = deque()
        for cust in self.venue.line:
            cust.patience -= 1
            if cust.patience > 0:
                new_queue.append(cust)
            else:
                lostPat += 1
        self.venue.line = new_queue
        return served, lostQ, lostStock, lostPat
    def display_turn(self, turn_idx: int):
        """Simple per‑turn console UI showing queue length and cash."""
        # Updated clock: each turn is 15 minutes
        minutes_since_open = turn_idx * 15  # each turn represents 15 minutes
        hour   = 8 + minutes_since_open // 60
        minute = minutes_since_open % 60
        clock  = f"{hour:02d}:{minute:02d}"
        q_len = len(self.venue.line)
        bar_len = min(self.venue.maxLine, MAX_QUEUE_DISPLAY)
        filled  = "#" * min(q_len, bar_len)
        empty   = "-" * (bar_len - len(filled))
        bar = filled + empty
        print(f"{clock} | Turn {turn_idx+1:02d} | Queue [{bar}] {q_len}/{self.venue.maxLine} | Cash ${self.cash:.2f}")
    def start_day(self, turns):
        """Placeholder for the daily simulation loop."""
        self.morningMenu()
        # Reset daily cost trackers
        self.dailyIngredientCost = 0
        self.dailyAdSpend = 0
        opening_cash = self.cash
        served = lostStock = 0
        revenue = 0 
        lostQueue = 0 
        lostPatience = 0 
        # Removed unused TURN_DELAY code
        for turn_idx in range(turns):
            arrive = self.generateArrivals(self.venue, self.adFactor)
            for j in range(arrive):
                customer = Customer(self.venue.basePatience) #make it random
                drink = self.pickDrink(customer)
                if drink is None:
                    continue 
                customer.desiredDrink = drink
                if len(self.venue.line) < self.venue.maxLine:
                    self.venue.line.append(customer)
                else: 
                    lostQueue += 1
            capacity = 0
            for employee in self.employees:
                capacity += employee.capacity
            for _ in range(min(capacity, len(self.venue.line))):
                cust = self.venue.line.popleft()

                # Check if we have enough inventory for this drink
                canMake = True
                for ing, qty in cust.desiredDrink.recipe.items():
                    if self.stock.get(ing, 0) < qty:
                        canMake = False
                        break

                if not canMake:
                    # Try to repick another affordable & in‑stock drink
                    alt_menu = [d for d in self.menu
                                if d.basePrice <= cust.maxAfford
                                and all(self.stock.get(ing, 0) >= qty for ing, qty in d.recipe.items())]
                    if alt_menu:
                        cust.desiredDrink = random.choices(
                            alt_menu,
                            weights=[d.desirability for d in alt_menu],
                            k=1
                        )[0]
                        # re‑evaluate ingredients after swap
                        for ing, qty in cust.desiredDrink.recipe.items():
                            self.stock[ing] -= qty
                        self.cash += cust.desiredDrink.basePrice
                        revenue += cust.desiredDrink.basePrice
                        served  += 1
                    else:
                        lostStock += 1
                    continue

                # Deduct inventory now that we know we can make it
                for ing, qty in cust.desiredDrink.recipe.items():
                    self.stock[ing] -= qty

                # Collect revenue
                self.cash += cust.desiredDrink.basePrice
                revenue += cust.desiredDrink.basePrice
                served += 1
            # ---- End of actions for this turn; show status once ----
            self.display_turn(turn_idx)
            # time.sleep(TURN_DELAY)
            # No delay; instant turn advance
            new_queue = deque()
            for customer in self.venue.line:
                customer.patience -= 1
                if customer.patience > 0:
                    new_queue.append(customer)
                else:
                    lostPatience += 1
            self.venue.line = new_queue
        # ---- Financial summary ----
        wagesCost = sum(emp.wage for emp in self.employees)
        rentCost  = self.venue.rent
        profitDay = revenue - wagesCost - rentCost - self.dailyIngredientCost - self.dailyAdSpend
        print(CLEAR_DIVIDER)
        print(f"Opening Cash: ${opening_cash:.2f}")
        print(f"Revenue     : ${revenue:.2f}")
        print(f"Wages       : -${wagesCost:.2f}")
        print(f"Rent        : -${rentCost:.2f}")
        print(f"Ingredients : -${self.dailyIngredientCost:.2f}")
        print(f"Ads         : -${self.dailyAdSpend:.2f}")
        print(f"Profit      : ${profitDay:.2f}")
        print(f"Served: {served}, Lost (queue): {lostQueue}, Lost (stock): {lostStock}, Lost (patience): {lostPatience}, Cash: ${self.cash:.2f}")
        print("Stock levels:")
        for ing in self.ingredients: 
            print(f" {ing.name:12}: {self.stock[ing]}")
        for employee in self.employees: 
            self.cash -= employee.wage
        self.cash -= self.venue.rent
        if self.cash < 0:
            print("BANKRUPT! Game over.")
            exit()
        # Spoilage step: decrement freshness and discard expired
        for ing in self.ingredients:
            if ing.shelf_life < 9999:
                self.fresh_left[ing] -= 1
                if self.fresh_left[ing] <= 0:
                    self.stock[ing] = 0
                    self.fresh_left[ing] = 0
                    print(f" Spoiled: all remaining {ing.name} discarded.")
        return served, lostQueue, lostPatience

    def run_days(self, num_days=3, turns=TURNS_PER_DAY):
        """
        Run multiple consecutive days. After the final day, print a cumulative report.
        """
        total_profit = total_revenue = total_served = total_lostQ = total_lostStock = total_lostPat = 0
        opening_bank = self.cash

        for _ in range(num_days):
            print("\n" + CLEAR_DIVIDER)
            print(f"=== Day {self.day} ===")
            start_cash = self.cash
            served, lostQ, lostPat = self.start_day(turns)
            # Profit = change in cash during day
            day_profit = self.cash - start_cash
            # Estimate revenue as profit + known costs (already tracked inside start_day)
            day_revenue = max(day_profit + self.dailyIngredientCost + self.dailyAdSpend
                              + sum(emp.wage for emp in self.employees) + self.venue.rent, 0)

            total_profit  += day_profit
            total_revenue += day_revenue
            total_served  += served
            total_lostQ   += lostQ
            total_lostPat += lostPat

            self.day += 1

        print("\n" + CLEAR_DIVIDER)
        print(f"=== {num_days}-Day Summary ===")
        print(f"Opening Cash : ${opening_bank:.2f}")
        print(f"Closing Cash : ${self.cash:.2f}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Total Profit : ${total_profit:.2f}")
        print(f"Drinks Served: {total_served}")
        print(f"Lost (queue) : {total_lostQ}")
        print(f"Lost (patience): {total_lostPat}")
    # --- Quick test helper ---
    @staticmethod
    def run_simple_test(days: int = 3, turns: int = 60):
        """
        Create a Game instance and run one simulated day.
        """
        g = Game()
        print("Running multi‑day test...")
        g.run_days(days, turns)
    

# --- Quick per‑turn UI demo ---
def demo_turn_ui(turns: int = TURNS_PER_DAY):
    """
    Spin up a fresh game and run a single day with a limited number
    of turns so you can get a feel for the per‑turn queue display.
    """
    g = Game()
    print("\n" + CLEAR_DIVIDER)
    print("=== Per‑Turn UI Demo ===")
    g.start_day(turns)


if __name__ == "__main__":
    demo_turn_ui(TURNS_PER_DAY)
