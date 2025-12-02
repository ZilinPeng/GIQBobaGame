from collections import deque

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
    def __init__(self):
        super().__init__("Boba Stand", 5, 2, 20, 3)

class Truck(Venue):
    def __init__(self):
        super().__init__("Boba Truck", 12, 4, 40, 4)

class Store(Venue):
    def __init__(self):
        super().__init__("Boba Store", 30, 8, 80, 5)