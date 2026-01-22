import tkinter as tk
from tkinter import ttk
from threading import Thread
import queue
from pathlib import Path

from finder import search_files, load_cache
from view import FinderView
from utils import (
    open_file,
    open_folder,
    preview_drawio,
    save_tabs,
    load_tabs,
)

HOME = str(Path.home())


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart File Finder Pro")
        self.geometry("1100x650")

        # ---------- Theme ----------
        style = ttk.Style()
        style.theme_use("clam")
        self.configure(bg="#2b2b2b")

        # ---------- Core State ----------
        self.view = FinderView(self)
        self.queue = queue.Queue()
        self.cache = load_cache()

        self.tabs = {}        # tab_id -> tab context
        self.stop_flags = {}  # tab_id -> [bool]

        # ---------- Bindings ----------
        self.view.search_btn.config(command=self.search_current_tab)
        self.view.new_tab_btn.config(command=self.new_tab)
        self.view.fav_btn.config(command=self.favorite_current_tab)

        self.view.open_file_btn.config(command=self.open_selected_file)
        self.view.open_folder_btn.config(command=self.open_selected_folder)

        self.after(100, self.process_queue)

        # ---------- Startup ----------
        self.restore_favorite_tabs()
        if not self.tabs:
            self.new_tab("Search 1")

    # ==========================================================
    # Tabs
    # ==========================================================

    def new_tab(self, title="New Search"):
        frame, tree = self.view.create_tab(title)
        tab_id = str(id(frame))

        self.tabs[tab_id] = {
            "frame": frame,
            "tree": tree,
            "mode": None,
            "query": None,
            "favorite": False,
        }
        self.stop_flags[tab_id] = [False]

        self.view.tabs.select(frame)

    def current_tab_id(self):
        frame = self.view.tabs.nametowidget(self.view.tabs.select())
        return str(id(frame))

    def current_tab(self):
        return self.tabs[self.current_tab_id()]

    # ==========================================================
    # Search
    # ==========================================================

    def search_current_tab(self):
        tab_id = self.current_tab_id()
        tab = self.tabs[tab_id]

        query = self.view.entry.get().strip()
        if not query:
            return

        tab["tree"].delete(*tab["tree"].get_children())
        tab["mode"] = self.view.mode.get()
        tab["query"] = query
        self.stop_flags[tab_id][0] = False

        self.view.progress.start()

        Thread(
            target=search_files,
            args=(
                HOME,
                tab["mode"],
                query,
                lambda path: self.queue.put((tab_id, path)),
                self.stop_flags[tab_id],
                self.cache,
            ),
            daemon=True,
        ).start()

    def process_queue(self):
        while not self.queue.empty():
            tab_id, path = self.queue.get()
            if tab_id in self.tabs:
                self.tabs[tab_id]["tree"].insert("", "end", values=(path,))

        self.after(100, self.process_queue)

    # ==========================================================
    # File actions
    # ==========================================================

    def selected_path(self):
        tree = self.current_tab()["tree"]
        sel = tree.selection()
        if not sel:
            return None
        return tree.item(sel[0])["values"][0]

    def open_selected_file(self):
        path = self.selected_path()
        if not path:
            return

        open_file(path)
        if path.lower().endswith(".drawio"):
            preview_drawio(path, self.view.preview_canvas)

    def open_selected_folder(self):
        path = self.selected_path()
        if path:
            open_folder(path)

    # ==========================================================
    # Favorites
    # ==========================================================

    def favorite_current_tab(self):
        tab = self.current_tab()
        tab["favorite"] = True

        idx = self.view.tabs.index(self.view.tabs.select())
        title = self.view.tabs.tab(idx, "text")
        if not title.startswith("⭐"):
            self.view.tabs.tab(idx, text=f"⭐ {title}")

        self.save_favorites()

    def save_favorites(self):
        favs = [
            {"mode": t["mode"], "query": t["query"]}
            for t in self.tabs.values()
            if t["favorite"] and t["query"]
        ]
        save_tabs(favs)

    def restore_favorite_tabs(self):
        for fav in load_tabs():
            self.new_tab(f"⭐ {fav['query']}")
            self.view.entry.delete(0, tk.END)
            self.view.entry.insert(0, fav["query"])
            self.view.mode.set(fav["mode"])
            self.search_current_tab()


if __name__ == "__main__":
    App().mainloop()

