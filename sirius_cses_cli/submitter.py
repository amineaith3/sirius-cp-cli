import os
import re
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console

from sirius_cses_cli.config import get_cookie
from sirius_cses_cli.api import get_problem_path, sync_index

console = Console()

def get_cses_language_id(lang: str) -> str:
    # Based on our scratch script, CSES language values:
    # C++ is "C++"
    # Python3 is "Python3"
    # Wait, the value is just the text name usually. Let's map it.
    if lang == "cpp":
        return "C++"
    if lang == "py":
        return "Python3"
    return "C++"

def submit_solution(task_id: str, lang: str):
    task_id = re.sub(r'[^a-zA-Z0-9_-]', '', task_id)
    folder_name = get_problem_path(task_id)
    cookie_str = get_cookie()
    
    if not cookie_str:
        console.print("[bold red][FAILED] CSES_COOKIE not found. Run sirius-cses init or set it in .env[/bold red]")
        return
        
    # Extract PHPSESSID from cookie string if it's full string
    phpsessid = ""
    if "PHPSESSID=" in cookie_str:
        for part in cookie_str.split(";"):
            if part.strip().startswith("PHPSESSID="):
                phpsessid = part.split("=")[1].strip()
    else:
        phpsessid = cookie_str.strip()
        
    cookies = {"PHPSESSID": phpsessid}
    
    ext = "cpp" if lang == "cpp" else "py"
    src_file = os.path.join(folder_name, f"main.{ext}")
    
    if not os.path.exists(src_file):
        console.print(f"[bold red][FAILED] {src_file} not found.[/bold red]")
        return

    submit_url = f"https://cses.fi/problemset/submit/{task_id}/"
    
    console.print(f"Preparing to submit {src_file} to CSES Task {task_id}...")
    
    with requests.Session() as session:
        # Step 1: Fetch CSRF token
        with console.status("Fetching CSRF token..."):
            try:
                res = session.get(submit_url, cookies=cookies, timeout=10)
                res.raise_for_status()
            except requests.RequestException as e:
                console.print(f"[bold red][FAILED] Network Error: {e}[/bold red]")
                return
                
        soup = BeautifulSoup(res.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf_token"})
        if not csrf_input:
            console.print("[bold red][FAILED] Could not find csrf_token. Are you logged in? Check your PHPSESSID.[/bold red]")
            return
            
        csrf_token = csrf_input["value"]
        
        # Step 2: Submit form
        with console.status("Submitting code..."):
            with open(src_file, "r", encoding="utf-8") as f:
                file_content = f.read()
                
            data = {
                "csrf_token": csrf_token,
                "task": task_id,
                "lang": get_cses_language_id(lang),
                "option": "C++17" if lang == "cpp" else "",
                "type": "course",
                "target": "problemset"
            }
            files = {
                "file": (f"main.{ext}", file_content, "text/plain")
            }
            
            try:
                post_url = "https://cses.fi/course/send.php"
                post_res = session.post(post_url, data=data, files=files, cookies=cookies, timeout=10, allow_redirects=True)
                post_res.raise_for_status()
            except requests.RequestException as e:
                console.print(f"[bold red][FAILED] Submission failed: {e}[/bold red]")
                return
                
        # In CSES, submission redirects to /problemset/result/{submission_id}/
        result_url = post_res.url
        if "submit" in result_url:
            console.print("[bold red][FAILED] Submission failed. Server rejected the form. Did you set the right language or cookie?[/bold red]")
            return
            
        console.print(f"[bold green]Submission sent! Tracking live grading at {result_url}[/bold green]")
        
        # Step 3: Polling Loop
        max_attempts = 60
        attempts = 0
        poll_error_shown = False
        
        with console.status("[cyan]In queue...[/cyan]") as status:
            while attempts < max_attempts:
                time.sleep(2)
                attempts += 1
                try:
                    poll_res = session.get(result_url, cookies=cookies, timeout=10)
                    poll_res.raise_for_status()
                    poll_error_shown = False
                except requests.RequestException:
                    if not poll_error_shown:
                        console.print("[yellow]Warning: Network lag while checking result... retrying[/yellow]")
                        poll_error_shown = True
                    continue
                    
                poll_soup = BeautifulSoup(poll_res.text, "html.parser")
                
                # In CSES results page, there's a table with the status
                # Example: <td class="test-status"><span class="test-result ready">ACCEPTED</span></td>
                # Or <span class="task-score icon full"></span>
                # The easiest way is to find the overall status block
                # There is usually a summary table
                summary_table = poll_soup.find("table", class_="summary-table")
                if summary_table:
                    status_text = ""
                    result_text = ""
                    for row in summary_table.find_all("tr"):
                        tds = row.find_all("td")
                        if len(tds) >= 2:
                            if "Status:" in tds[0].text:
                                status_text = tds[1].text.strip()
                            elif "Result:" in tds[0].text:
                                result_text = tds[1].text.strip()
                            
                    if status_text:
                        if "TESTING" in status_text.upper() or "PENDING" in status_text.upper() or "COMPILE" in status_text.upper():
                            status.update(f"[cyan]Status: {status_text}...[/cyan]")
                        elif "READY" in status_text.upper() and result_text:
                            final_result = result_text
                            if "ACCEPTED" in final_result.upper():
                                console.print(f"\n[bold green][SUCCESS] {final_result}[/bold green]")
                                # Auto-sync index to update stats.txt
                                sync_index()
                            else:
                                console.print(f"\n[bold red][FAILED] {final_result}[/bold red]")
                            return
                        elif "ERROR" in status_text.upper():
                            console.print(f"[bold red][FAILED] {status_text}[/bold red]")
                            return
                else:
                    # Alternative check if summary-table doesn't exist
                    status.update("[cyan]Waiting for grading...[/cyan]")

        console.print("[yellow]Polling timed out after 2 minutes. Check results in browser.[/yellow]")
