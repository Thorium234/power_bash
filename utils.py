import os
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from PIL import Image, ImageTk

# ---------------- PATHS ---------------- #

TABS_FILE = Path.home() / ".file_finder_tabs.json"

# ---------------- JSON PERSISTENCE ---------------- #

def save_tabs(tabs: List[Dict[str, Any]]) -> None:
    """
    Atomically save favorite tabs to disk.
    """
    try:
        tmp = TABS_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tabs, f, indent=2)
        tmp.replace(TABS_FILE)
    except Exception as e:
        print("[tabs] save failed:", e)

def load_tabs() -> List[Dict[str, Any]]:
    """
    Load saved favorite tabs safely.
    """
    if not TABS_FILE.exists():
        return []

    try:
        with open(TABS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print("[tabs] load failed:", e)
        return []

# ---------------- FILE OPERATIONS ---------------- #

def open_file(path: str) -> None:
    """
    Open a file using system default app (non-blocking).
    """
    try:
        subprocess.Popen(
            ["xdg-open", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        print("[open_file] error:", e)

def open_folder(path: str) -> None:
    """
    Open the containing folder of a file.
    """
    try:
        folder = os.path.dirname(path)
        subprocess.Popen(
            ["xdg-open", folder],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        print("[open_folder] error:", e)

# ---------------- DRAW.IO PREVIEW ---------------- #

def preview_drawio(path: str, canvas) -> None:
    """
    Render a preview thumbnail for .drawio files using draw.io CLI.

    Requirements:
      - drawio or drawio-desktop installed
    """
    drawio_bin = shutil.which("drawio") or shutil.which("drawio-desktop")
    if not drawio_bin:
        print("[drawio] CLI not found")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = os.path.join(tmpdir, "preview.png")

            subprocess.run(
                [
                    drawio_bin,
                    "--export",
                    "--output",
                    png_path,
                    path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            img = Image.open(png_path)
            img.thumbnail((240, 240), Image.LANCZOS)

            tk_img = ImageTk.PhotoImage(img)

            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=tk_img)

            # prevent garbage collection
            canvas.image = tk_img

    except Exception as e:
        print("[drawio] preview failed:", e)

