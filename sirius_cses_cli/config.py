import os
import json
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()  # Load .env once at module level

CONFIG_FILE = Path.home() / ".sirius-cses-cli.json"
console = Console()

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            console.print("[yellow]Warning: CSES Config file is corrupted. Run sirius-cses init to reset.[/yellow]")
            return {}
    return {}

def save_config(handle: str, lang: str, template_path: str = "", workspace: str = ""):
    data = {"handle": handle, "lang": lang, "template_cpp": template_path, "workspace": workspace}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_default_lang() -> str:
    config = load_config()
    return config.get("lang", "cpp")

def get_handle() -> str:
    config = load_config()
    return config.get("handle", "")

def get_template_cpp_path() -> str:
    config = load_config()
    return config.get("template_cpp", "")

def get_workspace_path() -> str:
    config = load_config()
    ws = config.get("workspace", "")
    if ws:
        return os.path.abspath(os.path.expanduser(ws))
    # Default to ~/Desktop/cses-offline
    default_ws = Path.home() / "Desktop" / "cses-offline"
    return str(default_ws.absolute())

def get_cookie() -> str:
    # Look for CSES_COOKIE instead of CF_COOKIE
    cookie = os.getenv("CSES_COOKIE")
    if cookie:
        return cookie
    
    # Alternatively check PHPSESSID if user named it that way
    phpsessid = os.getenv("PHPSESSID")
    if phpsessid:
        # Check if it has 'PHPSESSID=' already
        if "PHPSESSID=" in phpsessid:
            return phpsessid
        return f"PHPSESSID={phpsessid}"
        
    config = load_config()
    return config.get("cookie", "")
