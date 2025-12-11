from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel,
    QMessageBox, QRadioButton, QButtonGroup, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import pyqtSignal, Qt
from game.systems.inventory import generate_offers


class BuyStockDialog(QDialog):
    stock_changed = pyqtSignal(list)   # emits list of textual purchase summaries

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Buy Ingredients")
        self.setMinimumWidth(520)

        self.cart = []

        layout = QVBoxLayout(self)

        # -----------------------------------------------------
        # Ingredient List
        # -----------------------------------------------------
        self.list = QListWidget()
        self.ingredients = self.game.ingredients
        for ing in self.ingredients:
            self.list.addItem(ing.name)
        layout.addWidget(self.list)

        # -----------------------------------------------------
        # Info Box
        # -----------------------------------------------------
        self.info = QLabel("Select an ingredient.")
        self.info.setStyleSheet("""
            background: #fdfdfd;
            color: black;
            padding: 8px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            """)
        layout.addWidget(self.info)

        # -----------------------------------------------------
        # CASH PREVIEW LABEL
        # -----------------------------------------------------
        self.cash_preview = QLabel(f"Cash Available: ${self.game.cash:.2f}")
        self.cash_preview.setStyleSheet("padding:4px; font-weight:bold;")
        layout.addWidget(self.cash_preview)

        # -----------------------------------------------------
        # Vendor Selection
        # -----------------------------------------------------
        self.vendor_group = QButtonGroup(self)
        self.retail_radio = QRadioButton("Vendor 1 (Retail)")
        self.bulk_radio = QRadioButton("Vendor 2 (Bulk)")
        self.retail_radio.setChecked(True)

        self.vendor_group.addButton(self.retail_radio)
        self.vendor_group.addButton(self.bulk_radio)

        vendor_row = QVBoxLayout()
        vendor_row.addWidget(self.retail_radio)
        vendor_row.addWidget(self.bulk_radio)
        layout.addLayout(vendor_row)

        # -----------------------------------------------------
        # Quantity selector
        # -----------------------------------------------------
        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("Bundles:"))

        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(999)
        qty_row.addWidget(self.qty_spin)

        layout.addLayout(qty_row)

        # -----------------------------------------------------
        # Add to Cart
        # -----------------------------------------------------
        add_btn = QPushButton("Add to Cart")
        add_btn.clicked.connect(self.add_to_cart)
        layout.addWidget(add_btn)

        # -----------------------------------------------------
        # CART TABLE
        # -----------------------------------------------------
        self.cart_table = QTableWidget(0, 4)
        self.cart_table.setHorizontalHeaderLabels(["Ingredient", "Qty", "Vendor", "Cost"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cart_table)

        # -----------------------------------------------------
        # Checkout Button
        # -----------------------------------------------------
        checkout_btn = QPushButton("Checkout & Close")
        checkout_btn.clicked.connect(self.checkout)
        layout.addWidget(checkout_btn)

        # Load offers
        self.offers = generate_offers(self.ingredients)

        # UI events
        self.list.currentRowChanged.connect(self.update_preview)
        self.retail_radio.toggled.connect(self.update_preview)
        self.bulk_radio.toggled.connect(self.update_preview)
        self.qty_spin.valueChanged.connect(self.update_preview)


    # -----------------------------------------------------------------
    # PREVIEW including Cash Remaining
    # -----------------------------------------------------------------
    def update_preview(self):
        idx = self.list.currentRow()
        if idx < 0:
            self.info.setText("Select an ingredient.")
            self.cash_preview.setText(f"Cash Available: ${self.game.cash:.2f}")
            return

        ing = self.ingredients[idx]
        off = self.offers[ing]

        bulk_min = off["bulk"]["min"]
        retail_bundle = max(1, bulk_min // 4)

        retail_unit = off["retail"]["unit"]
        bulk_unit = off["bulk"]["unit"]

        bundles = self.qty_spin.value()

        if self.retail_radio.isChecked():
            qty = retail_bundle * bundles
            cost = retail_bundle * retail_unit * bundles
            vendor = "Retail"
        else:
            qty = bulk_min * bundles
            cost = bulk_min * bulk_unit * bundles
            vendor = "Bulk"

        # Cash remaining preview
        remaining = self.game.cash - cost
        color = "green" if remaining >= 0 else "red"

        self.cash_preview.setText(
            f"Cash Available: ${self.game.cash:.2f}  →  "
            f"<span style='color:{color};'>After Purchase: ${remaining:.2f}</span>"
        )

        self.info.setText(
            f"<b>{ing.name}</b><br><br>"
            f"Vendor: {vendor}<br>"
            f"Bundles: {bundles}<br>"
            f"Units: {qty}<br>"
            f"Total Cost: <b>${cost:.2f}</b><br><br>"
            f"<i>Retail</i>: {retail_bundle} units @ ${retail_unit:.2f}<br>"
            f"<i>Bulk</i>: {bulk_min} units @ ${bulk_unit:.2f}"
        )


    # -----------------------------------------------------------------
    # Add to cart
    # -----------------------------------------------------------------
    def add_to_cart(self):
        idx = self.list.currentRow()
        if idx < 0:
            return

        ing = self.ingredients[idx]
        off = self.offers[ing]

        bulk_min = off["bulk"]["min"]
        retail_bundle = max(1, bulk_min // 4)

        retail_unit = off["retail"]["unit"]
        bulk_unit = off["bulk"]["unit"]

        bundles = self.qty_spin.value()

        if self.retail_radio.isChecked():
            qty = retail_bundle * bundles
            cost = retail_bundle * retail_unit * bundles
            vendor = "Retail"
        else:
            qty = bulk_min * bundles
            cost = bulk_min * bulk_unit * bundles
            vendor = "Bulk"

        # Add to cart list
        self.cart.append((ing, qty, cost, vendor))

        # Add to cart UI table
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(ing.name))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(vendor))
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"${cost:.2f}"))

        # Recalculate preview so Cash Available stays accurate
        self.update_preview()


    # -----------------------------------------------------------------
    # Checkout
    # -----------------------------------------------------------------
    def checkout(self):
        if not self.cart:
            self.accept()
            return
    
        total_cost = sum(item[2] for item in self.cart)
    
        # ---------------------------------------------------------
        # FUNDS CHECK
        # ---------------------------------------------------------
        if total_cost > self.game.cash:
            QMessageBox.warning(
                self,
                "Insufficient Funds",
                (
                    f"Total cost is ${total_cost:.2f}, but you only have "
                    f"${self.game.cash:.2f} available."
                )
            )
            return
    
        # ---------------------------------------------------------
        # APPLY PURCHASES
        # ---------------------------------------------------------
        summary = []
    
        for ing, qty, cost, vendor in self.cart:
            # Deduct cash
            self.game.cash -= cost
    
            # Increase stock
            self.game.stock[ing] += qty
    
            # Track ingredient cost for the daily summary
            self.game.dailyIngredientCost += cost
    
            summary.append(f"Bought {qty} × {ing.name} from {vendor} (${cost:.2f})")
    
        # Emit summary back to main window UI
        self.stock_changed.emit(summary)
    
        # Close dialog
        self.accept()