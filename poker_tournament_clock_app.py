import tkinter as tk
from tkinter import ttk, messagebox


class PokerTournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Tournament Manager")
        self.root.geometry("1920x1080")
        self.root.minsize(850, 600)

        self.players = []
        self.levels = [
            {"small": 25, "big": 50, "ante": 0, "minutes": 15},
            {"small": 50, "big": 100, "ante": 0, "minutes": 15},
            {"small": 75, "big": 150, "ante": 0, "minutes": 15},
            {"small": 100, "big": 200, "ante": 0, "minutes": 15},
            {"type": "break", "minutes": 5},
            {"small": 150, "big": 300, "ante": 0, "minutes": 20},
            {"small": 200, "big": 400, "ante": 0, "minutes": 20},
            {"small": 250, "big": 500, "ante": 0, "minutes": 20},
            {"type": "break", "minutes": 5},
            {"small": 300, "big": 600, "ante": 0, "minutes": 20},
            {"small": 400, "big": 800, "ante": 0, "minutes": 20},
            {"small": 500, "big": 1000, "ante": 0, "minutes": 20},
            {"type": "break", "minutes": 5},
            {"small": 700, "big": 1400, "ante": 0, "minutes": 20},
            {"small": 1000, "big": 2000, "ante": 0, "minutes": 20},
            {"small": 1500, "big": 3000, "ante": 0, "minutes": 20},
            {"type": "break", "minutes": 5},
            {"small": 2000, "big": 4000, "ante": 0, "minutes": 20},
            {"small": 3000, "big": 6000, "ante": 0, "minutes": 20},
            {"small": 4000, "big": 8000, "ante": 0, "minutes": 60}
        ]
        self.current_level = 0
        self.seconds_left = self.levels[0]["minutes"] * 60
        self.timer_running = False
        self.timer_job = None

        self.buy_in_var = tk.StringVar(value="10")
        self.rebuy_var = tk.StringVar(value="10")
        self.currency_var = tk.StringVar(value="£")
        self.player_name_var = tk.StringVar()
        self.small_var = tk.StringVar()
        self.big_var = tk.StringVar()
        self.ante_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="15")
        self.last_rebuy_level = 13

        self._build_ui()
        self._refresh_all()
        self._update_clock_display()

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Big.TLabel", font=("Segoe UI", 75, "bold"))
        style.configure("Metric.TLabel", font=("Segoe UI", 45, "bold"))
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 15))
        style.configure("Treeview.Heading", font=("Segoe UI", 15, "bold"))
        style.configure("Next.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("NextTitle.TLabel", font=("Segoe UI", 16, "bold"))

        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="POKER TOURNAMENT", style="Title.TLabel").pack(side="left")
        pot_frame = ttk.Frame(header)
        pot_frame.pack(side="right")

        self.pot_label = ttk.Label(
            pot_frame,
            text="Prize pot: £0",
            style="Metric.TLabel"
        )
        self.pot_label.pack()

        ttk.Button(
            header,
            text="Reset Tournament",
            command=self.reset_tournament
        ).pack(side="right", padx=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.players_tab = ttk.Frame(self.notebook, padding=14)
        self.blinds_tab = ttk.Frame(self.notebook, padding=14)
        self.clock_tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.players_tab, text="Players & Rebuys")
        self.notebook.add(self.blinds_tab, text="Blind Levels")
        self.notebook.add(self.clock_tab, text="Tournament Clock")

        self._build_players_tab()
        self._build_blinds_tab()
        self._build_clock_tab()

    def _build_players_tab(self):
        top_frame = ttk.Frame(self.players_tab)
        top_frame.pack(fill="x", pady=(0, 12))

        # ADD A PLAYER - LEFT
        add_frame = ttk.LabelFrame(top_frame, text="Add a player", padding=10)
        add_frame.pack(side="left", fill="y", padx=(0, 10))

        name_entry = ttk.Entry(add_frame, textvariable=self.player_name_var, width=28)
        name_entry.pack(side="left", padx=(0, 8))
        name_entry.bind("<Return>", lambda _event: self.add_player())

        ttk.Button(add_frame, text="Add player", command=self.add_player).pack(side="left")

        # TOURNAMENT SETTINGS - RIGHT
        settings = ttk.LabelFrame(top_frame, text="Tournament settings", padding=10)
        settings.pack(side="left", fill="x", expand=True)

        ttk.Label(settings, text="Buy-in (£)").grid(row=0, column=0, padx=(0, 6), sticky="w")
        ttk.Entry(settings, textvariable=self.buy_in_var, width=10).grid(row=0, column=1, padx=(0, 18))
        ttk.Label(settings, text="Rebuy (£)").grid(row=0, column=2, padx=(0, 6), sticky="w")
        ttk.Entry(settings, textvariable=self.rebuy_var, width=10).grid(row=0, column=3, padx=(0, 18))
        ttk.Button(settings, text="Update pot", command=self._refresh_pot).grid(row=0, column=4)

        list_frame = ttk.Frame(self.players_tab)
        list_frame.pack(fill="x", expand=False)
        columns = ("name", "status", "rebuys", "entries")
        self.player_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse", height=10)
        for col, heading, width in [
            ("name", "Player", 300), ("status", "Status", 150),
            ("rebuys", "Rebuys", 120), ("entries", "Total entries", 140)
        ]:
            self.player_tree.heading(col, text=heading)
            self.player_tree.column(col, width=width, anchor="center" if col != "name" else "w")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.player_tree.yview)
        self.player_tree.configure(yscrollcommand=scrollbar.set)
        self.player_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actions = ttk.Frame(self.players_tab)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Add rebuy to selected", command=self.add_rebuy).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Knock out selected", command=self.knock_out).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Reinstate selected", command=self.reinstate).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Remove selected", command=self.remove_player).pack(side="right")

        self.players_summary = ttk.Label(self.players_tab, text="")
        self.players_summary.pack(anchor="w", pady=(10, 0))

    def _build_blinds_tab(self):
        form = ttk.LabelFrame(self.blinds_tab, text="Add a blind level", padding=10)
        form.pack(fill="x", pady=(0, 12))

        fields = [
            ("Small blind", self.small_var), ("Big blind", self.big_var),
            ("Ante", self.ante_var), ("Minutes", self.minutes_var)
        ]
        for index, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=index * 2, padx=(0, 5), sticky="w")
            ttk.Entry(form, textvariable=variable, width=10).grid(row=0, column=index * 2 + 1, padx=(0, 14))
        ttk.Button(form, text="Add level", command=self.add_level).grid(row=0, column=8)

        table_frame = ttk.Frame(self.blinds_tab)
        table_frame.pack(fill="both", expand=True)
        cols = ("level", "small", "big", "ante", "minutes")
        self.level_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        headings = [("level", "Level"), ("small", "Small blind"), ("big", "Big blind"),
                    ("ante", "Ante"), ("minutes", "Duration (mins)")]
        for col, heading in headings:
            self.level_tree.heading(col, text=heading)
            self.level_tree.column(col, width=150, anchor="center")
        self.level_tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.level_tree.yview)
        self.level_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        actions = ttk.Frame(self.blinds_tab)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Move up", command=lambda: self.move_level(-1)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Move down", command=lambda: self.move_level(1)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Delete selected", command=self.delete_level).pack(side="left")
        ttk.Label(actions, text="Select a level, then use Move up/down to change the order.",
                  foreground="#555").pack(side="right")

    def _build_clock_tab(self):
        # Two-column layout: clock on the left, payouts on the right
        self.clock_tab.columnconfigure(0, weight=3)
        self.clock_tab.columnconfigure(1, weight=2)
        self.clock_tab.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self.clock_tab)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right_frame = ttk.LabelFrame(
            self.clock_tab,
            text="Prize payouts",
            padding=12
        )
        right_frame.grid(row=0, column=1, sticky="nsew")

        # CURRENT LEVEL
        current = ttk.LabelFrame(left_frame, text="Current level", padding=18)
        current.pack(fill="x", pady=(0, 14))

        self.level_title = ttk.Label(
            current,
            text="Level 1",
            style="Title.TLabel"
        )
        self.level_title.pack()

        self.blind_display = ttk.Label(
            current,
            text="25 / 50",
            style="Metric.TLabel",
            wraplength=650,
            justify="center"
        )
        self.blind_display.pack(pady=(8, 2))

        self.clock_display = ttk.Label(
            current,
            text="15:00",
            style="Big.TLabel"
        )
        self.clock_display.pack(pady=(8, 0))

        # NEXT BLIND LEVEL
        next_frame = ttk.LabelFrame(
            left_frame,
            text="Next blind level",
            padding=10
        )
        next_frame.pack(fill="x", pady=(0, 10))

        self.next_blind_display = ttk.Label(
            next_frame,
            text="50 / 100",
            style="Next.TLabel",
            foreground="#666666"
        )
        self.next_blind_display.pack()

        # TIMER CONTROLS
        controls = ttk.Frame(left_frame)
        controls.pack(pady=8)

        self.start_button = ttk.Button(
            controls,
            text="Start",
            command=self.toggle_timer,
            width=14
        )
        self.start_button.pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Reset level timer",
            command=self.reset_timer
        ).pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Next level →",
            command=self.next_level
        ).pack(side="left", padx=5)

        self.level_progress = ttk.Label(left_frame, text="")
        self.level_progress.pack(pady=(14, 0))

        ttk.Label(
            left_frame,
            text="The clock automatically moves to the next level when the countdown reaches zero.",
            foreground="#555",
            wraplength=430
        ).pack(pady=(8, 0))

        # PAYOUT SUMMARY
        self.payout_summary = ttk.Label(
            right_frame,
            text="Add players to calculate payouts.",
            justify="left"
        )
        self.payout_summary.pack(anchor="w", pady=(0, 12))

        # PAYOUT TABLE
        payout_columns = ("place", "share", "prize")

        self.payout_tree = ttk.Treeview(
            right_frame,
            columns=payout_columns,
            show="headings",
            height=7
        )

        self.payout_tree.heading("place", text="Place")
        self.payout_tree.heading("share", text="Share")
        self.payout_tree.heading("prize", text="Payout")

        self.payout_tree.column("place", width=85, anchor="center")
        self.payout_tree.column("share", width=75, anchor="center")
        self.payout_tree.column("prize", width=110, anchor="e")
        self.payout_tree.pack(fill="x", expand=False)

        ttk.Label(
            right_frame,
            text=(
                "Payout structure adjusts automatically to the number "
                "of entries. Prizes are rounded to £5, with any rounding "
                "difference added to first place."
            ),
            foreground="#555",
            wraplength=260,
            justify="left"
        ).pack(anchor="w", pady=(12, 0))

        # REBUY COUNTDOWN
        self.rebuy_countdown_label = ttk.Label(
            right_frame,
            text="Rebuys close in 10 levels",
            style="Next.TLabel",
            foreground="#666666"
        )
        self.rebuy_countdown_label.pack(anchor="w", pady=(15, 0))

    # Players
    def add_player(self):
        name = self.player_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Enter a player's name first.")
            return
        if any(p["name"].casefold() == name.casefold() for p in self.players):
            messagebox.showwarning("Already added", "That player is already on the list.")
            return
        self.players.append({"name": name, "rebuys": 0, "active": True})
        self.player_name_var.set("")
        self._refresh_players()
        self._refresh_pot()

    def _selected_player(self):
        selection = self.player_tree.selection()
        if not selection:
            messagebox.showinfo("Select a player", "Please select a player from the list first.")
            return None
        index = int(selection[0])
        if index >= len(self.players):
            return None
        return index

    def add_rebuy(self):
        grace_seconds = 5 * 60

        if (
            self.current_level > self.last_rebuy_level
            or (
                self.current_level == self.last_rebuy_level
                and self.seconds_left <= 0
                and grace_seconds <= 0
            )
        ):
            messagebox.showwarning(
                "Rebuys Closed",
                "The rebuy period has ended."
            )
            return

        index = self._selected_player()
        if index is None:
            return
        if not self.players[index]["active"]:
            messagebox.showwarning("Player is out", "Reinstate the player before recording another rebuy.")
            return
        self.players[index]["rebuys"] += 1
        self._refresh_players()
        self._refresh_pot()
        self.player_tree.selection_set(str(index))

    def knock_out(self):
        index = self._selected_player()
        if index is None:
            return
        if not self.players[index]["active"]:
            messagebox.showinfo("Already out", "This player has already been knocked out.")
            return
        name = self.players[index]["name"]
        if messagebox.askyesno("Confirm knockout", f"Knock out {name}?"):
            self.players[index]["active"] = False
            self._refresh_players()
            self._refresh_pot()

    def reinstate(self):
        index = self._selected_player()
        if index is None:
            return
        self.players[index]["active"] = True
        self._refresh_players()
        self._refresh_pot()
        self.player_tree.selection_set(str(index))

    def remove_player(self):
        index = self._selected_player()
        if index is None:
            return
        name = self.players[index]["name"]
        if messagebox.askyesno("Remove player", f"Remove {name} and their entries from the tournament?"):
            del self.players[index]
            self._refresh_players()
            self._refresh_pot()

    def _refresh_players(self):
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        for i, player in enumerate(self.players):
            status = "Playing" if player["active"] else "Knocked out"
            entries = 1 + player["rebuys"]
            self.player_tree.insert("", "end", iid=str(i),
                                    values=(player["name"], status, player["rebuys"], entries))
        playing = sum(1 for p in self.players if p["active"])
        self.players_summary.config(text=f"{playing} still playing  •  {len(self.players)} total players")

    # Prize pot
    def _money_value(self, variable, label):
        try:
            value = float(variable.get())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            raise ValueError(f"{label} must be a valid amount of 0 or more.")

    def _refresh_pot(self):
        try:
            buy_in = self._money_value(self.buy_in_var, "Buy-in")
            rebuy_cost = self._money_value(self.rebuy_var, "Rebuy")
        except ValueError as error:
            self.pot_label.config(text=str(error))
            self.payout_summary.config(text="Check your buy-in and rebuy amounts.")
            for item in self.payout_tree.get_children():
                self.payout_tree.delete(item)
            return

        initial_entries = len(self.players)
        total_rebuys = sum(p["rebuys"] for p in self.players)

        total_entries = initial_entries + total_rebuys
        pot = initial_entries * buy_in + total_rebuys * rebuy_cost

        self.pot_label.config(
            text=f"Prize pot: {self.currency_var.get()}{pot:,.2f}"
        )

        self.players_summary.config(
            text=f"{sum(1 for p in self.players if p['active'])} still playing  •  "
                 f"{len(self.players)} total players  •  {total_rebuys} rebuys"
        )

        self._refresh_payouts(pot, total_entries, total_rebuys)


    def _refresh_payouts(self, pot, total_entries, total_rebuys):
        # Clear the previous payout table
        for item in self.payout_tree.get_children():
            self.payout_tree.delete(item)

        if total_entries == 0 or pot <= 0:
            self.payout_summary.config(
                text="Add players to calculate payouts."
            )
            return

        # Choose the number of paid places and their percentages
        if total_entries <= 5:
            percentages = [100]
        elif total_entries <= 10:
            percentages = [65, 35]
        elif total_entries <= 20:
            percentages = [55, 30, 15]
        elif total_entries <= 30:
            percentages = [45, 30, 15, 10]
        else:
            percentages = [40, 25, 15, 12, 8]

        # Round an amount to the nearest £5
        def round_to_five(amount):
            return int(amount / 5 + 0.5) * 5

        # Calculate each payout
        payouts = [
            round_to_five(pot * percentage / 100)
            for percentage in percentages
        ]

        # Adjust first place so the payouts add up exactly to the pot
        payouts[0] = round(pot - sum(payouts[1:]), 2)

        # Update the summary
        self.payout_summary.config(
            text=(
                f"Total entries: {total_entries}\n"
                f"Unique players: {len(self.players)}\n"
                f"Rebuys: {total_rebuys}\n"
                f"Prize pot: £{pot:,.2f}\n"
                f"Paid places: {len(percentages)}"
            )
        )

        # Fill the payout table
        for index, (percentage, payout) in enumerate(
            zip(percentages, payouts), start=1
        ):
            self.payout_tree.insert(
                "",
                "end",
                values=(
                    f"{index}{'st' if index == 1 else 'nd' if index == 2 else 'rd' if index == 3 else 'th'}",
                    f"{percentage}%",
                    f"£{payout:,.2f}"
                )
            )

    # Blind levels
    def add_level(self):
        try:
            small = int(self.small_var.get())
            big = int(self.big_var.get())
            ante = int(self.ante_var.get())
            minutes = int(self.minutes_var.get())
            if small < 0 or big <= 0 or ante < 0 or minutes <= 0 or small > big:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid level", "Enter whole numbers. Big blind and minutes must be above 0; small blind cannot exceed big blind.")
            return
        self.levels.append({"small": small, "big": big, "ante": ante, "minutes": minutes})
        self._refresh_levels()
        if len(self.levels) == 1:
            self.current_level = 0
            self.reset_timer()
        self.small_var.set("")
        self.big_var.set("")
        self.ante_var.set("0")
        self.minutes_var.set("15")

    def _selected_level(self):
        selection = self.level_tree.selection()
        if not selection:
            messagebox.showinfo("Select a level", "Please select a blind level first.")
            return None
        return int(selection[0])

    def move_level(self, direction):
        index = self._selected_level()
        if index is None:
            return
        new_index = index + direction
        if not 0 <= new_index < len(self.levels):
            return
        self.levels[index], self.levels[new_index] = self.levels[new_index], self.levels[index]
        if self.current_level == index:
            self.current_level = new_index
        elif self.current_level == new_index:
            self.current_level = index
        self._refresh_levels()
        self.level_tree.selection_set(str(new_index))
        self._update_clock_display()

    def delete_level(self):
        index = self._selected_level()
        if index is None:
            return
        if len(self.levels) == 1:
            messagebox.showwarning("Cannot delete", "Keep at least one blind level.")
            return
        del self.levels[index]
        if index < self.current_level:
            self.current_level -= 1
        elif index == self.current_level:
            self.current_level = min(self.current_level, len(self.levels) - 1)
            self.seconds_left = self.levels[self.current_level]["minutes"] * 60
        self._refresh_levels()
        self._update_clock_display()

    def _refresh_levels(self):
        for item in self.level_tree.get_children():
            self.level_tree.delete(item)

        for i, level in enumerate(self.levels):

            if level.get("type") == "break":
                values = (i + 1, "BREAK", "—", "—", level["minutes"])
            else:
                values = (
                    i + 1,
                    level["small"],
                    level["big"],
                    level["ante"],
                    level["minutes"]
                )

            self.level_tree.insert(
                "",
                "end",
                iid=str(i),
                values=values
            )

        self._update_clock_display()

    # Tournament clock
    def toggle_timer(self):
        if self.timer_running:
            self._stop_timer()
        else:
            if not self.levels:
                return
            self.timer_running = True
            self.start_button.config(text="Pause")
            self._tick()

    def _stop_timer(self):
        self.timer_running = False
        self.start_button.config(text="Start")
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def _tick(self):
        self._update_clock_display()
        if not self.timer_running:
            return
        if self.seconds_left <= 0:
            if self.current_level < len(self.levels) - 1:
                self.current_level += 1
                self.seconds_left = self.levels[self.current_level]["minutes"] * 60
            else:
                self._stop_timer()
                messagebox.showinfo("Tournament levels complete", "You have reached the final blind level.")
                self._update_clock_display()
                return
        else:
            self.seconds_left -= 1
        self.timer_job = self.root.after(1000, self._tick)

    def reset_timer(self):
        self._stop_timer()
        if self.levels:
            self.seconds_left = self.levels[self.current_level]["minutes"] * 60
        self._update_clock_display()

    def next_level(self):
        self._stop_timer()
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            self.seconds_left = self.levels[self.current_level]["minutes"] * 60
        else:
            messagebox.showinfo("Final level", "You are already on the final blind level.")
        self._update_clock_display()

    
    def _update_clock_display(self):
        if not hasattr(self, "level_title"):
            return

        if not self.levels:
            self.level_title.config(text="No blind levels")
            self.blind_display.config(text="Add a level in the Blind Levels tab")
            self.clock_display.config(text="--:--")
            self.level_progress.config(text="")
            self.next_blind_display.config(text="No upcoming level")
            return

        self.current_level = max(0, min(self.current_level, len(self.levels) - 1))

        level = self.levels[self.current_level]

        mins, secs = divmod(max(0, self.seconds_left), 60)

        self.level_title.config(text=f"LEVEL {self.current_level + 1}")

        if level.get("type") == "break":
            self.blind_display.config(text="break time - go grab a cold one")
        else:
            if level["ante"] > 0:
                current_text = (
                    f"{level['small']:,} / {level['big']:,} "
                    f"| Ante {level['ante']:,}"
                )
            else:
                current_text = f"{level['small']:,} / {level['big']:,}"

            self.blind_display.config(text=current_text)

        self.clock_display.config(text=f"{mins:02d}:{secs:02d}")

        self.level_progress.config(
            text=f"Level {self.current_level + 1} of {len(self.levels)}"
        )

        # Update next blind level
        next_index = self.current_level + 1

        if next_index < len(self.levels):
            next_level = self.levels[next_index]

            if next_level.get("type") == "break":
                next_text = f"BREAK — {next_level['minutes']} minutes"
            else:
                if next_level["ante"] > 0:
                    next_text = (
                        f"{next_level['small']:,} / "
                        f"{next_level['big']:,} | "
                        f"Ante {next_level['ante']:,}"
                    )
                else:
                    next_text = (
                        f"{next_level['small']:,} / {next_level['big']:,}"
                    )
        else:
            next_text = "Tournament finished"

        self.next_blind_display.config(text=next_text)
        self._update_rebuy_countdown()

    def _update_rebuy_countdown(self):
        if self.current_level < self.last_rebuy_level:
            total_seconds = max(0, self.seconds_left)

            # Add the full duration of every remaining level
            for level_index in range(self.current_level + 1, self.last_rebuy_level):
                total_seconds += self.levels[level_index]["minutes"] * 60

            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            self.rebuy_countdown_label.config(
                text=f"Rebuys close in {hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        else:
            self.rebuy_countdown_label.config(text="REBUYS CLOSED")
    
    def reset_tournament(self):
        confirm = messagebox.askyesno(
            "Reset Tournament",
            "Are you sure you want to reset the tournament?\n\n"
            "All players, rebuys and tournament progress will be cleared.\n"
            "Your blind levels will be kept."
        )

        if not confirm:
            return

        # Stop the clock
        self._stop_timer()

        # Clear all players
        self.players.clear()

        # Reset clock to Level 1
        self.current_level = 0
        self.seconds_left = self.levels[0]["minutes"] * 60

        # Refresh the app
        self._refresh_all()
        self._update_clock_display()

        # Return to Players tab
        self.notebook.select(self.players_tab)

        messagebox.showinfo(
            "Tournament Reset",
            "Ready for a new poker tournament!"
        )
    
    def _refresh_all(self):
        self._refresh_players()
        self._refresh_levels()
        self._refresh_pot()


if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTournamentApp(root)
    root.mainloop()
