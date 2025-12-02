"""
Lightweight Tkinter GUI wrapper for GIQBobaGame.
Run `python GIQBobaGameWithGraphics.py` to launch.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from threading import Thread, Event
from time import sleep
import random
import textwrap
from config import WAGE_MULTIPLIER, MAX_QUEUE_DISPLAY

from GIQBobaGame import Game, TURNS_PER_DAY
from GIQBobaGame import Stand, Truck, Store  # for upgrade dialog
from GIQBobaGame import Drink, Staff as Employee, CUP_REGULAR, CUP_TALL, STRAW, SEAL

TURN_DELAY_MS = 1000  # real‑time delay between turns (0.3 s)

# --- UI scaling constants ---
RECT_W = 18   # width of one queue slot (scaled up from 12)

class GameGUI:
    def __init__(self, root: tk.Tk):
        # --- UI scaling ---
        import sys
        scale = 1.2 if sys.platform.startswith("win") else 1.5
        root.tk.call('tk', 'scaling', scale)
        tkfont.nametofont('TkDefaultFont').configure(size=14)
        tkfont.nametofont('TkFixedFont').configure(size=14)
        self.root = root
        root.title("Boba Tycoon GUI")

        # --- game state ---
        self.game = Game()
        self.morning_done = False

        # --- widgets ---
        self.cash_var = tk.StringVar()
        self.queue_var = tk.StringVar()
        # -------- Scrollable container --------
        scroll_canvas = tk.Canvas(root, borderwidth=0, highlightthickness=0)
        vbar = ttk.Scrollbar(root, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=vbar.set)
        # Bind mouse‑wheel / trackpad scrolling only to this canvas (not globally)
        def _on_mousewheel(event):
            # Windows / MacOS use event.delta, Linux uses Button‑4/5
            scroll = -1 if event.delta > 0 else 1
            scroll_canvas.yview_scroll(scroll, "units")
            return "break"  # prevent root from also scrolling
        scroll_canvas.bind("<MouseWheel>", _on_mousewheel)          # Windows / macOS
        scroll_canvas.bind("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))  # Linux up
        scroll_canvas.bind("<Button-5>", lambda e: scroll_canvas.yview_scroll( 1, "units"))  # Linux down
        vbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        # Frame INSIDE canvas that will hold all the UI widgets
        self.main_frame = tk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def _configure_scrollregion(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        self.main_frame.bind("<Configure>", _configure_scrollregion)

        tk.Label(self.main_frame, textvariable=self.cash_var,
                 font=("Helvetica", 14)).pack(pady=5)
        tk.Label(self.main_frame, textvariable=self.queue_var,
                 font=("Helvetica", 12)).pack()

        # Queue bar canvas
        self.queue_canvas = tk.Canvas(self.main_frame,
                                      width=MAX_QUEUE_DISPLAY * RECT_W,
                                      height=28,
                                      highlightthickness=0,
                                      bg=root.cget("bg"))
        self.queue_canvas.pack(pady=6)

        # Status panel (menu, stock, staff, ad)
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var,
                                     justify="left", font=("Courier New", 12), anchor="w")
        self.status_label.pack(pady=4)

        # Activity log (hidden until day starts)
        self.log_frame = tk.Frame(self.main_frame)
        tk.Label(self.log_frame, text="Activity Log").pack()
        self.log_text = tk.Text(self.log_frame, width=55, height=8, state="disabled",
                                font=("Courier New", 11),
                                bg=root.cget("bg"), relief="flat", borderwidth=1)
        self.log_text.pack(side="left")
        self.log_scroll = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll.set)
        self.log_scroll.pack(side="right", fill="y")
        # Keep hidden until simulation begins
        self.log_frame.pack_forget()
        self.log_visible = False

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Morning Menu",
                  command=self.open_morning_menu).grid(row=0, column=0, padx=5)
        self.run_btn = tk.Button(btn_frame, text="Run Day", command=self.start_day)
        self.run_btn.grid(row=0, column=1, padx=5)
        # Removed standalone "Upgrade Venue" button from main toolbar

        # Pause/Resume button
        self.pause_btn = tk.Button(btn_frame, text="Pause",
                                   command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=2, padx=5)

        # Step button (Next Turn)
        self.step_btn = tk.Button(btn_frame, text="Next Turn",
                                  command=self.step_once, state="disabled")
        self.step_btn.grid(row=0, column=3, padx=5)

        self.progress = ttk.Progressbar(self.main_frame, length=300, maximum=TURNS_PER_DAY)
        self.progress.pack(pady=10)

        # Daily summary label (updates after each day)
        self.summary_var = tk.StringVar(value="Day summary will appear here.")
        tk.Label(self.main_frame, textvariable=self.summary_var,
                 justify="left", font=("Courier New", 12)).pack(pady=6)

        self.refresh_labels()

        # Pause control state
        self.paused = False
        self.pause_event = Event()
        self.pause_event.set()  # initially unpaused

    # ---------- helper UI funcs ----------
    def refresh_labels(self):
        self.cash_var.set(f"Cash: ${self.game.cash:.2f}")
        q_len = len(self.game.venue.line)
        self.queue_var.set(f"Queue: {q_len}/{self.game.venue.maxLine}")
        # -- Queue bar drawing --
        self.queue_canvas.delete("all")
        bar_len = min(self.game.venue.maxLine, MAX_QUEUE_DISPLAY)
        filled  = min(len(self.game.venue.line), bar_len)
        canvas_w = MAX_QUEUE_DISPLAY * RECT_W
        start_x  = (canvas_w - bar_len * RECT_W) // 2

        self.queue_canvas.config(width=canvas_w)

        for i in range(bar_len):
            x0 = start_x + i * RECT_W
            color = "green" if i < filled else "lightgray"
            self.queue_canvas.create_rectangle(x0, 0, x0 + RECT_W, 28,
                                               fill=color, width=0)
        self.status_var.set(self.build_status_text())

    def build_status_text(self) -> str:
        lines = ["Menu:"]
        for d in self.game.menu:
            size_label = "Regular" if d.size == "regular" else "Tall"
            lines.append(f"  {d.name:20} ${d.basePrice:6.2f}  {size_label}")
        lines.append("\nStock:")
        for ing in self.game.ingredients:
            lines.append(f"  {ing.name:20} {self.game.stock.get(ing,0):4}")
        lines.append("\nEmployees:")
        for emp in self.game.employees:
            lines.append(f"  {emp.name:10} Capacity={emp.capacity} Charm={emp.charm} Wage=${emp.wage}")
        lines.append(f"\nAd Budget Today:  ${self.game.adBudget:.2f}")
        lines.append(f"Ad Boost Factor:   {self.game.adFactor*100:.0f}%")
        return "\n".join(lines)

    # ---------- Activity log helper ----------
    def log(self, message: str):
        """Append a new line to the activity log Text widget."""
        if not self.log_visible:
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.yview_moveto(1.0)  # auto-scroll to bottom

    @staticmethod
    def clock_from_turn(turn_idx: int) -> str:
        minutes = turn_idx * 15  # 15 minutes per turn
        hour = 8 + minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

    # ---------- callbacks ----------
    # ---------- Morning Menu ----------
    def open_morning_menu(self):
        mm = tk.Toplevel(self.root)
        mm.title("Morning Menu")
        mm.geometry("320x360")

        def close_mm():
            mm.destroy()
            self.set_morning_done()
        mm.protocol("WM_DELETE_WINDOW", close_mm)

        # --- scrollable container ---
        canvas = tk.Canvas(mm, borderwidth=0, highlightthickness=0)
        vbar   = ttk.Scrollbar(mm, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def _sync_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _sync_scroll)

        # Enable independent scrolling for this Morning Menu
        def _mm_wheel(event):
            scroll_dir = -1 if event.delta > 0 else 1
            canvas.yview_scroll(scroll_dir, "units")
            return "break"
        canvas.bind("<MouseWheel>", _mm_wheel)  # Win / macOS
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux up
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll( 1, "units"))  # Linux down

        tk.Label(inner, text=f"Day {self.game.day} ‑ Morning", font=("Helvetica", 12)).pack(pady=6)

        tk.Button(inner, text="Upgrade Venue", command=self.open_upgrade_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Hire Employees", command=self.hire_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Fire Employees", command=self.fire_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Add Drink", command=self.add_drink_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Edit Drink Price", command=self.edit_price_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Buy Stock", command=self.buy_stock_dialog)\
            .pack(fill="x", padx=20, pady=2)
        tk.Button(inner, text="Set Ad Budget", command=self.ad_budget_dialog)\
            .pack(fill="x", padx=20, pady=2)

        tk.Button(inner, text="Done", command=lambda: [mm.destroy(), self.set_morning_done()])\
            .pack(pady=10)

    # --- Hire employees ---
    def hire_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Hire Employees")

        first_names = ["Alex", "Jordan", "Casey", "Riley", "Taylor",
                       "Morgan", "Jamie", "Avery", "Sam", "Devon"]
        candidates = []
        name_pool = random.sample(first_names, 3)  # guarantee unique names
        for name in name_pool:
            cap  = random.randint(1, 3)
            charm = random.randint(0, 3)
            wage = cap * WAGE_MULTIPLIER + charm * 3 + random.randint(-5, 5)
            candidates.append(Employee(name, wage, cap, charm))

        tk.Label(dialog, text="Choose applicants to hire:", font=("Helvetica", 11)).pack(pady=4)
        lb = tk.Listbox(dialog, selectmode="multiple", width=40)
        for idx, cand in enumerate(candidates, 1):
            lb.insert("end", f"{idx}) {cand.name}  Capacity={cand.capacity}  Charm={cand.charm}  Wage=${cand.wage}")
        lb.pack(padx=10, pady=6)

        def hire_selected():
            sels = lb.curselection()
            for i in sels:
                cand = candidates[i]
                if cand.wage > self.game.cash:
                    proceed = messagebox.askyesno(
                        "Low Cash",
                        f"{cand.name}'s wage (${cand.wage}) exceeds your current cash "
                        f"(${self.game.cash:.2f}). Hire anyway?")
                    if not proceed:
                        continue
                self.game.employees.append(cand)
            self.refresh_labels()
            dialog.destroy()

        tk.Button(dialog, text="Hire Selected", command=hire_selected).pack(pady=6)

    # --- Fire employees ---
    def fire_dialog(self):
        if len(self.game.employees) <= 1:
            messagebox.showinfo("No staff", "Only owner employed.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Fire Employees")
        tk.Label(dialog, text="Select staff to fire:", font=("Helvetica", 11)).pack(pady=4)
        lb = tk.Listbox(dialog, selectmode="multiple", width=40)
        for idx, emp in enumerate(self.game.employees[1:], 1):
            lb.insert("end", f"{idx}) {emp.name}  Capacity={emp.capacity}  Charm={emp.charm}  Wage=${emp.wage}")
        lb.pack(padx=10, pady=6)

        def fire_selected():
            sels = sorted(lb.curselection(), reverse=True)
            for i in sels:
                self.game.employees.pop(i+1)  # +1 to skip owner
            self.refresh_labels()
            dialog.destroy()

        tk.Button(dialog, text="Fire Selected", command=fire_selected).pack(pady=6)

    # --- Add drink ---
    def add_drink_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("New Drink")

        name_var = tk.StringVar()
        price_var = tk.StringVar()
        size_var = tk.StringVar(value="regular")

        tk.Label(dlg, text="Drink name:").pack()
        tk.Entry(dlg, textvariable=name_var).pack()

        tk.Label(dlg, text="Base price ($):").pack()
        tk.Entry(dlg, textvariable=price_var).pack()

        size_frame = tk.Frame(dlg)
        size_frame.pack(pady=4)
        tk.Label(size_frame, text="Size:").pack(side="left")
        tk.Radiobutton(size_frame, text="Regular", variable=size_var, value="regular").pack(side="left")
        tk.Radiobutton(size_frame, text="Tall", variable=size_var, value="tall").pack(side="left")

        tk.Label(dlg, text="Select ingredients (ctrl‑click to multi‑select):").pack()
        # Exclude packaging items from ingredient list
        non_pack = [ing for ing in self.game.ingredients
                    if ing not in {CUP_REGULAR, CUP_TALL, STRAW, SEAL}]
        lb = tk.Listbox(dlg, selectmode="multiple", width=40, height=12)
        for idx, ing in enumerate(non_pack, 1):
            lb.insert("end", f"{idx}) {ing.name}")
        lb.pack()

        qty_var = tk.StringVar(value="1")

        tk.Label(dlg, text="Quantity for each selected ingredient:").pack()
        tk.Entry(dlg, textvariable=qty_var, width=5).pack()

        def add_drink():
            try:
                base_price = float(price_var.get())
                if base_price < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid", "Enter a non‑negative number for price.")
                return
            try:
                qty = int(qty_var.get())
                if qty <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid", "Qty must be positive integer.")
                return
            sels = lb.curselection()
            if not name_var.get().strip() or not sels:
                messagebox.showerror("Missing", "Provide name and at least one ingredient.")
                return
            recipe = {}
            for i in sels:
                ing = non_pack[i]
                recipe[ing] = qty
            self.game.menu.append(
                Drink(name_var.get().strip(), recipe, base_price, baseDesirability=5, size=size_var.get())
            )
            dlg.destroy()

        tk.Button(dlg, text="Add Drink", command=add_drink).pack(pady=6)

    # --- Edit price ---
    def edit_price_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit Drink Price")
        tk.Label(dlg, text="Select drink:", font=("Helvetica", 11)).pack()
        lb = tk.Listbox(dlg, width=40)
        for d in self.game.menu:
            lb.insert("end", f"{d.name} (${d.basePrice:.2f})")
        lb.pack(pady=4)
        price_var = tk.StringVar()
        tk.Label(dlg, text="New price:").pack()
        tk.Entry(dlg, textvariable=price_var).pack()

        def apply():
            sel = lb.curselection()
            if not sel:
                return
            try:
                new_price = float(price_var.get())
                if new_price < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid", "Price must be non‑negative.")
                return
            drink = self.game.menu[sel[0]]
            drink.setPrice(new_price)
            dlg.destroy()

        tk.Button(dlg, text="Apply", command=apply).pack(pady=6)

    # --- Buy stock ---
    def buy_stock_dialog(self):
        self.game.generate_offers()   # refresh offers
        dlg = tk.Toplevel(self.root)
        dlg.title("Buy Stock")
        
        # Ingredient selector
        tk.Label(dlg, text="Select ingredient:", font=("Helvetica", 11)).pack(pady=(10,0))
        lb = tk.Listbox(dlg, width=40)
        for ing in self.game.ingredients:
            lb.insert("end", ing.name)
        lb.pack(padx=10, pady=4)

        choice_var = tk.StringVar(value="retail")
        
        # Offer display
        offer_lbl = tk.Label(dlg, text="", justify="left", font=("Courier New", 11))
        offer_lbl.pack(pady=4)

        def show_offer(event=None):
            idxs = lb.curselection()
            if not idxs:
                offer_lbl.config(text="")
                return
            ing = self.game.ingredients[idxs[0]]
            off = self.game.offers[ing]
            bundle_small = off['bulk']['min'] // 4
            bundle_large = off['bulk']['min']
            cost_small  = round(bundle_small * off['retail']['unit'], 2)
            cost_large  = round(bundle_large * off['bulk']['unit'],   2)
            # Two-decimal formatting
            info = (
                f"Vendor 1: {bundle_small} units – ${cost_small:.2f}\n"
                f"Vendor 2: {bundle_large} units – ${cost_large:.2f}"
            )
            offer_lbl.config(text=info)

        lb.bind("<<ListboxSelect>>", show_offer)

        # Vendor radio buttons
        tier_frame = tk.Frame(dlg)
        tk.Label(tier_frame, text="Vendor:").pack(side="left")
        tk.Radiobutton(tier_frame, text="Vendor 1", variable=choice_var, value="retail").pack(side="left", padx=4)
        tk.Radiobutton(tier_frame, text="Vendor 2", variable=choice_var, value="bulk").pack(side="left", padx=4)
        tier_frame.pack(pady=4)

        show_offer()  # initial offer display

        def purchase():
            idxs = lb.curselection()
            if not idxs:
                return
            ing = self.game.ingredients[idxs[0]]
            off = self.game.offers[ing]
            bundle_small = off['bulk']['min'] // 4
            bundle_large = off['bulk']['min']
            tier = choice_var.get()
            qty  = bundle_large if tier == 'bulk' else bundle_small
            unit = off['bulk']['unit'] if tier == 'bulk' else off['retail']['unit']
            cost = round(qty * unit, 2)
            # Improved error grammar
            if cost > self.game.cash:
                messagebox.showerror(
                    "Cash",
                    f"Need ${cost:.2f} but you only have ${self.game.cash:.2f}."
                )
                return
            # Deduct and track
            self.game.cash -= cost
            self.game.dailyIngredientCost += cost
            self.game.stock[ing] += qty
            self.refresh_labels()
            # Refresh offer text for further purchases
            show_offer()

        # Buttons
        btn_frame = tk.Frame(dlg)
        tk.Button(btn_frame, text="Purchase", command=purchase).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Done",     command=dlg.destroy).pack(side="left")
        btn_frame.pack(pady=10)
    # --- Ad budget ---
    def ad_budget_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Set Ad Budget")
        val = tk.StringVar(value=str(self.game.adBudget))
        tk.Label(dlg, text=f"Cash available: ${self.game.cash:.2f}").pack(pady=3)
        tk.Entry(dlg, textvariable=val).pack()

        def apply():
            if not val.get().strip():
                amount = 0
            else:
                try:
                    amount = float(val.get())
                    if amount < 0: raise ValueError
                except ValueError:
                    messagebox.showerror("Invalid", "Enter non‑negative number.")
                    return
            # Just store the budget; deduct cash at start of the day
            self.game.adBudget = amount
            # Update boost factor immediately so preview is correct
            self.game.adFactor = self.game.calculateAdFactor()
            dlg.destroy()
            self.refresh_labels()

        tk.Button(dlg, text="Apply", command=apply).pack(pady=6)

    def set_morning_done(self):
        self.morning_done = True
        self.refresh_labels()

    def open_upgrade_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Upgrade Venue")
        tk.Label(win, text=f"Current: {self.game.venue.name}", font=("Helvetica", 12)).pack(pady=5)

        def try_upgrade(venue_cls, cost):
            if isinstance(self.game.venue, venue_cls):
                messagebox.showinfo("No change", "Already at that level.")
                return
            if cost > self.game.cash:
                messagebox.showerror("Cash",
                                     f"Need ${cost} to upgrade; you have ${self.game.cash:.2f}.")
                return
            self.game.cash -= cost
            self.game.venue = venue_cls()
            messagebox.showinfo("Upgraded",
                                f"You paid ${cost} and now have a {self.game.venue.name}.")
            win.destroy()
            self.refresh_labels()

        tk.Button(win, text="Stand  ($0)",     width=18,
                  command=lambda: try_upgrade(Stand, 0)).pack(pady=2)
        tk.Button(win, text="Truck  ($500)",   width=18,
                  command=lambda: try_upgrade(Truck, 500)).pack(pady=2)
        tk.Button(win, text="Store  ($1000)",  width=18,
                  command=lambda: try_upgrade(Store, 1000)).pack(pady=2)

    def start_day(self):
        if not self.morning_done:
            messagebox.showwarning("Morning Menu Required",
                                   "Please complete the Morning Menu first.")
            return
        # Deduct advertising budget at the start of the day
        if self.game.adBudget > 0:
            if self.game.adBudget > self.game.cash:
                messagebox.showerror("Cash",
                                     f"Cannot run day: Ad budget ${self.game.adBudget:.2f} "
                                     f"exceeds cash on hand (${self.game.cash:.2f}).")
                return
            self.game.cash -= self.game.adBudget
            self.game.dailyAdSpend = self.game.adBudget
        self.progress['value'] = 0
        # stats for daily summary
        self.day_served = 0
        self.day_lostQ = 0
        self.day_lostPat = 0
        self.day_revenue = 0.0
        self.day_lostStock = 0
        # Track opening cash at start of day
        self.opening_cash = self.game.cash
        # Bankruptcy flag for thread
        self.terminated = False
        # Disable Run Day while simulation is active
        self.run_btn.config(state="disabled")
        # Enable control buttons
        self.pause_btn.config(state="normal", text="Pause")
        self.step_btn.config(state="disabled")
        self.paused = False
        self.pause_event.set()
        # Show log above status panel if not already visible
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        if not self.log_visible:
            # Show log above status panel
            self.log_frame.pack(before=self.status_label, pady=4)
            self.log_visible = True
        Thread(target=self._day_thread, daemon=True).start()

    def _day_thread(self):
        for turn in range(TURNS_PER_DAY):
            if getattr(self, "terminated", False):
                break
            # Wait if paused; pause_event cleared means pause
            if self.paused:
                self.pause_event.wait()
                if self.terminated:
                    break
            served, lostQ, lostStock, lostPat = self.game.single_turn()
            self.day_served   += served
            self.day_lostQ    += lostQ
            self.day_lostPat  += lostPat
            self.day_lostStock += lostStock
            # Compute average price for this turn for log
            avg_price = served and (self.game.cash - self.opening_cash) / max(1, self.day_served) or 0
            # Log activity for this turn, one entry per event
            clock_str = self.clock_from_turn(turn)
            if served:
                self.root.after(0, self.log,
                                f"{clock_str}  Served {served} customer(s) [+${served * avg_price:.2f}]")
            if lostQ:
                self.root.after(0, self.log,
                                f"{clock_str}  {lostQ} left – queue full")
            if lostPat:
                self.root.after(0, self.log,
                                f"{clock_str}  {lostPat} left – patience ran out")
            if lostStock:
                self.root.after(0, self.log,
                                f"{clock_str}  {lostStock} left – drink out of stock")
            self.root.after(0, self._tick_ui, turn + 1)
            sleep(TURN_DELAY_MS / 1000)
        self.root.after(0, self._day_finished)

    # --- scheduled on main thread ---
    def _tick_ui(self, turn):
        self.progress['value'] = turn
        self.refresh_labels()
        if self.game.cash < 0 and not getattr(self, "terminated", False):
            self.terminated = True
            self.pause_btn.config(state="disabled")
            self.step_btn.config(state="disabled")
            self.run_btn.config(state="disabled")
            if self.log_visible:
                self.log_frame.pack_forget()
                self.log_visible = False
            messagebox.showerror("Bankruptcy",
                                 f"You ran out of cash (${self.game.cash:.2f}). Game over.")
            self.root.quit()
            return

    def _day_finished(self):
        # Costs that have NOT yet been deducted today
        wagesCost = sum(emp.wage for emp in self.game.employees)
        rentCost  = self.game.venue.rent

        # Profit so far (ingredients + ads already deducted during morning)
        profit_before_wages = self.game.cash - self.opening_cash

        # Deduct wages and rent from cash
        self.game.cash -= (wagesCost + rentCost)
        profit = profit_before_wages - wagesCost - rentCost

        revenue_est = (self.game.cash - self.opening_cash) + wagesCost + rentCost

        self.refresh_labels()
        summary = (
            f"Day {self.game.day} Summary\n"
            f"-------------------------------\n"
            f"{'Revenue':<16}: ${revenue_est:.2f}\n"
            f"{'Wages':<16}: -${wagesCost:.2f}\n"
            f"{'Rent':<16}: -${rentCost:.2f}\n"
            f"{'Ingredients':<16}: -${self.game.dailyIngredientCost:.2f}\n"
            f"{'Advertising':<16}: -${self.game.dailyAdSpend:.2f}\n"
            f"{'Profit':<16}: ${profit:.2f}\n"
            f"\n{'Served':<16}: {self.day_served}\n"
            f"{'Lost (queue)':<16}: {self.day_lostQ}\n"
            f"{'Lost (stock)':<16}: {self.day_lostStock}\n"
            f"{'Lost (patience)':<16}: {self.day_lostPat}\n"
            f"{'Cash end':<16}: ${self.game.cash:.2f}"
        )
        self.summary_var.set(summary)

        # --- make sure the *reset* happens AFTER the summary so today's costs show up ---
        self.game.dailyIngredientCost = 0
        self.game.dailyAdSpend        = 0

        # Bankruptcy check post-costs
        if self.game.cash < 0:
            messagebox.showerror("Bankruptcy",
                                 f"You ran out of cash (${self.game.cash:.2f}). Game over.")
            self.root.quit()
            return

        # Disable control buttons
        self.pause_btn.config(state="disabled", text="Pause")
        self.step_btn.config(state="disabled")

        # Hide activity log at end of day
        if self.log_visible:
            self.log_frame.pack_forget()
            self.log_visible = False

        # Re-enable Run Day for next cycle
        self.run_btn.config(state="normal")

        # Prepare for next day
        self.morning_done = False
        self.game.day += 1

    def toggle_pause(self):
        if not self.paused:
            # Enter pause mode
            self.paused = True
            self.pause_btn.config(text="Resume")
            self.step_btn.config(state="normal")
            self.pause_event.clear()
        else:
            # Resume automatic mode
            self.paused = False
            self.pause_btn.config(text="Pause")
            self.step_btn.config(state="disabled")
            self.pause_event.set()

    def step_once(self):
        """Advance exactly one turn when paused."""
        if self.paused:
            # Allow one iteration to proceed
            self.pause_event.set()
            # Immediately clear again for next click
            self.pause_event.clear()

# --------------- launch ---------------
if __name__ == "__main__":
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()