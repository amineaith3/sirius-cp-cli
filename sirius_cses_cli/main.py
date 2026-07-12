import typer
from rich.console import Console

from sirius_cses_cli.config import save_config, load_config, get_default_lang, get_handle
from sirius_cses_cli.scraper import fetch_problem
from sirius_cses_cli.tester import test_solution
from sirius_cses_cli.submitter import submit_solution
from sirius_cses_cli.api import sync_index, get_next_unsolved, get_problem_report, INDEX_FILE
import json
import time

app = typer.Typer(help="Sirius CSES CLI - Offline Competitive Programming Environment")
console = Console()

@app.command("init")
def init(
    handle: str = typer.Option(..., prompt="Your CSES handle"),
    lang: str = typer.Option("cpp", prompt="Default language (cpp/py)"),
    cookie: str = typer.Option("", prompt="CSES_COOKIE string (leave blank to read from .env later)", show_default=False),
    template: str = typer.Option("", prompt="Path to custom C++ template (leave blank for default)", show_default=False),
    workspace: str = typer.Option("", prompt="Path to CSES offline workspace (leave blank for default ~/Desktop/cses-offline)", show_default=False)
):
    """
    Initialize or update global configuration.
    """
    save_config(handle, lang, template, workspace)
    if cookie:
        # Save to config if provided. If they leave it blank, we read from .env
        config = load_config()
        config["cookie"] = cookie
        import json
        from sirius_cses_cli.config import CONFIG_FILE
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
            
    console.print("[bold green][OK] Config saved to ~/.sirius-cses-cli.json[/bold green]")
    console.print(f"Handle: {handle} | Default Lang: {lang}")

@app.command("fetch")
def fetch(
    task_id: str = typer.Argument(..., help="Task ID (e.g. 1068)")
):
    """
    Fetch a CSES problem, test cases, and scaffold code.
    """
    fetch_problem(task_id)

@app.command("test")
def test(
    task_id: str = typer.Argument(..., help="Task ID (e.g. 1068)"),
    lang: str = typer.Option(None, help="Language override (cpp/py)")
):
    """
    Test solution against sample inputs.
    """
    test_lang = lang if lang else get_default_lang()
    test_solution(task_id, test_lang)

@app.command("submit")
def submit(
    task_id: str = typer.Argument(..., help="Task ID (e.g. 1068)"),
    lang: str = typer.Option(None, help="Language override (cpp/py)")
):
    """
    Submit solution to CSES.
    """
    submit_lang = lang if lang else get_default_lang()
    submit_solution(task_id, submit_lang)

@app.command("sync")
def sync():
    """
    Sync all 400 problems from CSES and track solved status.
    """
    sync_index()

@app.command("next")
def next_problem(
    category: str = typer.Argument(None, help="Optional category filter (e.g. 'Dynamic Programming' or 'graph')")
):
    """
    Automatically fetch the next unsolved problem.
    """
    task_id = get_next_unsolved(category)
    if task_id:
        console.print(f"[bold cyan]Next unsolved task found: {task_id}[/bold cyan]")
        fetch_problem(task_id)

@app.command("report")
def report(
    task_id: str = typer.Argument(..., help="Task ID (e.g. 1068)")
):
    """
    Show your latest AC submission for a specific task.
    """
    get_problem_report(task_id)

@app.command("download-all")
def download_all():
    """
    Bulk download all 400 CSES problems for offline practice.
    """
    if not INDEX_FILE.exists():
        console.print("[yellow]Index not found. Syncing first...[/yellow]")
        if not sync_index():
            return
            
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
        
    problems = index_data.get("problems", {})
    total = len(problems)
    console.print(f"[bold cyan]Starting bulk download of {total} tasks...[/bold cyan]")
    
    count = 0
    for task_id in problems.keys():
        count += 1
        console.print(f"\n[bold yellow]({count}/{total}) Task {task_id}[/bold yellow]")
        fetch_problem(task_id)
        # Polite delay to prevent rate-limiting
        time.sleep(0.5)
        
    console.print("\n[bold green]Offline download complete! All 400 problems are stored locally.[/bold green]")

if __name__ == "__main__":
    app()
