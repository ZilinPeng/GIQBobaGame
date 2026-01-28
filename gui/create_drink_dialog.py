from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

from game.models.drink import Drink
from game.utils.constants import INGREDIENTS_BY_CATEGORY


class CreateDrinkDialog(QDialog):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Create New Drink")
        self.setMinimumWidth(650)

        layout = QVBoxLayout(self)

        # ---------------- Name ----------------
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Drink Name:"))
        self.name_input = QLineEdit()
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)

        # ---------------- Size ----------------
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size_box = QComboBox()
        self.size_box.addItems(["regular", "tall"])
        size_row.addWidget(self.size_box)
        layout.addLayout(size_row)

        # ---------------- Ingredient Table ----------------
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Ingredient", "Qty", "Unit Cost"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.ingredients = []  # (Ingredient, QSpinBox)

        # Populate table with category dividers
        for category, items in INGREDIENTS_BY_CATEGORY.items():
            # --- Category divider row ---
            row = self.table.rowCount()
            self.table.insertRow(row)

            header_item = QTableWidgetItem(f"{category}")
            header_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            header_item.setBackground(Qt.GlobalColor.lightGray)
            header_item.setFont(self._bold_font())
            header_item.setForeground(Qt.GlobalColor.black)
            self.table.setItem(row, 0, header_item)
            self.table.setSpan(row, 0, 1, 3)

            # --- Ingredient rows ---
            for ing in items:
                row = self.table.rowCount()
                self.table.insertRow(row)

                name_item = QTableWidgetItem(ing.name)
                name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 0, name_item)

                qty_spin = QSpinBox()
                qty_spin.setMinimum(0)
                qty_spin.setMaximum(10)
                qty_spin.valueChanged.connect(self.update_cost)
                self.table.setCellWidget(row, 1, qty_spin)

                cost_item = QTableWidgetItem(f"${ing.unit_cost:.2f}")
                cost_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 2, cost_item)

                self.ingredients.append((ing, qty_spin))

        # ---------------- Cost Preview ----------------
        self.cost_label = QLabel("Estimated Cost: $0.00")
        self.cost_label.setStyleSheet("font-weight:bold;")
        layout.addWidget(self.cost_label)

        # ---------------- Price Input ----------------
        price_row = QHBoxLayout()
        price_row.addWidget(QLabel("Sell Price:"))
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g. 4.50")
        price_row.addWidget(self.price_input)
        layout.addLayout(price_row)

        # ---------------- Buttons ----------------
        btn_row = QHBoxLayout()
        create_btn = QPushButton("Create Drink")
        cancel_btn = QPushButton("Cancel")

        create_btn.clicked.connect(self.create_drink)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(create_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.update_cost()

    # --------------------------------------------------
    # Cost calculation
    # --------------------------------------------------
    def update_cost(self):
        total = 0.0
        for ing, spin in self.ingredients:
            total += spin.value() * ing.unit_cost

        self.estimated_cost = total
        self.cost_label.setText(f"Estimated Cost: ${total:.2f}")

    # --------------------------------------------------
    # Create drink
    # --------------------------------------------------
    def create_drink(self):
        name = self.name_input.text().strip()
        if not name:
            return

        try:
            price = float(self.price_input.text())
        except ValueError:
            return

        recipe = {
            ing: spin.value()
            for ing, spin in self.ingredients
            if spin.value() > 0
        }

        if not recipe:
            return

        drink = Drink(
            name=name,
            recipe=recipe,
            basePrice=price,
            baseDesirability=5,
            size=self.size_box.currentText(),
        )

        self.game.menu.append(drink)
        self.accept()

    def _bold_font(self):
        font = self.font()
        font.setBold(True)
        return font