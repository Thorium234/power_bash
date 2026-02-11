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
    """Open file with system default application safely."""
    if not os.path.exists(path):
        print(f"[utils] File not found: {path}")
        return False
    
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            # Validate file path to prevent command injection
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.path.expanduser("~")):
                print(f"[utils] Suspicious path blocked: {abs_path}")
                return False
                
            subprocess.Popen(
                ["xdg-open", abs_path], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                start_new_session=True,
                close_fds=True
            )
        return True
    except (FileNotFoundError, PermissionError) as e:
        print(f"[utils] Cannot open file {path}: {e}")
        return False
    except Exception as e:
        print(f"[utils] open_file error: {e}")
        return False

def open_folder(path):
    """Open containing folder safely."""
    if not os.path.exists(path):
        print(f"[utils] Path not found: {path}")
        return False
        
    try:
        folder = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(folder):
            print(f"[utils] Folder not found: {folder}")
            return False
            
        if os.name == "nt":
            os.startfile(folder)
        else:
            # Validate folder path
            if not folder.startswith(os.path.expanduser("~")):
                print(f"[utils] Suspicious folder blocked: {folder}")
                return False
                
            subprocess.Popen(
                ["xdg-open", folder], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                start_new_session=True,
                close_fds=True
            )
        return True
    except (FileNotFoundError, PermissionError) as e:
        print(f"[utils] Cannot open folder: {e}")
        return False
    except Exception as e:
        print(f"[utils] open_folder error: {e}")
        return False

# ---------------- DRAWIO PREVIEW ---------------- #

def preview_drawio(path, canvas):
    """
    Render preview for drawio files using draw.io CLI.
    """
    # Clean up existing image reference
    if hasattr(canvas, 'image'):
        canvas.image = None
    
    drawio_bin = shutil.which("drawio") or shutil.which("drawio-desktop")
    if not drawio_bin:
        print("[utils] drawio CLI not found")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = os.path.join(tmpdir, "preview.png")
            result = subprocess.run(
                [drawio_bin, "--export", "--output", png_path, path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                check=True, timeout=10
            )
            img = Image.open(png_path)
            img.thumbnail((240, 240), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img  # Keep reference
    except subprocess.TimeoutExpired:
        print("[utils] drawio preview timeout")
    except subprocess.CalledProcessError as e:
        print(f"[utils] drawio export failed: {e}")
    except Exception as e:
        print(f"[utils] preview_drawio error: {e}")
    finally:
        pass

