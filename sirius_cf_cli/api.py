import requests
from typing import List, Dict, Set
from rich.console import Console

console = Console()
CF_API_BASE = "https://codeforces.com/api"

def get_user_solved_problems(handle: str) -> Set[str]:
    """Returns a set of solved problems in the format 'CONTEST_ID-PROBLEM_INDEX' (e.g. '1800-A')."""
    if not handle:
        return set()
        
    url = f"{CF_API_BASE}/user.status?handle={handle}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("status") != "OK":
            console.print(f"[yellow]CF API Error for {handle}: {data.get('comment')}[/yellow]")
            return set()
            
        solved = set()
        for submission in data.get("result", []):
            if submission.get("verdict") == "OK":
                prob = submission.get("problem", {})
                contest_id = prob.get("contestId")
                index = prob.get("index")
                if contest_id and index:
                    solved.add(f"{contest_id}-{index}")
        return solved
    except Exception as e:
        console.print(f"[red]Error fetching user status:[/red] {e}")
        return set()

def get_next_problem_by_rating(target_rating: int, solved: Set[str]) -> tuple[str, str]:
    """Returns (contest_id, problem_index) for an unsolved problem with the target rating."""
    url = f"{CF_API_BASE}/problemset.problems"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("status") != "OK":
            console.print(f"[red]CF API Error: {data.get('comment')}[/red]")
            return None, None
            
        problems = data.get("result", {}).get("problems", [])
        for prob in problems:
            # We skip non-standard contest IDs if desired, but here we just check rating
            if prob.get("rating") == target_rating:
                contest_id = str(prob.get("contestId"))
                index = str(prob.get("index"))
                prob_key = f"{contest_id}-{index}"
                
                if prob_key not in solved:
                    return contest_id, index
                    
        return None, None
    except Exception as e:
        console.print(f"[red]Error fetching problems:[/red] {e}")
        return None, None
