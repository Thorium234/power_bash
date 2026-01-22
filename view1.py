import tkinter as tk
from tkinter import ttk


class FinderView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self._build_controls()
        self._build_progress()
        self._build_tabs()
        self._build_actions()

    # ---------------- UI BUILDERS ---------------- #

    def _build_controls(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=6)

        self.mode = tk.StringVar(value="ext")

        ttk.Radiobutton(
            top, text="By Extension", variable=self.mode, value="ext"
        ).pack(side="left")

        ttk.Radiobutton(
            top, text="By Name", variable=self.mode, value="name"
        ).pack(side="left", padx=(5, 10))

        self.entry = ttk.Entry(top, width=35)
        self.entry.pack(side="left", padx=5)

        self.search_btn = ttk.Button(top, text="🔍 Search")
        self.search_btn.pack(side="left", padx=5)

        self.new_tab_btn = ttk.Button(top, text="➕ New Tab")
        self.new_tab_btn.pack(side="left", padx=5)

        self.fav_btn = ttk.Button(top, text="⭐ Favorite")
        self.fav_btn.pack(side="left", padx=5)

    def _build_progress(self):
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 5))

    def _build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

    def _build_actions(self):
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=5)

        self.open_file_btn = ttk.Button(bottom, text="📂 Open File")
        self.open_file_btn.pack(side="left", padx=5)

        self.open_folder_btn = ttk.Button(bottom, text="📁 Open Folder")
        self.open_folder_btn.pack(side="left", padx=5)

        self.preview_canvas = tk.Canvas(
            bottom, width=240, height=240, bg="#1e1e1e", highlightthickness=1
        )
        self.preview_canvas.pack(side="right", padx=5)

    # ---------------- TAB MANAGEMENT ---------------- #

    def create_tab(self, title: str):
        """
        Create and activate a new search tab.
        Returns: (frame, tree)
        """
        frame = ttk.Frame(self.tabs)

        tree = ttk.Treeview(
            frame,
            columns=("path",),
            show="headings",
            selectmode="browse",
        )
        tree.heading("path", text="Full File Path")
        tree.column("path", anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabs.add(frame, text=title)
        self.tabs.select(frame)

        return frame, tree

