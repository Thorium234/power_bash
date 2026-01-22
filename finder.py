import os
import pickle
from pathlib import Path
import subprocess
import shutil
import platform

EXCLUDED_DIRS = {".cache", ".local/share/Trash"}
CACHE_FILE = Path.home() / ".file_finder_cache.pkl"

# ---------------- CACHE ---------------- #

def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print("[finder] Cache save error:", e)


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print("[finder] Cache load failed:", e)
            return {}
    return {}

# ---------------- SEARCH ---------------- #

def search_files(root, mode, query, callback, stop_flag, cache=None):
    """
    Search files recursively with caching, cancellation, and optional ripgrep backend.
    """
    if cache is None:
        cache = {}

    key = f"{mode}:{query}:{str(root)}"
    if key in cache:
        for path in cache[key]:
            callback(path)
        return

    results = []

    # Try ripgrep if available (fast backend)
    rg_bin = shutil.which("rg")
    if rg_bin:
        try:
            ext_flag = "--glob" if mode == "ext" else "-g"
            pattern = f"*.{query}" if mode == "ext" else f"*{query}*"
            cmd = [rg_bin, "--files", str(root), ext_flag, pattern]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            for line in proc.stdout:
                if stop_flag[0]:
                    proc.kill()
                    break
                path = line.strip()
                results.append(path)
                callback(path)
            proc.stdout.close()
            proc.wait()
        except Exception as e:
            print("[finder] Ripgrep search failed, fallback to Python", e)
            _walk_search(root, mode, query, callback, stop_flag, results)
    else:
        _walk_search(root, mode, query, callback, stop_flag, results)

    cache[key] = results
    save_cache(cache)


def _walk_search(root, mode, query, callback, stop_flag, results):
    """Fallback search using os.walk"""
    for dirpath, dirnames, filenames in os.walk(root):
        if stop_flag[0]:
            break
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            if stop_flag[0]:
                break
            if (mode == "name" and query.lower() in name.lower()) or \
               (mode == "ext" and name.lower().endswith(f".{query.lower()}")):
                full_path = os.path.join(dirpath, name)
                results.append(full_path)
                callback(full_path)

