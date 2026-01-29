from __future__ import annotations


class LoanOption:
    def __init__(self, name: str, amount: float, interest_rate: float, payback_rate: float):
        self.name = name
        self.amount = float(amount)
        self.interest_rate = float(interest_rate)
        self.payback_rate = float(payback_rate)

    @property
    def payment_per_turn(self) -> float:
        return self.amount * self.payback_rate


class Loan:
    def __init__(self, option: LoanOption):
        self.option = option
        self.principal = option.amount
        self.interest_rate = option.interest_rate
        self.payback_rate = option.payback_rate
        self.payment_per_turn = option.payment_per_turn
        self.remaining_balance = option.amount

    @property
    def name(self) -> str:
        return self.option.name
    def __str__(self):
        return self.name