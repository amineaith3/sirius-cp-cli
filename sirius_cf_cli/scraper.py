import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress

from sirius_cf_cli.templates import MATHJAX_BOILERPLATE, CPP_TEMPLATE, PY_TEMPLATE
from sirius_cf_cli.config import get_template_cpp_path

console = Console()

def fetch_problem(contest_id: str, problem_id: str):
    contest_id = re.sub(r'[^a-zA-Z0-9]', '', contest_id)
    problem_id = re.sub(r'[^a-zA-Z0-9]', '', problem_id)
    folder_name = f"{contest_id}-{problem_id}"
    os.makedirs(folder_name, exist_ok=True)
    
    url = f"https://codeforces.com/problemset/problem/{contest_id}/{problem_id}"
    console.print(f"[bold blue]Fetching problem from:[/bold blue] {url}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        page_html = response.text
    except Exception as e:
        console.print(f"[bold red]Error fetching page:[/bold red] {e}")
        return False

    soup = BeautifulSoup(page_html, 'html.parser')
    problem_div = soup.find('div', class_='problem-statement')
    
    if not problem_div:
        console.print("[bold red]Could not find the problem statement. Problem might not exist.[/bold red]")
        return False

    # Download images and rewrite src
    img_tags = problem_div.find_all('img')
    if img_tags:
        with Progress() as progress:
            task = progress.add_task("[green]Downloading images...", total=len(img_tags))
            for i, img in enumerate(img_tags):
                src = img.get('src')
                if not src:
                    progress.advance(task)
                    continue
                    
                full_img_url = urljoin(url, src)
                ext = os.path.splitext(full_img_url.split('?')[0])[1] or '.png'
                local_img_name = f"image{i+1}{ext}"
                local_img_path = os.path.join(folder_name, local_img_name)
                
                try:
                    img_res = requests.get(full_img_url, headers=headers, stream=True, timeout=10)
                    img_res.raise_for_status()
                    with open(local_img_path, 'wb') as f:
                        for chunk in img_res.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    img['src'] = local_img_name
                except Exception as e:
                    console.print(f"[yellow]Failed to download image {full_img_url}:[/yellow] {e}")
                progress.advance(task)

    # Save problem.html
    html_content = MATHJAX_BOILERPLATE.replace('{content}', str(problem_div))
    with open(os.path.join(folder_name, "problem.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    console.print(f"[green][OK] Saved offline problem statement to {folder_name}/problem.html[/green]")

    # Extract inputs and outputs for testing
    inputs = problem_div.find_all('div', class_='input')
    outputs = problem_div.find_all('div', class_='output')

    saved_samples = 0
    for i, (inp_div, outp_div) in enumerate(zip(inputs, outputs), 1):
        inp_pre = inp_div.find('pre')
        outp_pre = outp_div.find('pre')
        if not inp_pre or not outp_pre:
            continue
            
        inp_text = inp_pre.get_text(separator='\n').strip()
        outp_text = outp_pre.get_text(separator='\n').strip()
        
        inp_text = re.sub(r'\n+', '\n', inp_text)
        outp_text = re.sub(r'\n+', '\n', outp_text)
        
        with open(os.path.join(folder_name, f"input{i}.txt"), "w", encoding="utf-8") as f:
            f.write(inp_text + "\n")
        with open(os.path.join(folder_name, f"output{i}.txt"), "w", encoding="utf-8") as f:
            f.write(outp_text + "\n")
        saved_samples += 1
            
    console.print(f"[green][OK] Saved {saved_samples} test case(s).[/green]")

    # Scaffolding
    cpp_file = os.path.join(folder_name, "main.cpp")
    if not os.path.exists(cpp_file):
        custom_template_path = get_template_cpp_path()
        if custom_template_path and os.path.isfile(custom_template_path):
            with open(custom_template_path, "r", encoding="utf-8") as tf:
                cpp_content = tf.read()
        else:
            # Dynamic cin >> t generation
            problem_text = problem_div.get_text().lower()
            if "test case" in problem_text:
                cpp_content = CPP_TEMPLATE.replace("{test_case_read}", "cin >> t;")
            else:
                cpp_content = CPP_TEMPLATE.replace("{test_case_read}", "// cin >> t;")
                
        with open(cpp_file, "w", encoding="utf-8") as f:
            f.write(cpp_content)
    
    py_file = os.path.join(folder_name, "main.py")
    if not os.path.exists(py_file):
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(PY_TEMPLATE)
            
    console.print(f"[green][OK] Scaffolded starter code in {folder_name}/[/green]")
    return True
