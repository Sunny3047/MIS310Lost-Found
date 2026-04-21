# home_screen.py - Home / Search Screen

import tkinter as tk
from constants import BG, ACCENT, BTN_SEC_BG, FONT_HEAD, FONT_BODY, FONT_SMALL, PAD
from constants import make_banner, styled_btn, format_row
import database as db


class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self._build()

    def _build(self):
        make_banner(self, "🎓  LOST & FOUND — CCSU Campus Application")

        # Mode selector
        mode_frm = tk.Frame(self, bg=BG)
        mode_frm.pack(fill="x", padx=PAD*2, pady=(PAD, 0))
        tk.Label(mode_frm, text="Mode:", font=FONT_HEAD, bg=BG).pack(side="left")
        self.mode_var = tk.StringVar(value="Lost")
        for val, label in [("Lost", "  I Lost an Item  "), ("Found", "  I Found an Item  ")]:
            tk.Radiobutton(mode_frm, text=label, variable=self.mode_var, value=val,
                           font=FONT_BODY, bg=BG, activebackground=BG).pack(side="left", padx=8)

        # Search bar
        search_frm = tk.Frame(self, bg=BG)
        search_frm.pack(fill="x", padx=PAD*2, pady=(6, 0))
        tk.Label(search_frm, text="Search:", font=FONT_HEAD, bg=BG).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frm, textvariable=self.search_var,
                                     font=FONT_BODY, width=45)
        self.search_entry.pack(side="left", padx=(8, 4))
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        # Action buttons
        btn_frm = tk.Frame(self, bg=BG)
        btn_frm.pack(fill="x", padx=PAD*2, pady=8)
        styled_btn(btn_frm, "🔍  Search / Find Match", self._do_search).pack(side="left", padx=4)
        styled_btn(btn_frm, "📋  View All Reports", self._view_all,
                   bg=BTN_SEC_BG).pack(side="left", padx=4)

        # Results label
        tk.Label(self, text="Results:", font=FONT_HEAD, bg=BG, anchor="w")\
            .pack(fill="x", padx=PAD*2)

        # Results listbox
        list_frm = tk.Frame(self, bg=BG)
        list_frm.pack(fill="both", expand=True, padx=PAD*2, pady=4)

        scrollbar = tk.Scrollbar(list_frm)
        scrollbar.pack(side="right", fill="y")

        self.results_box = tk.Listbox(list_frm, font=FONT_BODY, yscrollcommand=scrollbar.set,
                                      selectbackground=ACCENT, selectforeground="white",
                                      height=12, bg="white", relief="solid", bd=1)
        self.results_box.pack(fill="both", expand=True)
        scrollbar.config(command=self.results_box.yview)
        self.results_box.bind("<Double-Button-1>", self._on_result_select)

        tk.Label(self, text="(double-click a result to see details)",
                 font=FONT_SMALL, bg=BG, fg="gray").pack(anchor="w", padx=PAD*2)

        # Bottom navigation
        nav_frm = tk.Frame(self, bg=BG)
        nav_frm.pack(fill="x", padx=PAD*2, pady=PAD)
        styled_btn(nav_frm, "📝  Report a Lost Item",
                   lambda: self.controller.show_report("Lost")).pack(side="left", padx=4)
        styled_btn(nav_frm, "📝  Report a Found Item",
                   lambda: self.controller.show_report("Found")).pack(side="left", padx=4)

    # Search and display results
    def _do_search(self):
        keyword = self.search_var.get().strip()
        mode = self.mode_var.get()
        results = db.search_reports(keyword, report_type=mode)
        self._display_results(results)

    def _view_all(self):
        results = db.get_all_reports()
        self._display_results(results)

    def _display_results(self, results):
        self.results_box.delete(0, tk.END)
        self._current_results = results
        if not results:
            self.results_box.insert(tk.END, "  No results found.")
        else:
            for r in results:
                self.results_box.insert(tk.END, "  " + format_row(r))

    def _on_result_select(self, _event):
        sel = self.results_box.curselection()
        if not sel or not hasattr(self, "_current_results"):
            return
        idx = sel[0]
        if idx >= len(self._current_results):
            return
        record = self._current_results[idx]
        self.controller.show_match([record], detail=True)

    # Called when screen becomes active
    def refresh(self):
        self.results_box.delete(0, tk.END)
