# gui/main_window.py

from __future__ import annotations

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import copy
from typing import Dict
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
from gui.hire_dialog import HireDialog
from gui.buy_stock_dialog import BuyStockDialog


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

        hour_sales = {}    # { "09:00": { drink_name: count } }

        for t in range(self.turns):
            prev_cash = self.game.cash
            prev_stock = dict(self.game.stock)

            # Updated call — now returns 5 values
            served, lostQ, lostS, lostP, drinks_list = self.game.single_turn()

            # Update totals
            stats["served"] += served
            stats["lost_queue"] += lostQ
            stats["lost_stock"] += lostS
            stats["lost_patience"] += lostP

            # Determine hour label
            clock = self.clock_from_turn(t)        # e.g. "09:15"
            hour_label = clock.split(":")[0] + ":00"   # → "09:00"

            if hour_label not in hour_sales:
                hour_sales[hour_label] = {}

            # Count each drink sold this turn
            for drink in drinks_list:
                name = drink.name
                hour_sales[hour_label][name] = hour_sales[hour_label].get(name, 0) + 1

            # Cash delta
            cash_change = self.game.cash - prev_cash

            # Stock deltas
            stock_changes = {}
            for ing, old_qty in prev_stock.items():
                new_qty = self.game.stock.get(ing, 0)
                delta = new_qty - old_qty
                if delta != 0:
                    stock_changes[ing] = delta

            turn_info = {
                "turn": t,
                "clock": clock,
                "served": served,
                "lost_queue": lostQ,
                "lost_stock": lostS,
                "lost_patience": lostP,
                "queue_size": len(self.game.venue.line),
                "cash": self.game.cash,
                "cash_change": cash_change,
                "stock_changes": stock_changes,
            }

            self.tick.emit(turn_info)

        # End-of-day accounting
        wages = sum(e.wage for e in self.game.employees)
        rent = self.game.venue.rent
        revenue = self.game.cash - self.game.opening_cash
        expenses = wages + rent + self.game.dailyIngredientCost + self.game.dailyAdSpend
        profit = revenue - expenses
        self.game.cash -= expenses

        summary = {
            "served": stats["served"],
            "lost_queue": stats["lost_queue"],
            "lost_stock": stats["lost_stock"],
            "lost_patience": stats["lost_patience"],
            "revenue": revenue,
            "profit": profit,
            "expenses": expenses,
            "cash_end": self.game.cash,
            "hour_sales": hour_sales,      
        }

        self.finished.emit(summary)
    
    @staticmethod
    def clock_from_turn(turn_idx: int) -> str:
        """Convert turn index into HH:MM time, starting at 08:00, 15 minutes per turn."""
        minutes = turn_idx * 15
        hour = 8 + minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

class MainWindow(QWidget):
    """
    Main PyQt6 window for Boba Tycoon.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Boba Tycoon")

        self.resize(1400, 900)

        self.game = Game()
        # ----------------------------------------------------------
        # MAIN WINDOW SPLITTER (Left Panel | Right Panel)
        # ----------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # ==========================================================
        # LEFT SIDE — scrollable info + logs + summary
        # ==========================================================
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        splitter.addWidget(left_scroll)

        left_container = QWidget()
        left_scroll.setWidget(left_container)

        left_layout = QVBoxLayout(left_container)

        # ---------------- General Info Widgets ----------------
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

        # Buttons row
        btn_row = QHBoxLayout()
        self.action_btn = QPushButton("Action")
        self.run_btn = QPushButton("Run Day")
        btn_row.addWidget(self.action_btn)
        btn_row.addWidget(self.run_btn)
        left_layout.addLayout(btn_row)

        # Progress bar
        self.bar = QProgressBar()
        self.bar.setMaximum(TURNS_PER_DAY)
        left_layout.addWidget(self.bar)

        # ---------------- Turn Log ----------------
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(200)
        self.log_edit.setStyleSheet(
            "background-color: #111; color: #eee; font-family: monospace;"
        )
        left_layout.addWidget(self.log_edit)

        # ---------------- Day Summary ----------------
        self.summary_label = QLabel("Day summary will appear here.")
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        left_layout.addWidget(self.summary_label)

        # Stretch to push content top & scroll nicely
        left_layout.addStretch()

        # ==========================================================
        # RIGHT SIDE — scrollable graphs
        # ==========================================================
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        splitter.addWidget(right_scroll)

        right_container = QWidget()
        right_scroll.setWidget(right_container)

        right_layout = QVBoxLayout(right_container)

        # Main Graph
        self.sales_chart = FigureCanvasQTAgg(Figure(figsize=(6, 4)))
        self.ax = self.sales_chart.figure.subplots()
        right_layout.addWidget(self.sales_chart)

        # Future graphs can be added here:
        # right_layout.addWidget(another_graph_canvas)

        right_layout.addStretch()

        # ----------------------------------------------------------
        # Connect buttons
        # ----------------------------------------------------------
        self.action_btn.clicked.connect(self.open_action)
        self.run_btn.clicked.connect(self.run_day)

        # Initial update
        self.update_info()

    # ---------------- Morning Menu ----------------
    def open_action(self):
        dialog = Action(self.game)
        dialog.exec()
        self.update_info()

    # ---------------- Run Day ----------------
    def run_day(self):
        self.game.opening_cash = self.game.cash

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
        self.run_btn.setEnabled(True)
        self.action_btn.setEnabled(True)

    # ---------------- Per-Turn UI Update ----------------
    def on_tick(self, info: dict):
        turn = info["turn"]
        self.bar.setValue(turn + 1)

        clock = info["clock"]
        served = info["served"]
        lostQ = info["lost_queue"]
        lostS = info["lost_stock"]
        lostP = info["lost_patience"]
        qsize = info["queue_size"]
        cash = info["cash"]
        cash_delta = info["cash_change"]
        stock_changes = info["stock_changes"]

        # Stock changes
        stock_parts = []
        for ing, delta in stock_changes.items():
            sign = "" if delta < 0 else "+"
            stock_parts.append(f"{ing.name} {sign}{delta}")
        stock_str = ", ".join(stock_parts) if stock_parts else "—"

        line = (
            f"[{clock}] Q={qsize:2d}  "
            f"Served={served}  LostQ={lostQ}  LostS={lostS}  LostP={lostP}  "
            f"ΔCash={cash_delta:+.2f}  Cash=${cash:.2f}  "
            f"Stock: {stock_str}"
        )

        self.log_edit.appendPlainText(line)
        self.update_info()

    # ---------------- Day Finished ----------------
    def on_day_finished(self, summary: dict):
        wages = sum(e.wage for e in self.game.employees)
        rent = self.game.venue.rent
        ingredients = self.game.dailyIngredientCost
        ads = self.game.dailyAdSpend

        # total_expenses = wages + rent + ingredients + ads

        text = (
            f"<b>Day Summary</b><br>"
            f"<b>Opening Cash:</b> {self.game.opening_cash}<br>"
            f"--------------------------<br>"
            f"<b>Served:</b> {summary['served']}<br>"
            f"<b>Lost (queue):</b> {summary['lost_queue']}<br>"
            f"<b>Lost (stock):</b> {summary['lost_stock']}<br>"
            f"<b>Lost (patience):</b> {summary['lost_patience']}<br><br>"
            f"<b>Revenue:</b> ${summary['revenue']:.2f}<br><br>"
            f"<b>Expenses</b><br>"
            f" - Ingredients: ${ingredients:.2f}<br>"
            f" - Advertising: ${ads:.2f}<br>"
            f" - Wages:       ${wages:.2f}<br>"
            f" - Rent:        ${rent}<br>"
            f"<b>Total Expenses:</b> ${summary['expenses']:.2f}<br><br>"
            f"<b>Profit:</b> ${summary['profit']:.2f}<br>"
            f"<b>Cash End:</b> ${summary['cash_end']:.2f}<br>"
        )

        self.summary_label.setText(text)

        # Render graph
        self.render_hourly_sales_chart(summary["hour_sales"])
        self.update_info()

        # Reset counters
        self.game.dailyIngredientCost = 0
        self.game.dailyAdSpend = 0

    # ---------------- Info Panel Refresh ----------------
    def update_info(self):
        self.cash_label.setText(f"<b>Cash:</b> ${self.game.cash:.2f}")

        v = self.game.venue
        self.venue_label.setText(
            f"<b>Venue:</b> {v.name}  (Max line: {v.maxLine}, Foot traffic: {v.footTraffic}, Rent: ${v.rent})"
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
    # ---------------- Graph Renderer ----------------
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
            self.ax.set_xlabel("Hour of Day")
            self.ax.set_ylabel("Drinks Sold")
            self.ax.set_xticks(range(len(hours)))
            self.ax.set_xticklabels(hours)
            self.sales_chart.draw()
            return

        x = np.arange(len(hours))
        width = 0.8 / len(drink_names)

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

            # Values on bars
            self.ax.bar_label(
                rects,
                labels=[str(v) if v > 0 else "" for v in yvals],
                padding=2,
                fontsize=9,
                color="white",
            )
        total_sales = [sum(hour_sales[h].values()) for h in hours]
        max_height = max(max_height, max(total_sales))

        # Center line over grouped bars
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

        # Labels on line points
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