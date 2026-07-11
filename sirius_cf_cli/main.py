import typer
from typing import Optional
from rich.console import Console

from sirius_cf_cli.config import save_config, load_config, get_default_lang, get_handle
from sirius_cf_cli.scraper import fetch_problem
from sirius_cf_cli.tester import test_solution
from sirius_cf_cli.submitter import submit_solution
from sirius_cf_cli.api import get_user_solved_problems, get_next_problem_by_rating

app = typer.Typer(name="sirius-cf", help="A local Codeforces competitive programming environment.")
console = Console()

@app.command()
def init(
    handle: str = typer.Option(..., prompt="Your Codeforces handle"),
    lang: str = typer.Option("cpp", prompt="Default language (cpp/py)"),
    cookie: str = typer.Option("", prompt="CF_COOKIE string (leave blank to read from .env later)", show_default=False),
    template: str = typer.Option("", prompt="Path to custom C++ template (leave blank for default)", show_default=False)
):
    """Initialize the sirius-cf configuration."""
    config = load_config()
    config["handle"] = handle
    config["default_lang"] = lang
    if cookie:
        config["cf_cookie"] = cookie
    if template:
        config["template_cpp"] = template
        
    save_config(config)
    console.print(f"[bold green][OK] Config saved to ~/.sirius-cf-cli.json[/bold green]")
    console.print(f"Handle: {handle} | Default Lang: {lang}")

@app.command()
def fetch(contest: str, problem: str):
    """Fetch problem statement and test cases, scaffold starter code."""
    fetch_problem(contest, problem.upper())

@app.command()
def test(
    contest: str, 
    problem: str, 
    lang: Optional[str] = typer.Option(None, help="Language to test (cpp/py). Defaults to config.")
):
    """Compile and test your solution against downloaded test cases."""
    lang = lang or get_default_lang()
    test_solution(contest, problem.upper(), lang)

@app.command()
def submit(
    contest: str, 
    problem: str, 
    lang: Optional[str] = typer.Option(None, help="Language to submit (cpp/py). Defaults to config.")
):
    """Submit your code directly to Codeforces."""
    lang = lang or get_default_lang()
    submit_solution(contest, problem.upper(), lang)

@app.command()
def next(rating: int = typer.Argument(..., help="Target rating to practice (e.g., 1200)")):
    """Find the next unsolved problem for a given rating and set it up."""
    handle = get_handle()
    if not handle:
        console.print("[bold red]Please run `sirius-cf init` to set your handle first.[/bold red]")
        raise typer.Exit(1)
        
    with console.status(f"Analyzing solved problems for [bold]{handle}[/bold]..."):
        solved = get_user_solved_problems(handle)
        
    console.print(f"[green][OK] Found {len(solved)} solved problems for {handle}.[/green]")
    
    with console.status(f"Finding an unsolved problem with rating {rating}..."):
        contest_id, problem_index = get_next_problem_by_rating(rating, solved)
        
    if contest_id is not None and problem_index is not None:
        console.print(f"[bold magenta]Found problem:[/bold magenta] {contest_id}-{problem_index} ({rating})")
        fetch_problem(contest_id, problem_index)
    else:
        console.print(f"[bold yellow]Could not find any unsolved problem with rating {rating}.[/bold yellow]")

if __name__ == "__main__":
    app()
