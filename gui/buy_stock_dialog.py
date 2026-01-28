from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QRadioButton, QButtonGroup, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt

from game.systems.inventory import generate_offers
from game.utils.constants import INGREDIENTS_BY_CATEGORY


class BuyStockDialog(QDialog):
    stock_changed = pyqtSignal(list)

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Buy Ingredients")
        self.setMinimumWidth(560)

        self.cart = []

        layout = QVBoxLayout(self)

        # -----------------------------------------------------
        # INGREDIENT TREE (Categories → Ingredients)
        # -----------------------------------------------------
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        layout.addWidget(self.tree)

        self.ingredients = []

        for category, items in INGREDIENTS_BY_CATEGORY.items():
            # Category node
            cat_item = QTreeWidgetItem([category])
            cat_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            cat_item.setExpanded(True)
            cat_item.setBackground(0, Qt.GlobalColor.black)
            self.tree.addTopLevelItem(cat_item)

            # Ingredient children
            for ing in items:
                child = QTreeWidgetItem([ing.name])
                child.setData(0, Qt.ItemDataRole.UserRole, ing)
                cat_item.addChild(child)
                self.ingredients.append(ing)

        # -----------------------------------------------------
        # Info Box
        # -----------------------------------------------------
        self.info = QLabel("Select an ingredient.")
        self.info.setStyleSheet("""
            background: #ffffff;
            color: black;
            padding: 8px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        """)
        layout.addWidget(self.info)

        # -----------------------------------------------------
        # CASH PREVIEW
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
        self.cart_table.setHorizontalHeaderLabels(
            ["Ingredient", "Qty", "Vendor", "Cost"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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
        self.tree.currentItemChanged.connect(self.update_preview)
        self.retail_radio.toggled.connect(self.update_preview)
        self.bulk_radio.toggled.connect(self.update_preview)
        self.qty_spin.valueChanged.connect(self.update_preview)

    # -----------------------------------------------------------------
    # PREVIEW including Cash Remaining
    # -----------------------------------------------------------------
    def update_preview(self):
        item = self.tree.currentItem()
        if not item:
            return

        ing = item.data(0, Qt.ItemDataRole.UserRole)
        if ing is None:
            # Category selected
            self.info.setText("Select an ingredient.")
            self.cash_preview.setText(
                f"Cash Available: ${self.game.cash:.2f}"
            )
            return

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

        remaining = self.game.cash - cost
        color = "green" if remaining >= 0 else "red"

        self.cash_preview.setText(
            f"Cash Available: ${self.game.cash:.2f} → "
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
        item = self.tree.currentItem()
        if not item:
            return

        ing = item.data(0, Qt.ItemDataRole.UserRole)
        if ing is None:
            return  # category clicked

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

        self.cart.append((ing, qty, cost, vendor))

        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(ing.name))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(vendor))
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"${cost:.2f}"))

        self.update_preview()

    # -----------------------------------------------------------------
    # Checkout
    # -----------------------------------------------------------------
    def checkout(self):
        if not self.cart:
            self.accept()
            return

        total_cost = sum(item[2] for item in self.cart)

        if total_cost > self.game.cash:
            QMessageBox.warning(
                self,
                "Insufficient Funds",
                (
                    f"Total cost is ${total_cost:.2f}, "
                    f"but you only have ${self.game.cash:.2f}."
                )
            )
            return

        summary = []

        for ing, qty, cost, vendor in self.cart:
            self.game.cash -= cost
            self.game.stock[ing] += qty
            self.game.dailyIngredientCost += cost
            summary.append(
                f"Bought {qty} × {ing.name} from {vendor} (${cost:.2f})"
            )

        self.stock_changed.emit(summary)
        self.accept()