from models.ingredient import Ingredient

# name, unit_cost, shelf_life(days), addedDesirability

# liquids
MILK        = Ingredient("Milk", 0.15, 5, 0.1)
FRUIT_TEA     = Ingredient("Fruit Tea", 0.12, 365, 0.08)

# sugar
CANE_SUGAR  = Ingredient("Cane Sugar", 0.03, 365, 0.07)
REFINED_SUGAR = Ingredient("Refined Sugar", 0.02, 365, 0.05)

# topping
BOBA_PEARLS = Ingredient("Boba Pearls", 0.10, 7, 0.1)
STRAWBERRY  = Ingredient("Strawberry", 0.25, 2, 0.2)
LYCHEE        = Ingredient("Lychee", 0.30, 2, 0.25)

# container
CUP_REGULAR = Ingredient("Cup (Regular)", 0.05, 9999, 0)
CUP_TALL    = Ingredient("Cup (Tall)",    0.07, 9999, 0)
STRAW       = Ingredient("Straw",         0.01, 9999, 0)
SEAL        = Ingredient("Seal",          0.012, 9999, 0)