from ..models.ingredient import Ingredient
from game.models.staff import Staff
from game.models.loan import LoanOption
# name, unit_cost, shelf_life(days), addedDesirability
# Ingredient Categories
CAT_MILK       = "Milk"
CAT_TEA        = "Tea Base"
CAT_FRUIT      = "Fruit"
CAT_SWEETENER  = "Sweetener"
CAT_TOPPING    = "Topping"
CAT_POWDER     = "Powder"
CAT_CREAM      = "Cream / Foam"
CAT_ICE        = "Ice"
CAT_CONTAINER  = "Container"

# milk
WHOLE_MILK  = Ingredient("Whole Milk", 0.15, 5, 0.10, CAT_MILK)
SKIM_MILK   = Ingredient("Skim Milk",  0.14, 5, 0.08, CAT_MILK)
OAT_MILK    = Ingredient("Oat Milk",   0.22, 5, 0.12, CAT_MILK)
ALMOND_MILK = Ingredient("Almond Milk",0.25, 5, 0.13, CAT_MILK)
SOY_MILK    = Ingredient("Soy Milk",   0.18, 5, 0.09, CAT_MILK)

# tea
BLACK_TEA     = Ingredient("Black Tea",    0.10, 365, 0.05, CAT_TEA)
GREEN_TEA     = Ingredient("Green Tea",    0.11, 365, 0.06, CAT_TEA)
OOLONG_TEA    = Ingredient("Oolong Tea",   0.13, 365, 0.07, CAT_TEA)
FRUIT_TEA     = Ingredient("Fruit Tea",    0.12, 365, 0.08, CAT_TEA)
EARL_GREY_TEA = Ingredient("Earl Grey Tea",0.14, 365, 0.07, CAT_TEA)

# fruit
STRAWBERRY_FRUIT = Ingredient("Strawberry (Fresh)", 0.30, 3, 0.22, CAT_FRUIT)
MANGO_FRUIT      = Ingredient("Mango (Fresh)",      0.32, 3, 0.24, CAT_FRUIT)
AVACADO_FRUIT     = Ingredient("Avacato",           0.35, 3, 0.26, CAT_FRUIT)
PASSION_FRUIT    = Ingredient("Passion Fruit",      0.38, 3, 0.28, CAT_FRUIT)
PEACH_FRUIT      = Ingredient("Peach",              0.29, 3, 0.21, CAT_FRUIT)
PINEAPPLE_FRUIT  = Ingredient("Pineapple",          0.27, 3, 0.20, CAT_FRUIT)
KIWI_FRUIT       = Ingredient("Kiwi",               0.31, 3, 0.23, CAT_FRUIT)
BLUEBERRY_FRUIT  = Ingredient("Blueberry",          0.34, 3, 0.25, CAT_FRUIT)
ORANGE_FRUIT     = Ingredient("Orange",             0.26, 3, 0.18, CAT_FRUIT)
GRAPE_FRUIT      = Ingredient("Grape",              0.28, 3, 0.19, CAT_FRUIT)

# sugar
CANE_SUGAR    = Ingredient("Cane Sugar",    0.03, 365, 0.07, CAT_SWEETENER)
REFINED_SUGAR = Ingredient("Refined Sugar", 0.02, 365, 0.05, CAT_SWEETENER)
BROWN_SUGAR   = Ingredient("Brown Sugar",   0.04, 365, 0.09, CAT_SWEETENER)
HONEY         = Ingredient("Honey",         0.08, 90,  0.12, CAT_SWEETENER)
AGAVE_SYRUP   = Ingredient("Agave Syrup",   0.09, 180, 0.10, CAT_SWEETENER)

# topping
BOBA_PEARLS  = Ingredient("Boba Pearls",  0.10, 7, 0.10, CAT_TOPPING)
GOLDEN_BOBA  = Ingredient("Golden Boba",  0.12, 7, 0.12, CAT_TOPPING)
CRYSTAL_BOBA = Ingredient("Crystal Boba", 0.11, 7, 0.11, CAT_TOPPING)

STRAWBERRY   = Ingredient("Strawberry", 0.25, 2, 0.20, CAT_TOPPING)
MANGO        = Ingredient("Mango",      0.28, 2, 0.22, CAT_TOPPING)
LYCHEE       = Ingredient("Lychee",     0.30, 2, 0.25, CAT_TOPPING)

GRASS_JELLY   = Ingredient("Grass Jelly",   0.16, 10, 0.10, CAT_TOPPING)
COCONUT_JELLY = Ingredient("Coconut Jelly", 0.18, 10, 0.11, CAT_TOPPING)
ALOEVERA      = Ingredient("Aloe Vera",     0.20, 10, 0.12, CAT_TOPPING)

# toppers
CHEESE_FOAM      = Ingredient("Cheese Foam",      0.30, 3,   0.30, CAT_CREAM)
WHIPPED_CREAM    = Ingredient("Whipped Cream",    0.18, 3,   0.15, CAT_CREAM)

MATCHA_POWDER    = Ingredient("Matcha Powder",    0.22, 365, 0.20, CAT_POWDER)
TARO_POWDER      = Ingredient("Taro Powder",      0.20, 365, 0.18, CAT_POWDER)
CHOCOLATE_POWDER = Ingredient("Chocolate Powder", 0.19, 365, 0.15, CAT_POWDER)

# ice
ICE_CUBES = Ingredient("Ice Cubes", 0.01, 1, 0.00, CAT_ICE)

# container
CUP_REGULAR = Ingredient("Cup (Regular)", 0.05, 9999, 0, CAT_CONTAINER)
CUP_TALL    = Ingredient("Cup (Tall)",    0.07, 9999, 0, CAT_CONTAINER)
CUP_JUMBO   = Ingredient("Cup (Jumbo)",   0.10, 9999, 0, CAT_CONTAINER)

STRAW       = Ingredient("Straw",    0.01,  9999, 0, CAT_CONTAINER)
SEAL        = Ingredient("Seal",     0.012, 9999, 0, CAT_CONTAINER)
DOME_LID    = Ingredient("Dome Lid", 0.015, 9999, 0, CAT_CONTAINER)


INGREDIENTS = [
    WHOLE_MILK, SKIM_MILK, OAT_MILK, ALMOND_MILK, SOY_MILK,
    BLACK_TEA, GREEN_TEA, OOLONG_TEA, FRUIT_TEA, EARL_GREY_TEA,
    STRAWBERRY_FRUIT, MANGO_FRUIT, AVACADO_FRUIT,
    PASSION_FRUIT, PEACH_FRUIT, PINEAPPLE_FRUIT,
    KIWI_FRUIT, BLUEBERRY_FRUIT, ORANGE_FRUIT, GRAPE_FRUIT,
    CANE_SUGAR, REFINED_SUGAR, BROWN_SUGAR, HONEY, AGAVE_SYRUP,
    BOBA_PEARLS, GOLDEN_BOBA, CRYSTAL_BOBA,
    STRAWBERRY, MANGO, LYCHEE,
    GRASS_JELLY, COCONUT_JELLY, ALOEVERA,
    CHEESE_FOAM, WHIPPED_CREAM, MATCHA_POWDER, TARO_POWDER, CHOCOLATE_POWDER,
    ICE_CUBES,
    CUP_REGULAR, CUP_TALL, CUP_JUMBO, STRAW, SEAL, DOME_LID
]

INGREDIENTS_BY_CATEGORY = {
    CAT_MILK: [
        WHOLE_MILK, SKIM_MILK, OAT_MILK, ALMOND_MILK, SOY_MILK
    ],
    CAT_TEA: [
        BLACK_TEA, GREEN_TEA, OOLONG_TEA, FRUIT_TEA, EARL_GREY_TEA
    ],
    CAT_FRUIT: [
    STRAWBERRY_FRUIT, MANGO_FRUIT, AVACADO_FRUIT,
    PASSION_FRUIT, PEACH_FRUIT, PINEAPPLE_FRUIT,
    KIWI_FRUIT, BLUEBERRY_FRUIT, ORANGE_FRUIT, GRAPE_FRUIT
    ],
    CAT_SWEETENER: [
        CANE_SUGAR, REFINED_SUGAR, BROWN_SUGAR, HONEY, AGAVE_SYRUP
    ],
    CAT_TOPPING: [
        BOBA_PEARLS, GOLDEN_BOBA, CRYSTAL_BOBA,
        STRAWBERRY, MANGO, LYCHEE, GRASS_JELLY, COCONUT_JELLY, ALOEVERA
    ],
    CAT_CREAM: [
        CHEESE_FOAM, WHIPPED_CREAM
    ],
    CAT_POWDER: [
        MATCHA_POWDER, TARO_POWDER, CHOCOLATE_POWDER
    ],
    CAT_ICE: [
        ICE_CUBES
    ],
    CAT_CONTAINER: [
        CUP_REGULAR, CUP_TALL, CUP_JUMBO, STRAW, SEAL, DOME_LID
    ],
}

# CONSTANT EMPLOYEE POOL
EMPLOYEE_POOL = [
    Staff("Alex",     wage=18, capacity=2, charm=1, reliability=8),
    Staff("Jordan",   wage=22, capacity=3, charm=2, reliability=6),
    Staff("Casey",    wage=15, capacity=1, charm=3, reliability=9),
    Staff("Riley",    wage=20, capacity=2, charm=2, reliability=7),
    Staff("Taylor",   wage=25, capacity=3, charm=1, reliability=10),
    Staff("Morgan",   wage=17, capacity=2, charm=0, reliability=5),
    Staff("Jamie",    wage=14, capacity=1, charm=2, reliability=8),
    Staff("Avery",    wage=23, capacity=3, charm=3, reliability=4),
    Staff("Sam",      wage=16, capacity=2, charm=1, reliability=6),
    Staff("Devon",    wage=19, capacity=2, charm=3, reliability=9),
]

# LOAN OPTIONS (per turn)
LOAN_OPTIONS = [
    LoanOption("Starter Loan", amount=500, interest_rate=0.015, payback_rate=0.05),
    LoanOption("Small Business Loan", amount=1200, interest_rate=0.02, payback_rate=0.06),
    LoanOption("Expansion Loan", amount=3000, interest_rate=0.025, payback_rate=0.07),
    LoanOption("Growth Loan", amount=6000, interest_rate=0.03, payback_rate=0.08),
    LoanOption("High-Risk Investor Loan", amount=10000, interest_rate=0.04, payback_rate=0.10),
]