import os
import json
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
from rich.console import Console

from sirius_cses_cli.config import get_cookie, get_workspace_path

INDEX_FILE = Path.home() / ".sirius-cses-index.json"
console = Console()

def get_session():
    session = requests.Session()
    cookie_str = get_cookie()
    if cookie_str:
        phpsessid = ""
        if "PHPSESSID=" in cookie_str:
            for part in cookie_str.split(";"):
                if part.strip().startswith("PHPSESSID="):
                    phpsessid = part.split("=")[1].strip()
        else:
            phpsessid = cookie_str.strip()
        session.cookies.set("PHPSESSID", phpsessid)
    return session

def update_category_stats(ws_path: str, index_data: dict):
    categories = index_data.get("categories", [])
    problems = index_data.get("problems", {})
    
    # Group problems by category
    cat_to_probs = {cat: [] for cat in categories}
    for task_id, info in problems.items():
        if info["category"] in cat_to_probs:
            cat_to_probs[info["category"]].append(info)
            
    for cat in categories:
        cat_folder = os.path.join(ws_path, cat)
        os.makedirs(cat_folder, exist_ok=True)
        
        stats_file = os.path.join(cat_folder, "stats.txt")
        lines = [f"=== {cat} ==="]
        
        solved_in_cat = 0
        total_in_cat = len(cat_to_probs[cat])
        
        for prob in cat_to_probs[cat]:
            mark = "x" if prob["solved"] else " "
            if prob["solved"]:
                solved_in_cat += 1
            lines.append(f"[{mark}] {prob['id']} - {prob['name']}")
            
        lines.insert(1, f"Progress: {solved_in_cat} / {total_in_cat}")
        lines.insert(2, "")
        
        with open(stats_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

def sync_index():
    url = "https://cses.fi/problemset/"
    with console.status("Fetching problem index from CSES..."):
        session = get_session()
        try:
            res = session.get(url, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            console.print(f"[bold red][FAILED] Network Error: {e}[/bold red]")
            return False

    soup = BeautifulSoup(res.text, "html.parser")
    categories = soup.find_all("h2")
    
    index_data = {
        "categories": [],
        "problems": {}
    }
    
    solved_count = 0
    total_count = 0
    
    for cat in categories:
        cat_name = cat.text.strip()
        index_data["categories"].append(cat_name)
        
        ul = cat.find_next_sibling("ul")
        if ul:
            tasks = ul.find_all("li", class_="task")
            for t in tasks:
                a_tag = t.find("a")
                if not a_tag:
                    continue
                
                href = a_tag["href"]
                # href is like /problemset/task/1068
                task_id = href.split("/")[-1]
                if not task_id:
                    task_id = href.split("/")[-2] # in case of trailing slash
                    
                name = a_tag.contents[0].strip() if a_tag.contents else ""
                
                is_solved = False
                score_span = t.find("span", class_="task-score")
                if score_span and "full" in score_span.get("class", []):
                    is_solved = True
                    solved_count += 1
                
                index_data["problems"][task_id] = {
                    "id": task_id,
                    "name": name,
                    "category": cat_name,
                    "solved": is_solved
                }
                total_count += 1

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=4)
        
    ws_path = get_workspace_path()
    update_category_stats(ws_path, index_data)
        
    console.print(f"[bold green]Successfully synced {total_count} problems! You have solved {solved_count}.[/bold green]")
    return True

def get_problem_path(task_id: str) -> str:
    """Returns the absolute path to the task folder (e.g. ~/Desktop/cses-offline/Introductory Problems/1068--Weird-Algorithm)"""
    task_id = str(task_id)
    if not INDEX_FILE.exists():
        console.print("[yellow]Index not found. Running sync first...[/yellow]")
        if not sync_index():
            # Fallback if sync fails
            return os.path.join(get_workspace_path(), task_id)
            
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
        
    problem = index_data.get("problems", {}).get(task_id)
    if not problem:
        # Fallback if problem ID not in index (e.g., hidden contest problem)
        return os.path.join(get_workspace_path(), task_id)
        
    cat = problem["category"]
    name = problem["name"]
    # Sanitize name
    sanitized_name = re.sub(r'[^a-zA-Z0-9 -]', '', name).strip().replace(' ', '-')
    folder_name = f"{task_id}--{sanitized_name}"
    
    return os.path.join(get_workspace_path(), cat, folder_name)

def get_next_unsolved(category_query=None):
    if not INDEX_FILE.exists():
        console.print("[yellow]Index not found. Running sync first...[/yellow]")
        if not sync_index():
            return None
            
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
        
    # Default order based on categories list
    categories = index_data.get("categories", [])
    problems = index_data.get("problems", {})
    
    target_category = None
    if category_query:
        query_lower = category_query.lower()
        for cat in categories:
            if query_lower in cat.lower():
                target_category = cat
                console.print(f"[cyan]Matched category: {target_category}[/cyan]")
                break
        if not target_category:
            console.print(f"[bold red]No category matched '{category_query}'[/bold red]")
            return None

    # We must preserve CSES default order. Since dictionaries preserve insertion order in Python 3.7+, 
    # the problems are already in the order they appeared on the page.
    for task_id, info in problems.items():
        if target_category and info["category"] != target_category:
            continue
            
        if not info["solved"]:
            return task_id
            
    console.print("[bold green]Wow! You have solved all problems in this scope![/bold green]")
    return None

def get_problem_report(task_id: str):
    url = f"https://cses.fi/problemset/task/{task_id}/"
    with console.status("Fetching problem report..."):
        session = get_session()
        try:
            res = session.get(url, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            console.print(f"[bold red][FAILED] Network Error: {e}[/bold red]")
            return
            
    soup = BeautifulSoup(res.text, "html.parser")
    
    title_block = soup.find("div", class_="title-block")
    title = ""
    if title_block:
        h1 = title_block.find("h1")
        if h1:
            title = h1.text.strip()
            
    sidebar = soup.find("div", class_="sidebar")
    if not sidebar:
        console.print(f"Task {task_id}: {title} (No sidebar found, are you logged in?)")
        return
        
    submissions_header = sidebar.find("h4", string="Your submissions")
    if not submissions_header:
        console.print(f"[cyan]Task {task_id}: {title}[/cyan] -> [yellow]No submissions yet.[/yellow]")
        return
        
    subs = submissions_header.find_next_siblings("a")
    ac_sub = None
    for sub in subs:
        score_span = sub.find("span", class_="task-score")
        if score_span and "full" in score_span.get("class", []):
            ac_sub = sub
            break
            
    if ac_sub:
        time_text = ac_sub.contents[0].strip() if ac_sub.contents else ""
        href = ac_sub.get("href", "")
        console.print(f"[cyan]Task {task_id}: {title}[/cyan] -> [bold green][ACCEPTED][/bold green]")
        console.print(f"Last AC: {time_text}")
        console.print(f"Link: https://cses.fi{href}")
    else:
        # Check if there are any submissions
        if len(subs) > 0:
            last_sub = subs[0]
            time_text = last_sub.contents[0].strip() if last_sub.contents else ""
            href = last_sub.get("href", "")
            console.print(f"[cyan]Task {task_id}: {title}[/cyan] -> [bold red][NOT SOLVED YET][/bold red]")
            console.print(f"Last Attempt: {time_text}")
            console.print(f"Link: https://cses.fi{href}")
        else:
            console.print(f"[cyan]Task {task_id}: {title}[/cyan] -> [yellow]No submissions yet.[/yellow]")
