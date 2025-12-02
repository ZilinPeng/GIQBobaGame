import random
from models.Employee import Employee

class Staff(Employee):
    """Extended Employee with a charm trait (0-3 scale)."""
    def __init__(self, name, wage, capacity, charm, reliability):
        super().__init__(name, wage, capacity, reliability)
        self.charm = charm  # 0–3

    def __str__(self):
        return f"{self.name} (capacity {self.capacity}, charm {self.charm}, wage ${self.wage}, reliability ${self.reliability})"