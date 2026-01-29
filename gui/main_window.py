# gui/main_window.py

from __future__ import annotations

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QProgressBar,
    QPlainTextEdit,
    QSplitter,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from game.config import TURNS_PER_DAY
from game.game import Game
from gui.action_dialog import Action


class GameThread(QThread):
    tick = pyqtSignal(dict)
    finished = pyqtSignal(dict)

    def __init__(self, game: Game, turns: int):
        super().__init__()
        self.game = game
        self.turns = turns

    def run(self):
        stats = {
            "served": 0,
            "lost_queue": 0,
            "lost_stock": 0,
            "lost_patience": 0,
        }

        hour_sales: dict[str, dict[str, int]] = {}

        # Revenue = sum of prices of sold drinks (NOT cash delta)
        revenue = 0.0

        for t in range(self.turns):
            prev_stock = dict(self.game.stock)

            served, lostQ, lostS, lostP, drinks_list = self.game.single_turn()

            stats["served"] += served
            stats["lost_queue"] += lostQ
            stats["lost_stock"] += lostS
            stats["lost_patience"] += lostP

            revenue += sum(d.basePrice for d in drinks_list)

            clock = self.clock_from_turn(t)
            hour_label = clock.split(":")[0] + ":00"
            hour_sales.setdefault(hour_label, {})

            for drink in drinks_list:
                hour_sales[hour_label][drink.name] = hour_sales[hour_label].get(drink.name, 0) + 1

            stock_changes = {}
            for ing, old_qty in prev_stock.items():
                new_qty = self.game.stock.get(ing, 0)
                delta = new_qty - old_qty
                if delta != 0:
                    stock_changes[ing] = delta

            self.tick.emit({
                "turn": t,
                "clock": clock,
                "served": served,
                "lost_queue": lostQ,
                "lost_stock": lostS,
                "lost_patience": lostP,
                "queue_size": len(self.game.venue.line),
                "cash": self.game.cash,
                "stock_changes": stock_changes,
            })
        
        self.game.process_loans_per_day()

        # End-of-day accounting
        wages = sum(e.wage for e in self.game.employees)
        rent = float(self.game.venue.rent)

        # Loan payments made TODAY only
        loans_today = float(self.game.dailyLoanPayments)
        print(loans_today)
        total_expenses = (
            float(self.game.dailyIngredientCost)
            + float(self.game.dailyAdSpend)
            + float(wages)
            + float(rent)
            + loans_today
        )

        profit = revenue - total_expenses
        self.game.cash -= (wages + rent)

        summary = {
            "served": stats["served"],
            "lost_queue": stats["lost_queue"],
            "lost_stock": stats["lost_stock"],
            "lost_patience": stats["lost_patience"],
            "revenue": revenue,
            "expenses": total_expenses,
            "loan_payments": loans_today,
            "profit": profit,
            "cash_end": self.game.cash,
            "hour_sales": hour_sales,
        }

        self.finished.emit(summary)

    @staticmethod
    def clock_from_turn(turn_idx: int) -> str:
        minutes = turn_idx * 15
        hour = 8 + minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Boba Tycoon")
        self.resize(1400, 900)

        self.game = Game()

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # ================= LEFT PANEL =================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        splitter.addWidget(left_scroll)

        left_container = QWidget()
        left_scroll.setWidget(left_container)
        left_layout = QVBoxLayout(left_container)

        self.cash_label = QLabel()
        self.cash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.cash_label)

        self.venue_label = QLabel()
        left_layout.addWidget(self.venue_label)

        self.employee_label = QLabel()
        self.employee_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.employee_label)

        self.menu_label = QLabel()
        self.menu_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.menu_label)

        self.stock_label = QLabel()
        self.stock_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.stock_label)

        # Loan section
        self.loan_label = QLabel()
        self.loan_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.loan_label)

        btn_row = QHBoxLayout()
        self.action_btn = QPushButton("Action")
        self.run_btn = QPushButton("Run Day")
        btn_row.addWidget(self.action_btn)
        btn_row.addWidget(self.run_btn)
        left_layout.addLayout(btn_row)

        self.bar = QProgressBar()
        self.bar.setMaximum(TURNS_PER_DAY)
        left_layout.addWidget(self.bar)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(200)
        self.log_edit.setStyleSheet(
            "background-color: #111; color: #eee; font-family: monospace;"
        )
        left_layout.addWidget(self.log_edit)

        self.summary_label = QLabel("Day summary will appear here.")
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.summary_label)

        left_layout.addStretch()

        # ================= RIGHT PANEL =================
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        splitter.addWidget(right_scroll)

        right_container = QWidget()
        right_scroll.setWidget(right_container)
        right_layout = QVBoxLayout(right_container)

        self.sales_chart = FigureCanvasQTAgg(Figure(figsize=(6, 4)))
        self.ax = self.sales_chart.figure.subplots()
        right_layout.addWidget(self.sales_chart)

        right_layout.addStretch()

        self.action_btn.clicked.connect(self.open_action)
        self.run_btn.clicked.connect(self.run_day)

        self.update_info()

    def open_action(self):
        dialog = Action(self.game)
        dialog.exec()
        self.update_info()

    def run_day(self):
        self.game.opening_cash = self.game.cash
        self.game.dailyLoanPayments = 0.0

        self.bar.setValue(0)
        self.log_edit.clear()

        self.run_btn.setEnabled(False)
        self.action_btn.setEnabled(False)

        self.thread = GameThread(self.game, turns=TURNS_PER_DAY)
        self.thread.tick.connect(self.on_tick)
        self.thread.finished.connect(self.on_day_finished)
        self.thread.finished.connect(self._reenable_controls)
        self.thread.start()

    def _reenable_controls(self, *_args):
        self.run_btn.setEnabled(self.game.cash >= 0)
        self.action_btn.setEnabled(True)

    def on_tick(self, info: dict):
        self.bar.setValue(info["turn"] + 1)

        stock_parts = []
        for ing, delta in info["stock_changes"].items():
            stock_parts.append(f"{ing.name} {delta:+}")
        stock_str = ", ".join(stock_parts) if stock_parts else "—"

        self.log_edit.appendPlainText(
            f"[{info['clock']}] "
            f"Q={info['queue_size']} "
            f"Served={info['served']} "
            f"LostQ={info['lost_queue']} "
            f"LostS={info['lost_stock']} "
            f"LostP={info['lost_patience']} "
            f"Cash=${info['cash']:.2f} "
            f"Stock: {stock_str}"
        )

        self.update_info()

    def on_day_finished(self, summary: dict):
        wages = sum(e.wage for e in self.game.employees)
        rent = float(self.game.venue.rent)
        ingredients = float(self.game.dailyIngredientCost)
        ads = float(self.game.dailyAdSpend)
        loans = float(summary.get("loan_payments", 0.0))

        # Revenue breakdown by drink
        drink_totals = defaultdict(int)
        for hour_map in summary["hour_sales"].values():
            for drink_name, count in hour_map.items():
                drink_totals[drink_name] += count

        revenue_lines = ""
        if drink_totals:
            revenue_lines += "<b>Revenue Breakdown (cups):</b><br>"
            for name in sorted(drink_totals.keys()):
                revenue_lines += f" - {name}: {drink_totals[name]}<br>"
            revenue_lines += "<br>"

        total_expenses = float(summary["expenses"])

        text = (
            f"<b>Day Summary</b><br>"
            f"<b>Opening Cash:</b> ${self.game.opening_cash:.2f}<br>"
            f"--------------------------<br>"
            f"<b>Served:</b> {summary['served']}<br>"
            f"<b>Lost (queue):</b> {summary['lost_queue']}<br>"
            f"<b>Lost (stock):</b> {summary['lost_stock']}<br>"
            f"<b>Lost (patience):</b> {summary['lost_patience']}<br><br>"
            f"{revenue_lines}"
            f"<b>Revenue:</b> ${summary['revenue']:.2f}<br><br>"
            f"<b>Expenses</b><br>"
            f" - Ingredients: ${ingredients:.2f}<br>"
            f" - Advertising: ${ads:.2f}<br>"
            f" - Wages:       ${wages:.2f}<br>"
            f" - Rent:        ${rent:.2f}<br>"
            f" - Loans:       ${loans:.2f}<br>"
            f"<b>Total Expenses:</b> ${total_expenses:.2f}<br><br>"
            f"<b>Profit:</b> ${summary['profit']:.2f}<br>"
            f"<b>Cash End:</b> ${summary['cash_end']:.2f}<br>"
        )

        self.summary_label.setText(text)

        self.render_hourly_sales_chart(summary["hour_sales"])
        self.update_info()

        # Reset daily counters
        self.game.dailyIngredientCost = 0
        self.game.dailyAdSpend = 0
        if hasattr(self.game, "dailyLoanPayments"):
            self.game.dailyLoanPayments = 0.0

    def update_info(self):
        self.cash_label.setText(f"<b>Cash:</b> ${self.game.cash:.2f}")

        # Disable Run Day if cash < 0
        self.run_btn.setEnabled(self.game.cash >= 0)

        v = self.game.venue
        self.venue_label.setText(
            f"<b>Venue:</b> {v.name} "
            f"(Max line: {v.maxLine}, Foot traffic: {v.footTraffic}, Rent: ${v.rent})"
        )

        e_lines = ["<b>Employees:</b>"]
        for emp in self.game.employees:
            e_lines.append(
                f" - {emp.name}: Cap {emp.capacity}, Charm {emp.charm}, Wage ${emp.wage}"
            )
        self.employee_label.setText("<br>".join(e_lines))

        m_lines = ["<b>Menu:</b>"]
        for drink in self.game.menu:
            m_lines.append(f" - {drink.name} (${drink.basePrice:.2f})")
        self.menu_label.setText("<br>".join(m_lines))

        LOW_STOCK_THRESHOLD = 10
        s_lines = ["<b>Stock:</b>"]

        by_category = defaultdict(list)
        for ing in self.game.ingredients:
            by_category[ing.category].append(ing)

        for category, items in by_category.items():
            s_lines.append(f"<br><b>── {category} ──</b>")
            for ing in items:
                qty = self.game.stock.get(ing, 0)
                if qty <= LOW_STOCK_THRESHOLD:
                    qty_text = f"<span style='color:red; font-weight:bold;'>{qty}</span>"
                else:
                    qty_text = str(qty)
                s_lines.append(f"&nbsp;&nbsp;{ing.name}: {qty_text}")

        self.stock_label.setText("<br>".join(s_lines))

        # Loan display
        loan_lines = ["<b>Loans:</b>"]
        if hasattr(self.game, "loans") and self.game.loans:
            for loan in self.game.loans:
                loan_lines.append(
                    f"&nbsp;&nbsp;{loan.name}: "
                    f"<b>${loan.remaining_balance:.2f}</b> "
                    f"(Pay ${loan.payment_per_turn:.2f}/turn)"
                )
        else:
            loan_lines.append("&nbsp;&nbsp;None")

        self.loan_label.setText("<br>".join(loan_lines))

    def render_hourly_sales_chart(self, hour_sales):
        self.ax.clear()

        if not hour_sales:
            self.ax.set_title("No Sales Data")
            self.sales_chart.draw()
            return

        hours = sorted(hour_sales.keys())
        drink_names = sorted({
            drink
            for hour in hour_sales.values()
            for drink in hour.keys()
        })

        if not drink_names:
            self.ax.set_title("No Drinks Sold Today")
            self.sales_chart.draw()
            return

        x = np.arange(len(hours))
        width = 0.8 / max(1, len(drink_names))

        cmap = plt.get_cmap("tab10")
        colors = {drink: cmap(i) for i, drink in enumerate(drink_names)}

        max_height = 0

        for i, drink in enumerate(drink_names):
            yvals = [hour_sales[h].get(drink, 0) for h in hours]
            max_height = max(max_height, max(yvals))

            rects = self.ax.bar(
                x + i * width,
                yvals,
                width,
                label=drink,
                color=colors[drink],
                zorder=3,
            )

            self.ax.bar_label(
                rects,
                labels=[str(v) if v > 0 else "" for v in yvals],
                padding=2,
                fontsize=9,
                color="white",
            )

        total_sales = [sum(hour_sales[h].values()) for h in hours]
        max_height = max(max_height, max(total_sales))
        center_x = x + width * (len(drink_names) - 1) / 2

        self.ax.plot(
            center_x,
            total_sales,
            color="black",
            marker="o",
            linewidth=2,
            label="Total Sales",
            zorder=5,
        )

        for xi, total in zip(center_x, total_sales):
            if total > 0:
                self.ax.text(
                    xi,
                    total + 0.2,
                    str(total),
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                    color="black",
                    zorder=6,
                )

        self.ax.set_ylim(0, max_height * 1.25 + 1)
        self.ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(hours)
        self.ax.set_xlabel("Hour of Day")
        self.ax.set_ylabel("Drinks Sold")
        self.ax.set_title("Hourly Drink Sales")
        self.ax.legend(title="Drink Types")
        self.sales_chart.draw()