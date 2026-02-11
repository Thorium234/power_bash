"""
Configuration management for Smart File Finder Pro
Handles app settings, themes, and user preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".config" / "file_finder"
        self.config_file = self.config_dir / "config.json"
        self.cache_dir = self.home / ".cache" / "file_finder"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.defaults = {
            "app": {
                "name": "Smart File Finder Pro",
                "window_width": 1250,
                "window_height": 750,
            "min_width": 800,
            "min_height": 500,
                "max_history": 50,
                "search_timeout": 30
            },
            "ui": {
                "theme": "dark",
                "font_family": "JetBrains Mono",
                "font_size": 10,
                "tree_row_height": 24
            },
            "search": {
                "excluded_dirs": [
                    ".cache", ".local/share/Trash", ".git", 
                    "node_modules", "__pycache__", ".venv", "env"
                ],
                "max_results": 10000,
                "use_ripgrep": True,
                "cache_enabled": True,
                "cache_ttl": 3600  # 1 hour
            },
            "paths": {
                "home": str(self.home),
                "desktop": str(self.home / "Desktop"),
                "documents": str(self.home / "Documents"),
                "downloads": str(self.home / "Downloads"),
                "projects": str(self.home / "Projects")
            },
            "preview": {
                "max_size": (240, 240),
                "timeout": 10,
                "supported_formats": [".drawio", ".png", ".jpg", ".jpeg", ".gif", ".pdf"]
            }
        }
        
        self.config = self.load()
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation (e.g., 'ui.theme')"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value if value is not None else default
        except (KeyError, TypeError):
            # Try defaults
            value = self.defaults
            for k in keys:
                value = value[k]
            return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self.save()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[config] Error loading config: {e}")
        
        # Return a deep copy of defaults
        return json.loads(json.dumps(self.defaults))
    
    def save(self):
        """Save configuration to file"""
        try:
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            temp_file.replace(self.config_file)
        except IOError as e:
            print(f"[config] Error saving config: {e}")
    
    def get_cache_file(self, name: str) -> Path:
        """Get path to cache file"""
        return self.cache_dir / name
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme colors"""
        if theme_name is None:
            theme_name = self.get('ui.theme', 'dark')
            
        themes = {
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#e6e6e6",
                "accent": "#4caf50",
                "canvas": "#1e1e1e",
                "select_bg": "#404040",
                "select_fg": "#ffffff"
            },
            "light": {
                "bg": "#f2f2f2", 
                "fg": "#222222",
                "accent": "#007acc",
                "canvas": "#dddddd",
                "select_bg": "#007acc",
                "select_fg": "#ffffff"
            },
            "blue": {
                "bg": "#1e3a8a",
                "fg": "#e0e7ff",
                "accent": "#3b82f6",
                "canvas": "#172554",
                "select_bg": "#2563eb",
                "select_fg": "#ffffff"
            }
        }
        
        return themes.get(theme_name, themes["dark"])
    
    def get_search_scopes(self) -> Dict[str, str]:
        """Get available search scopes"""
        scopes = {}
        paths = self.get('paths', {})
        
        for name, path in paths.items():
            if Path(path).exists():
                # Capitalize first letter for display
                display_name = name.title().replace('_', ' ')
                scopes[display_name] = path
                
        return scopes

# Global config instance
config = Config()