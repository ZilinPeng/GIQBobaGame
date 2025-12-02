class Employee:
    def __init__(self, name, wage, capacity, reliability):
        self.name = name
        self.wage = wage
        self.capacity = capacity 
        self.reliability = reliability
    
    def __str__(self):
        return f"Name: {self.name}, Daily Wage: {self.wage}, Customer Capacity Per Turn: {self.capacity}"

    def print_attribute_description(self):
        ename = ''
        ewage = ''
        ecapacity = ''
        ereliability = ''