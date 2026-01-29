from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

from gui.hire_dialog import HireDialog
from gui.buy_stock_dialog import BuyStockDialog
from gui.create_drink_dialog import CreateDrinkDialog
from gui.upgrade_venue_dialog import UpgradeVenueDialog
from gui.loan_dialog import LoanDialog

class Action(QDialog):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Actions")
        self.setMinimumWidth(320)

        # Track all changes made this morning
        self.changes = {
            "hired": [],
            "fired": [],
            "stock": [],
            "drinks": [],
            "loans": [],
            "ads": None,
        }

        layout = QVBoxLayout(self)

        # --------------------------------------------------
        # ACTION BUTTONS
        # --------------------------------------------------
        hire_btn = QPushButton("Hire Employees")
        hire_btn.clicked.connect(self.open_hire)

        stock_btn = QPushButton("Buy Stock")
        stock_btn.clicked.connect(self.open_buy_stock)

        drink_btn = QPushButton("Create New Drink")
        drink_btn.clicked.connect(self.open_create_drink)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self.accept)
        upgrade_btn = QPushButton("Upgrade Venue")
        upgrade_btn.clicked.connect(self.open_upgrade_venue)
        loan_btn = QPushButton("Take Loan")
        loan_btn.clicked.connect(self.open_loan)

        layout.addWidget(hire_btn)
        layout.addWidget(stock_btn)
        layout.addWidget(drink_btn)
        layout.addWidget(upgrade_btn)
        layout.addWidget(loan_btn)


        # --------------------------------------------------
        # SUMMARY BOX
        # --------------------------------------------------
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        self.summary_label.setStyleSheet("""
            background: #fdfdfd;
            color: black;
            padding: 8px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)
        layout.addWidget(self.summary_label)

        # Finish button
        layout.addWidget(done_btn)

        self.update_summary_box()

    # --------------------------------------------------
    # Dialog open triggers
    # --------------------------------------------------
    def open_hire(self):
        dlg = HireDialog(self.game)
        dlg.hired.connect(self._record_hired)
        dlg.exec()
        self.update_summary_box()

    def open_buy_stock(self):
        dlg = BuyStockDialog(self.game)
        dlg.stock_changed.connect(self._record_stock)
        dlg.exec()
        self.update_summary_box()

    def open_create_drink(self):
        dlg = CreateDrinkDialog(self.game)
        if dlg.exec():
            # Newly created drink is already added to game.menu
            self.changes["drinks"].append(self.game.menu[-1].name)
        self.update_summary_box()

    # --------------------------------------------------
    # Change recorders
    # --------------------------------------------------
    def _record_hired(self, employees):
        for e in employees:
            self.changes["hired"].append(e.name)

    def _record_stock(self, text):
        self.changes["stock"].extend(text)

    # --------------------------------------------------
    # Summary Text
    # --------------------------------------------------
    def update_summary_box(self):
        txt = "<b>Today's Adjustments:</b><br><br>"

        if self.changes["hired"]:
            txt += "<b>Hired:</b> " + ", ".join(self.changes["hired"]) + "<br>"

        if self.changes["fired"]:
            txt += "<b>Fired:</b> " + ", ".join(self.changes["fired"]) + "<br>"

        if self.changes["stock"]:
            txt += "<b>Stock Purchases:</b><br>"
            for s in self.changes["stock"]:
                txt += f" - {s}<br>"

        if self.changes["drinks"]:
            txt += "<b>New Drinks:</b> " + ", ".join(self.changes["drinks"]) + "<br>"

        if self.changes["ads"] is not None:
            txt += f"<b>Ad Budget:</b> ${self.changes['ads']:.2f}<br>"
        
        if "venue" in self.changes and self.changes["venue"]:
            txt += "<b>Venue Upgraded:</b> " + ", ".join(self.changes["venue"]) + "<br>"
        
        if self.changes["loans"]:
            txt += "<b>Loans Taken:</b> " + ", ".join(self.changes["loans"]) + "<br>"
        
        if txt.strip() == "<b>Today's Adjustments:</b><br><br>":
            txt += "No changes made."

        self.summary_label.setText(txt)
    
    def open_upgrade_venue(self):
        dlg = UpgradeVenueDialog(self.game)
        if dlg.exec():
            self.changes.setdefault("venue", []).append(self.game.venue.name)
        self.update_summary_box()

    def open_loan(self):
        dlg = LoanDialog(self.game)
        before = self.game.cash
        if dlg.exec():
            # Record which loan was taken (most recent loan added)
            # (safe even with multiple loans, since take_loan appends)
            if self.game.loans:
                self.changes["loans"].append(self.game.loans[-1].name)
        self.update_summary_box()