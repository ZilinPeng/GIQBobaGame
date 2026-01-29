# gui/loan_dialog.py

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QScrollArea,
    QWidget,
)
from PyQt6.QtCore import Qt

from game.utils.constants import LOAN_OPTIONS


class LoanDialog(QDialog):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Take a Loan")
        self.setMinimumSize(620, 520)

        main_layout = QVBoxLayout(self)

        # --------------------------------------------------
        # TOP INSTRUCTIONS (WHITE TEXT)
        # --------------------------------------------------
        instructions = QLabel(
            """
            <b>How loans work</b><br>
            • Each loan can only be active once at a time<br>
            • You may retake a loan after it is fully paid off<br>
            • You pay a fixed % of the original principal each turn<br>
            • Interest compounds on the remaining balance after payment<br>
            • Loans automatically close when balance ≤ 0
            """
        )
        instructions.setTextFormat(Qt.TextFormat.RichText)
        instructions.setStyleSheet("""
            color: white;
            font-size: 13px;
            background: #222;
            padding: 10px;
            border-radius: 8px;
        """)
        main_layout.addWidget(instructions)

        # --------------------------------------------------
        # SCROLL AREA
        # --------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        cards_layout = QVBoxLayout(container)
        cards_layout.setSpacing(12)

        for opt in LOAN_OPTIONS:
            cards_layout.addWidget(self._build_loan_card(opt))

        cards_layout.addStretch()

        # --------------------------------------------------
        # CLOSE BUTTON
        # --------------------------------------------------
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid black;
                padding: 6px 16px;
                background: #f5f5f5;
                color: black;
            }
            QPushButton:hover {
                background: #e6e6e6;
            }
        """)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    # --------------------------------------------------
    # LOAN CARD
    # --------------------------------------------------
    def _build_loan_card(self, opt):
        box = QWidget()
        box.setObjectName("loanCard")

        v = QVBoxLayout(box)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(6)

        active = self.game.has_active_loan(opt.name)
        payment = opt.amount * opt.payback_rate

        title = QLabel(opt.name)
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: black;")
        v.addWidget(title)

        details = QLabel(
            f"""
            <span style="color:black; font-size:13px;">
            <b>Loan Amount:</b> ${opt.amount:,.0f}<br>
            <b>Interest:</b> {opt.interest_rate * 100:.2f}% per turn<br>
            <b>Payback Rate:</b> {opt.payback_rate * 100:.2f}% of principal<br>
            <b>Principal Payment:</b> ${payment:,.2f} per turn
            </span>
            """
        )
        details.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(details)

        row = QHBoxLayout()
        row.addStretch()

        take_btn = QPushButton("Active" if active else "Take Loan")
        take_btn.setEnabled(not active)
        take_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid black;
                padding: 6px 14px;
                color: black;
                background: white;
            }
            QPushButton:disabled {
                color: #777;
                border-color: #999;
                background: #f0f0f0;
            }
            QPushButton:hover:!disabled {
                background: #eaeaea;
            }
        """)
        take_btn.clicked.connect(lambda _=False, o=opt: self._take(o))
        row.addWidget(take_btn)

        v.addLayout(row)

        box.setStyleSheet("""
            QWidget#loanCard {
                border: 1px solid black;
                border-radius: 10px;
                background: white;
            }
        """)

        return box

    # --------------------------------------------------
    # TAKE LOAN
    # --------------------------------------------------
    def _take(self, opt):
        if not self.game.take_loan(opt):
            QMessageBox.information(
                self,
                "Loan Not Available",
                "This loan is already active.\nPay it off before taking it again."
            )
            return

        QMessageBox.information(
            self,
            "Loan Taken",
            f"You received ${opt.amount:,.0f} from '{opt.name}'."
        )
        self.accept()