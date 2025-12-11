from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from game.systems.hiring import generate_candidates

class HireDialog(QDialog):
    hired = pyqtSignal(list)

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Hire Employees")
        self.setMinimumWidth(420)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Get candidates
        self.candidates = generate_candidates(game)
        self.selected_index = None

        # Card container
        card_row = QHBoxLayout()
        layout.addLayout(card_row)

        self.card_widgets = []

        for i, cand in enumerate(self.candidates):
            card = self.create_card(cand, i)
            self.card_widgets.append(card)
            card_row.addWidget(card)

        # Hire button
        hire_btn = QPushButton("Hire Selected")
        hire_btn.clicked.connect(self.hire)
        layout.addWidget(hire_btn)

    def create_card(self, cand, index):
        """
        Creates a clickable employee card.
        """
        box = QGroupBox()
        box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #888;
                border-radius: 8px;
                padding: 10px;
            }
            QGroupBox:hover {
                border: 2px solid #55aaff;
            }
        """)
        box.setCursor(Qt.CursorShape.PointingHandCursor)

        v = QVBoxLayout()
        v.addWidget(QLabel(f"<b>{cand.name}</b>"))
        v.addWidget(QLabel(f"Capacity: {cand.capacity}"))
        v.addWidget(QLabel(f"Charm: {cand.charm}"))
        v.addWidget(QLabel(f"Reliability: {cand.reliability}"))
        v.addWidget(QLabel(f"Wage: ${cand.wage}"))
        box.setLayout(v)

        # Store index and card
        box.mousePressEvent = lambda e, idx=index: self.select_card(idx)

        return box

    def select_card(self, index):
        """
        Visually highlight selected card.
        """
        self.selected_index = index

        for i, card in enumerate(self.card_widgets):
            if i == index:
                card.setStyleSheet("""
                    QGroupBox {
                        border: 3px solid #33cc33;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """)
            else:
                card.setStyleSheet("""
                    QGroupBox {
                        border: 2px solid #888;
                        border-radius: 8px;
                        padding: 10px;
                    }
                    QGroupBox:hover {
                        border: 2px solid #55aaff;
                    }
                """)

    def hire(self):
        if self.selected_index is None:
            return

        chosen = self.candidates[self.selected_index]

        # Add employee to the game
        self.game.employees.append(chosen)

        # Emit signal for UI update
        self.hired.emit([chosen])

        self.accept()