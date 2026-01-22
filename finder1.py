import os
import pickle
import time
from pathlib import Path
from typing import Callable, Dict, List

# ---------------- CONFIG ---------------- #

EXCLUDED_DIRS = {
    ".cache",
    ".local/share/Trash",
    "node_modules",
    "__pycache__",
    ".git",
}

CACHE_FILE = Path.home() / ".file_finder_cache.pkl"
CACHE_VERSION = 2          # bump if cache structure changes
CACHE_TTL = 60 * 60 * 24   # 24 hours

# ---------------- CACHE ---------------- #

def _load_raw_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}

    try:
        with open(CACHE_FILE, "rb") as f:
            data = pickle.load(f)
            if data.get("_version") != CACHE_VERSION:
                return {}
            return data
    except Exception:
        return {}

def _save_raw_cache(cache: dict) -> None:
    try:
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print("[cache] save failed:", e)

def load_cache() -> dict:
    return _load_raw_cache()

def save_cache(cache: dict) -> None:
    _save_raw_cache(cache)

def _cache_key(root: str, mode: str, query: str) -> str:
    return f"{root}|{mode}|{query.lower()}"

def _is_cache_valid(entry: dict) -> bool:
    return (time.time() - entry["ts"]) < CACHE_TTL

# ---------------- SEARCH ENGINE ---------------- #

def search_files(
    root: str,
    mode: str,
    query: str,
    callback: Callable[[str], None],
    stop_flag: List[bool],
    cache: Dict | None = None,
) -> None:
    """
    Recursive file search with:
    - cancel support
    - cache
    - full absolute paths only
    """

    root = os.path.abspath(root)
    query = query.strip().lower()

    if not query:
        return

    if cache is None:
        cache = {}

    key = _cache_key(root, mode, query)

    # ---------- CACHE HIT ----------
    entry = cache.get(key)
    if entry and _is_cache_valid(entry):
        for path in entry["results"]:
            if stop_flag[0]:
                return
            callback(path)
        return

    results: List[str] = []

    # ---------- WALK ----------
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        if stop_flag[0]:
            break

        # prune directories early (huge speed win)
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDED_DIRS and not d.startswith(".")
        ]

        for filename in filenames:
            if stop_flag[0]:
                break

            filename_l = filename.lower()

            match = (
                mode == "name" and query in filename_l
            ) or (
                mode == "ext" and filename_l.endswith(f".{query}")
            )

            if not match:
                continue

            full_path = os.path.join(dirpath, filename)
            results.append(full_path)
            callback(full_path)

    # ---------- SAVE CACHE ----------
    cache[key] = {
        "ts": time.time(),
        "results": results,
    }
    save_cache(cache)

