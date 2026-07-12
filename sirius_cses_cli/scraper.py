import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
from rich.console import Console

from sirius_cses_cli.templates import MATHJAX_BOILERPLATE, CPP_TEMPLATE, PY_TEMPLATE
from sirius_cses_cli.config import get_template_cpp_path
from sirius_cses_cli.api import get_problem_path

console = Console()

def fetch_problem(task_id: str):
    task_id = re.sub(r'[^a-zA-Z0-9_-]', '', task_id)
    folder_name = get_problem_path(task_id)
    
    if os.path.exists(folder_name) and os.path.exists(os.path.join(folder_name, "problem.html")):
        console.print(f"[yellow]Task {task_id} already exists in {folder_name}. Skipping download.[/yellow]")
        return
        
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    url = f"https://cses.fi/problemset/task/{task_id}"
    
    with console.status(f"Fetching problem from: {url}"):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            console.print(f"[bold red][FAILED] Error fetching problem: {e}[/bold red]")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="content")
        if not content_div:
            # Maybe it's an error page
            console.print(f"[bold red][FAILED] Could not find problem content. Is the ID correct?[/bold red]")
            return
            
        # Strip all hrefs to make nothing clickable
        for a_tag in content_div.find_all("a"):
            if "href" in a_tag.attrs:
                del a_tag.attrs["href"]
                
        # Extract problem title
        title_text = f"Task {task_id}"
        title_block = soup.find("div", class_="title-block")
        if title_block:
            h1 = title_block.find("h1")
            if h1:
                title_text = h1.text.strip()
                
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSES - {title_text}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; background: #fff;}}
        .problem-statement {{ margin-top: 20px; }}
        pre {{ background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; }}
        code {{ font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; background: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-size: 85%; }}
        .math {{ font-family: "Latin Modern Math", "Cambria Math", "Asana Math", serif; }}
        /* Disable any stray links */
        a {{ color: inherit; text-decoration: none; cursor: default; pointer-events: none; }}
    </style>
    {MATHJAX_BOILERPLATE}
</head>
<body>
    <div class="problem-statement">
        <h1>{title_text}</h1>
        {content_div.prettify()}
    </div>
</body>
</html>
"""
        with open(os.path.join(folder_name, "problem.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        
        console.print(f"[bold green][OK] Saved offline problem statement to {folder_name}/problem.html[/bold green]")
        
        # Extract Test Cases
        # In CSES, inputs and outputs are typically in <pre> tags alternating.
        pres = soup.find_all("pre")
        
        test_case_count = 0
        if len(pres) % 2 == 0 and len(pres) > 0:
            for i in range(0, len(pres), 2):
                in_text = pres[i].text.strip()
                out_text = pres[i+1].text.strip()
                test_case_count += 1
                
                with open(os.path.join(folder_name, f"input{test_case_count}.txt"), "w", encoding="utf-8") as f:
                    f.write(in_text + "\n")
                with open(os.path.join(folder_name, f"output{test_case_count}.txt"), "w", encoding="utf-8") as f:
                    f.write(out_text + "\n")
        elif len(pres) == 1:
            # Only one <pre>, maybe no output provided, or we can't parse easily. Just save it as input.
            with open(os.path.join(folder_name, f"input1.txt"), "w", encoding="utf-8") as f:
                f.write(pres[0].text.strip() + "\n")
            test_case_count = 1
            console.print("[yellow]Warning: Found only 1 <pre> block. Saved as input1.txt, but output1.txt is missing.[/yellow]")
            
        console.print(f"[bold green][OK] Saved {test_case_count} test case(s).[/bold green]")
        
        # Scaffold Code
        cpp_file = os.path.join(folder_name, "main.cpp")
        if not os.path.exists(cpp_file):
            custom_template = get_template_cpp_path()
            if custom_template and os.path.isfile(custom_template):
                try:
                    shutil.copy(custom_template, cpp_file)
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not copy custom template ({e}). Using default.[/yellow]")
                    write_default_template(cpp_file)
            else:
                write_default_template(cpp_file)
                
            console.print(f"[bold green][OK] Scaffolded starter code in {folder_name}/[/bold green]")

def write_default_template(cpp_file: str):
    # CSES typically has 1 test case per file (no test cases loop).
    # "test cases" isn't a common keyword in CSES inputs like CF.
    # Most CSES problems are single test case.
    template = CPP_TEMPLATE.replace("// test_case_read", "int t = 1;\\n    // cin >> t;\\n    while (t--) {\\n        solve();\\n    }")
    with open(cpp_file, "w", encoding="utf-8") as f:
        f.write(template)
