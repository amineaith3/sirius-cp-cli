import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from rich.console import Console

import time
from sirius_cf_cli.config import get_cookie, get_handle

console = Console()

def submit_solution(contest_id: str, problem_id: str, lang: str):
    contest_id = re.sub(r'[^a-zA-Z0-9]', '', contest_id)
    problem_id = re.sub(r'[^a-zA-Z0-9]', '', problem_id)
    folder_name = f"{contest_id}-{problem_id}"
    if not os.path.exists(folder_name):
        console.print(f"[bold red]Folder {folder_name} not found.[/bold red]")
        return False

    cf_cookie = get_cookie()
    if not cf_cookie:
        console.print("[bold red]Error: CF_COOKIE not found.[/bold red]")
        console.print("Please set it in [bold]~/.sirius-cf-cli.json[/bold] using [cyan]sirius-cf init[/cyan] or via a local .env file.")
        return False

    # Language mapping
    lang_map = {
        "cpp": ("main.cpp", "89"), # C++20 (GCC 13-64)
        "py": ("main.py", "73")    # Python 3
    }
    
    if lang not in lang_map:
        console.print(f"[bold red]Unsupported language: {lang}[/bold red]")
        return False
        
    filename, program_type_id = lang_map[lang]
    file_path = os.path.join(folder_name, filename)
    
    if not os.path.exists(file_path):
        console.print(f"[bold red]Source file {file_path} not found.[/bold red]")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    console.print(f"[cyan]Preparing to submit {file_path} to {contest_id}{problem_id}...[/cyan]")

    # Session setup
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        'Cookie': cf_cookie,
        'Referer': f"https://codeforces.com/contest/{contest_id}/submit",
        'Origin': 'https://codeforces.com'
    }
    
    with requests.Session() as session:
        session.headers.update(headers)
    
        # 1. Fetch CSRF token from the contest submit page
        base_submit_url = f"https://codeforces.com/contest/{contest_id}/submit"
        
        with console.status("Fetching CSRF token..."):
            try:
                res = session.get(base_submit_url, timeout=10)
                res.raise_for_status()
            except Exception as e:
                console.print(f"[bold red]Failed to load submit page:[/bold red] {e}")
                return False
    
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Extract the dynamic action URL
        form = soup.find('form', class_='submit-form')
        action_url = base_submit_url
        if form and form.get('action'):
            action_url = urljoin(base_submit_url, form.get('action'))
            
        csrf_meta = soup.find('meta', {'name': 'X-Csrf-Token'})
        if not csrf_meta:
            console.print("[bold red]Failed to find CSRF token! Are you sure your CF_COOKIE is valid and not expired?[/bold red]")
            return False
            
        csrf_token = csrf_meta['content']
    
        # 2. Submit the form
        payload = {
            'csrf_token': csrf_token,
            'ftaa': 'c97x5e0q4p8v0w1n9m',
            'bfaa': 'f1b3f18fc1c546b08cea5c28ec2e1434',
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemIndex': problem_id,
            'programTypeId': program_type_id,
            'source': source_code,
            'tabSize': '4',
            '_tta': '176'
        }
    
        with console.status("Submitting solution..."):
            try:
                post_res = session.post(action_url, data=payload, allow_redirects=False, timeout=10)
                
                if post_res.status_code == 302:
                    console.print("\n[bold green]=======================================[/bold green]")
                    console.print("[bold green]          SUBMISSION SUCCESSFUL!       [/bold green]")
                    console.print("[bold green]=======================================[/bold green]")
                    console.print(f"Redirected to: {urljoin(base_submit_url, post_res.headers.get('Location', ''))}")
                    
                    handle = get_handle()
                    if not handle:
                        console.print("[yellow]Handle not set in config, cannot track live submission.[/yellow]")
                        return True
                    
                    console.print("\n[bold cyan]Tracking live submission status...[/bold cyan]")
                    time.sleep(2)
                    
                    max_attempts = 60
                    attempts = 0
                    last_test = -1
                    
                    poll_error_shown = False
                    with console.status("[cyan]In queue...[/cyan]") as status:
                        while attempts < max_attempts:
                            try:
                                api_url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=5"
                                res_api = requests.get(api_url, timeout=10)
                                data = res_api.json()
                                if data.get("status") == "OK":
                                    subs = data.get("result", [])
                                    target_sub = None
                                    for sub in subs:
                                        if str(sub.get("problem", {}).get("contestId")) == contest_id and \
                                           sub.get("problem", {}).get("index") == problem_id:
                                            target_sub = sub
                                            break
                                    
                                    if target_sub:
                                        verdict = target_sub.get("verdict")
                                        passed = target_sub.get("passedTestCount", 0)
                                        
                                        if not verdict or verdict == "TESTING":
                                            if passed > last_test:
                                                status.update(f"[cyan]Testing on test {passed + 1}...[/cyan]")
                                                last_test = passed
                                        else:
                                            status.stop()
                                            if verdict == "OK":
                                                console.print(f"[bold green][SUCCESS] Accepted on all {passed} tests![/bold green]")
                                            elif verdict == "WRONG_ANSWER":
                                                console.print(f"[bold red][FAILED] Wrong answer on test {passed + 1}[/bold red]")
                                            elif verdict == "TIME_LIMIT_EXCEEDED":
                                                console.print(f"[bold yellow][FAILED] Time limit exceeded on test {passed + 1}[/bold yellow]")
                                            elif verdict == "COMPILATION_ERROR":
                                                console.print(f"[bold red][FAILED] Compilation Error[/bold red]")
                                            elif verdict == "RUNTIME_ERROR":
                                                console.print(f"[bold red][FAILED] Runtime error on test {passed + 1}[/bold red]")
                                            else:
                                                console.print(f"[bold magenta]Verdict: {verdict.replace('_', ' ').capitalize()} on test {passed + 1}[/bold magenta]")
                                            return True
                            except Exception as poll_err:
                                if not poll_error_shown:
                                    status.update(f"[yellow]API poll failed ({poll_err}), retrying...[/yellow]")
                                    poll_error_shown = True
                                
                            attempts += 1
                            time.sleep(2)
                            
                    status.stop()
                    console.print("[yellow]Polling timed out. Check your Codeforces profile for the final result.[/yellow]")
                    return True
                else:
                    console.print(f"[bold red]Submission failed. Status code: {post_res.status_code}[/bold red]")
                    error_span = BeautifulSoup(post_res.text, 'html.parser').find('span', class_='error')
                    if error_span:
                        console.print(f"[bold yellow]Codeforces Error:[/bold yellow] {error_span.text}")
                    else:
                        console.print("[bold yellow]Unknown error. Make sure your CF_COOKIE is valid.[/bold yellow]")
                    return False
            except Exception as e:
                console.print(f"[bold red]Error during submission:[/bold red] {e}")
                return False
