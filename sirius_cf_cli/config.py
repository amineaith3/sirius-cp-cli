import os
import json
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()  # Load .env once at module level

CONFIG_FILE = Path.home() / ".sirius-cf-cli.json"
_console = Console()

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            _console.print(f"[bold yellow]Warning:[/bold yellow] Config file at [cyan]{CONFIG_FILE}[/cyan] is corrupted or invalid JSON. Please run [bold]sirius-cf init[/bold] to reset it.")
            return {}
        except Exception as e:
            _console.print(f"[bold yellow]Warning:[/bold yellow] Could not read config file: {e}")
            return {}
    return {}

def save_config(config_data: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def get_cookie() -> str:
    """Attempts to get CF_COOKIE from local .env or global config."""
    cookie = os.environ.get("CF_COOKIE")
    if cookie:
        return cookie
    config = load_config()
    return config.get("cf_cookie", "")

def get_default_lang() -> str:
    config = load_config()
    return config.get("default_lang", "cpp")

def get_handle() -> str:
    config = load_config()
    return config.get("handle", "")

def get_template_cpp_path() -> str:
    config = load_config()
    return config.get("template_cpp", "")
