from ..models.ingredient import Ingredient
from game.models.staff import Staff

# name, unit_cost, shelf_life(days), addedDesirability

# milk
WHOLE_MILK      = Ingredient("Whole Milk",      0.15, 5, 0.10)
SKIM_MILK       = Ingredient("Skim Milk",       0.14, 5, 0.08)
OAT_MILK        = Ingredient("Oat Milk",        0.22, 5, 0.12)
ALMOND_MILK     = Ingredient("Almond Milk",     0.25, 5, 0.13)
SOY_MILK        = Ingredient("Soy Milk",        0.18, 5, 0.09)

# tea
BLACK_TEA       = Ingredient("Black Tea",       0.10, 365, 0.05)
GREEN_TEA       = Ingredient("Green Tea",       0.11, 365, 0.06)
OOLONG_TEA      = Ingredient("Oolong Tea",      0.13, 365, 0.07)
FRUIT_TEA       = Ingredient("Fruit Tea",       0.12, 365, 0.08)
EARL_GREY_TEA   = Ingredient("Earl Grey Tea",   0.14, 365, 0.07)

# sugar
CANE_SUGAR      = Ingredient("Cane Sugar",      0.03, 365, 0.07)
REFINED_SUGAR   = Ingredient("Refined Sugar",   0.02, 365, 0.05)
BROWN_SUGAR     = Ingredient("Brown Sugar",     0.04, 365, 0.09)
HONEY           = Ingredient("Honey",           0.08, 90,  0.12)
AGAVE_SYRUP     = Ingredient("Agave Syrup",     0.09, 180, 0.10)

# topping
BOBA_PEARLS     = Ingredient("Boba Pearls",     0.10, 7,   0.10)
GOLDEN_BOBA     = Ingredient("Golden Boba",     0.12, 7,   0.12)
CRYSTAL_BOBA    = Ingredient("Crystal Boba",    0.11, 7,   0.11)

STRAWBERRY      = Ingredient("Strawberry",      0.25, 2,   0.20)
MANGO           = Ingredient("Mango",           0.28, 2,   0.22)
LYCHEE          = Ingredient("Lychee",          0.30, 2,   0.25)

GRASS_JELLY     = Ingredient("Grass Jelly",     0.16, 10,  0.10)
COCONUT_JELLY   = Ingredient("Coconut Jelly",   0.18, 10,  0.11)
ALOEVERA        = Ingredient("Aloe Vera",       0.20, 10,  0.12)

# toppers
CHEESE_FOAM     = Ingredient("Cheese Foam",     0.30, 3,   0.30)
WHIPPED_CREAM   = Ingredient("Whipped Cream",   0.18, 3,   0.15)
MATCHA_POWDER   = Ingredient("Matcha Powder",   0.22, 365, 0.20)
TARO_POWDER     = Ingredient("Taro Powder",     0.20, 365, 0.18)
CHOCOLATE_POWDER= Ingredient("Chocolate Powder",0.19, 365, 0.15)

# ice
ICE_CUBES       = Ingredient("Ice Cubes",       0.01, 1,   0.00)

# container
CUP_REGULAR     = Ingredient("Cup (Regular)",   0.05, 9999, 0)
CUP_TALL        = Ingredient("Cup (Tall)",      0.07, 9999, 0)
CUP_JUMBO       = Ingredient("Cup (Jumbo)",     0.10, 9999, 0)

STRAW           = Ingredient("Straw",           0.01, 9999, 0)
SEAL            = Ingredient("Seal",            0.012, 9999, 0)
DOME_LID        = Ingredient("Dome Lid",        0.015, 9999, 0)


INGREDIENTS = [
    WHOLE_MILK, SKIM_MILK, OAT_MILK, ALMOND_MILK, SOY_MILK,
    BLACK_TEA, GREEN_TEA, OOLONG_TEA, FRUIT_TEA, EARL_GREY_TEA,
    CANE_SUGAR, REFINED_SUGAR, BROWN_SUGAR, HONEY, AGAVE_SYRUP,
    BOBA_PEARLS, GOLDEN_BOBA, CRYSTAL_BOBA,
    STRAWBERRY, MANGO, LYCHEE,
    GRASS_JELLY, COCONUT_JELLY, ALOEVERA,
    CHEESE_FOAM, WHIPPED_CREAM, MATCHA_POWDER, TARO_POWDER, CHOCOLATE_POWDER,
    ICE_CUBES,
    CUP_REGULAR, CUP_TALL, CUP_JUMBO, STRAW, SEAL, DOME_LID
]

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