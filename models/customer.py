import random

class Customer:
    def __init__(self, basePatience, max_afford=None):
        self.patience = basePatience
        self.desiredDrink = None

        if max_afford is None:
            self.maxAfford = round(random.uniform(3, 9), 2)
        else:
            self.maxAfford = max_afford