import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from pathlib import Path
import queue
import time
import shutil
import platform
import json
import sys

from finder import search_files
from view import FinderView
from utils import (
    open_file,
    open_folder,
    preview_drawio,
)

# ================= CONFIG ================= #

APP_NAME = "Smart File Finder Pro"
HOME = Path.home()

HISTORY_FILE = HOME / ".file_finder_history.json"
MAX_HISTORY = 50

SEARCH_SCOPES = {
    "Home": HOME,
    "Desktop": HOME / "Desktop",
    "Projects": HOME / "Projects",
}

# ================= TASK ================= #

class SearchTask:
    """Encapsulates one cancellable search task."""

    def __init__(self, root, mode, query, out_queue):
        self.root = str(root)
        self.mode = mode
        self.query = query
        self.queue = out_queue
        self.stop_flag = [False]
        self.thread = None

    def start(self):
        self.thread = Thread(
            target=search_files,
            args=(
                self.root,
                self.mode,
                self.query,
                lambda p: self.queue.put(p),
                self.stop_flag,
            ),
            daemon=True,
        )
        self.thread.start()

    def cancel(self):
        self.stop_flag[0] = True

    def is_alive(self):
        return self.thread and self.thread.is_alive()

# ================= APP ================= #

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1200x700")
        self.minsize(900, 600)

        # ---------- STATE ----------
        self.queue = queue.Queue()
        self.active_task = None
        self.current_tree = None
        self.history = self.load_history()
        self.theme = "dark"

        # ---------- UI ----------
        self.view = FinderView(self)
        self.setup_scope_selector()
        self.setup_clock()
        self.setup_shortcuts()

        # ---------- EVENTS ----------
        self.view.search_btn.config(command=self.start_search)
        self.view.new_tab_btn.config(command=self.new_tab)
        self.view.open_file_btn.config(command=self.open_file)
        self.view.open_folder_btn.config(command=self.open_folder)

        self.after(50, self.process_queue)

        # ---------- INIT ----------
        self.new_tab("Welcome")

    # ================= UI EXTRAS ================= #

    def setup_scope_selector(self):
        self.scope_var = tk.StringVar(value="Home")

        scope_menu = ttk.OptionMenu(
            self.view, self.scope_var, "Home", *SEARCH_SCOPES.keys()
        )
        scope_menu.pack(anchor="w", padx=12)

    def setup_clock(self):
        self.clock = ttk.Label(self.view, font=("JetBrains Mono", 10))
        self.clock.pack(anchor="e", padx=10)
        self.update_clock()

    def update_clock(self):
        self.clock.config(text=time.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def setup_shortcuts(self):
        self.bind("<Control-Return>", lambda e: self.start_search())
        self.bind("<Control-t>", lambda e: self.new_tab())
        self.bind("<Control-w>", lambda e: self.close_tab())
        self.bind("<Control-q>", lambda e: self.safe_exit())
        self.bind("<Control-l>", lambda e: self.view.entry.focus())

    # ================= TABS ================= #

    def new_tab(self, title="New Search"):
        frame, tree = self.view.create_tab(title)
        self.current_tree = tree
        self.view.tabs.select(frame)

    def close_tab(self):
        current = self.view.tabs.select()
        if not current:
            return

        if self.active_task:
            self.active_task.cancel()

        self.view.tabs.forget(current)

    # ================= SEARCH ================= #

    def start_search(self):
        query = self.view.entry.get().strip()
        if not query:
            return

        if self.active_task:
            self.active_task.cancel()

        scope = SEARCH_SCOPES.get(self.scope_var.get(), HOME)

        self.current_tree.delete(*self.current_tree.get_children())

        self.active_task = SearchTask(
            root=scope,
            mode=self.view.mode.get(),
            query=query,
            out_queue=self.queue,
        )

        self.save_history(query)
        self.view.progress.start()
        self.active_task.start()

    def process_queue(self):
        try:
            while True:
                path = self.queue.get_nowait()
                self.current_tree.insert("", "end", values=(path,))
        except queue.Empty:
            pass

        if self.active_task and not self.active_task.is_alive():
            self.view.progress.stop()

        self.after(50, self.process_queue)

    # ================= ACTIONS ================= #

    def selected_path(self):
        sel = self.current_tree.selection()
        if not sel:
            return None
        return self.current_tree.item(sel[0])["values"][0]

    def open_file(self):
        path = self.selected_path()
        if not path:
            return
        open_file(path)
        if path.lower().endswith(".drawio"):
            preview_drawio(path, self.view.preview_canvas)

    def open_folder(self):
        path = self.selected_path()
        if path:
            open_folder(path)

    # ================= HISTORY ================= #

    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except Exception:
                return []
        return []

    def save_history(self, query):
        if query in self.history:
            self.history.remove(query)
        self.history.insert(0, query)
        self.history = self.history[:MAX_HISTORY]
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))

    # ================= EXIT ================= #

    def safe_exit(self):
        if self.active_task:
            self.active_task.cancel()
        self.destroy()


# ================= RUN ================= #

if __name__ == "__main__":
    try:
        App().mainloop()
    except KeyboardInterrupt:
        sys.exit(0)

