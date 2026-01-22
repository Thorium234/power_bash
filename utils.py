import os
import subprocess
from PIL import Image, ImageTk
import json
from pathlib import Path
import tempfile
import shutil

TABS_FILE = Path.home() / ".file_finder_tabs.json"

# ---------------- TAB PERSISTENCE ---------------- #

def save_tabs(tabs):
    try:
        tmp = TABS_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tabs, f, indent=2)
        tmp.replace(TABS_FILE)
    except Exception as e:
        print("[utils] save_tabs error:", e)

def load_tabs():
    if TABS_FILE.exists():
        try:
            with open(TABS_FILE, encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print("[utils] load_tabs error:", e)
    return []

# ---------------- FILE OPERATIONS ---------------- #

def open_file(path):
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except Exception as e:
        print("[utils] open_file error:", e)

def open_folder(path):
    try:
        folder = os.path.dirname(path)
        if os.name == "nt":
            os.startfile(folder)
        else:
            subprocess.Popen(["xdg-open", folder], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except Exception as e:
        print("[utils] open_folder error:", e)

# ---------------- DRAWIO PREVIEW ---------------- #

def preview_drawio(path, canvas):
    """
    Render preview for drawio files using draw.io CLI.
    """
    drawio_bin = shutil.which("drawio") or shutil.which("drawio-desktop")
    if not drawio_bin:
        print("[utils] drawio CLI not found")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = os.path.join(tmpdir, "preview.png")
            subprocess.run([drawio_bin, "--export", "--output", png_path, path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            img = Image.open(png_path)
            img.thumbnail((240, 240), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img
    except Exception as e:
        print("[utils] preview_drawio error:", e)

