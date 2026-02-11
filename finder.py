import os
import pickle
import time
from pathlib import Path
import subprocess
import shutil

from config import config

excluded_config = config.get('search.excluded_dirs')
EXCLUDED_DIRS = set(excluded_config) if excluded_config else {".cache", ".local/share/Trash"}
CACHE_FILE = config.get_cache_file('search_cache.pkl')

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
    Supports extension, name, and content search modes.
    Returns file metadata (path, size, modified_time).
    """
    if cache is None:
        cache = {}

    # Validate inputs
    if not query or len(query) < 1:
        return
        
    if mode not in ["ext", "name", "content"]:
        print(f"[finder] Invalid search mode: {mode}")
        return

    key = f"{mode}:{query}:{str(root)}"
    if key in cache:
        for file_info in cache[key]:
            if not stop_flag[0]:
                callback(file_info)
        return

    results = []

    # Try ripgrep if available (fast backend)
    rg_bin = shutil.which("rg")
    if rg_bin:
        proc = None  # Initialize outside try block
        try_ripgrep = True
        try:
            # Safer command construction
            if mode == "ext":
                cmd = [rg_bin, "--files", str(root), "--glob", f"*.{query}"]
            elif mode == "name":
                cmd = [rg_bin, "--files", str(root), "--iglob", f"*{query}*"]
            else:  # content search
                cmd = [rg_bin, "--files-with-matches", str(root), query]
                
            proc = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL, 
                text=True,
                preexec_fn=os.setsid if os.name != "nt" else None
            )
            
            if proc.stdout:
                for line in proc.stdout:
                    if stop_flag[0]:
                        if os.name != "nt":
                            os.killpg(os.getpgid(proc.pid), 9)
                        else:
                            proc.kill()
                        break
                        
                    path = line.strip()
                    if path and os.path.exists(path):  # Validate file exists
                        file_info = get_file_info(path)
                        results.append(file_info)
                        callback(file_info)
                        
                proc.stdout.close()
                proc.wait(timeout=30)
                
        except subprocess.TimeoutExpired as e:
            print("[finder] Ripgrep timeout, falling back to Python")
            if 'proc' in locals() and proc and proc.pid and os.name != "nt":
                os.killpg(os.getpgid(proc.pid), 9)
            try_ripgrep = False
        except Exception as e:
            print(f"[finder] Ripgrep failed, fallback to Python: {e}")
            try_ripgrep = False
            
        if not try_ripgrep or stop_flag[0]:
            _walk_search(root, mode, query, callback, stop_flag, results)
    else:
        _walk_search(root, mode, query, callback, stop_flag, results)

    cache[key] = results
    save_cache(cache)


def get_file_info(path):
    """Get file metadata including size and modification time."""
    try:
        stat = os.stat(path)
        size = format_file_size(stat.st_size)
        modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
        return {
            'path': path,
            'size': size,
            'modified': modified
        }
    except (OSError, PermissionError):
        return {
            'path': path,
            'size': 'Unknown',
            'modified': 'Unknown'
        }


def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def _walk_search(root, mode, query, callback, stop_flag, results):
    """Fallback search using os.walk"""
    query_lower = query.lower()
    
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            if stop_flag[0]:
                break
                
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
            
            for name in filenames:
                if stop_flag[0]:
                    break
                    
                try:
                    # Validate file name to prevent path traversal
                    if ".." in name or "/" in name or "\\" in name:
                        continue
                        
                    match = False
                    full_path = os.path.join(dirpath, name)
                    
                    # Validate full path exists and is accessible
                    if not os.path.isfile(full_path) or not os.access(full_path, os.R_OK):
                        continue
                    
                    if mode == "name":
                        match = query_lower in name.lower()
                    elif mode == "ext":
                        match = name.lower().endswith(f".{query_lower}")
                    elif mode == "content":
                        # Simple content search for text files
                        try:
                            # Only search in text files smaller than 1MB
                            if os.path.getsize(full_path) < 1024 * 1024:
                                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read(8192)  # Read first 8KB
                                    if query_lower in content.lower():
                                        match = True
                        except (OSError, UnicodeDecodeError):
                            continue
                        
                    if match:
                        file_info = get_file_info(full_path)
                        results.append(file_info)
                        callback(file_info)
                        
                except (OSError, UnicodeError):
                    # Skip files that can't be accessed
                    continue
                    
    except (OSError, PermissionError) as e:
        print(f"[finder] Search error in {root}: {e}")
    except Exception as e:
        print(f"[finder] Unexpected search error: {e}")

