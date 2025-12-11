from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from gui.hire_dialog import HireDialog
from gui.buy_stock_dialog import BuyStockDialog


class Action(QDialog):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Actions")
        self.setMinimumWidth(300)

        # Track all changes made this morning
        self.changes = {
            "hired": [],
            "fired": [],
            "stock": [],
            "ads": None
        }

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Buttons
        hire_btn = QPushButton("Hire Employees")
        hire_btn.clicked.connect(self.open_hire)

        stock_btn = QPushButton("Buy Stock")
        stock_btn.clicked.connect(self.open_buy_stock)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self.accept)

        layout.addWidget(hire_btn)
        layout.addWidget(stock_btn)

        # --- Summary box ---
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignTop)
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

        # Initial summary
        self.update_summary_box()

    # ----------------------------------------------------------
    # Dialog open triggers
    # ----------------------------------------------------------
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

    # ----------------------------------------------------------
    # Change recorders
    # ----------------------------------------------------------
    def _record_hired(self, employees):
        for e in employees:
            self.changes["hired"].append(e.name)
        self.update_summary_box()

    def _record_stock(self, text):
        self.changes["stock"].append(text)
        self.update_summary_box()

    # ----------------------------------------------------------
    # Summary Text
    # ----------------------------------------------------------
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

        if self.changes["ads"] is not None:
            txt += f"<b>Ad Budget:</b> ${self.changes['ads']:.2f}<br>"

        # If no changes at all
        if txt.strip() == "<b>Today's Adjustments:</b><br><br>":
            txt += "No changes made."

        self.summary_label.setText(txt)