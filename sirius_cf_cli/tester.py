import os
import re
import sys
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

def compare_outputs(expected_file: str, actual_output: str):
    with open(expected_file, 'r', encoding='utf-8') as f:
        expected = f.read().strip().splitlines()
    actual = actual_output.strip().splitlines()
    
    expected = [line.strip() for line in expected if line.strip()]
    actual = [line.strip() for line in actual if line.strip()]
    
    return expected == actual, expected, actual

def test_solution(contest_id: str, problem_id: str, lang: str):
    contest_id = re.sub(r'[^a-zA-Z0-9]', '', contest_id)
    problem_id = re.sub(r'[^a-zA-Z0-9]', '', problem_id)
    folder_name = f"{contest_id}-{problem_id}"
    if not os.path.exists(folder_name):
        console.print(f"[bold red]Folder {folder_name} not found. Run fetch first.[/bold red]")
        return False

    is_windows = platform.system() == "Windows"
    
    if lang == "cpp":
        # Check native g++
        try:
            subprocess.run(["g++", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            has_native_gpp = True
        except FileNotFoundError:
            has_native_gpp = False
            
        if has_native_gpp:
            console.print("[cyan]Compiling C++ code with native g++...[/cyan]")
            compile_cmd = ["g++", "main.cpp", "-o", "main"]
            run_cmd_list = ["./main"] if not is_windows else ["main.exe"]
        elif is_windows:
            console.print("[cyan]Compiling C++ code via WSL...[/cyan]")
            compile_cmd = ["wsl", "g++", "main.cpp", "-o", "main"]
            run_cmd_list = ["wsl", "./main"]
        else:
            console.print("[bold red]g++ not found in PATH.[/bold red]")
            return False

        with console.status("Compiling..."):
            res = subprocess.run(compile_cmd, cwd=folder_name, shell=False, capture_output=True, text=True)
        
        if res.returncode != 0:
            console.print("[bold red]Compilation Error:[/bold red]")
            console.print(Panel(res.stderr, title="g++ stderr", border_style="red"))
            return False
            
    elif lang == "py":
        run_cmd_list = [sys.executable, "main.py"]
    else:
        console.print(f"[bold red]Unsupported language: {lang}[/bold red]")
        return False

    i = 1
    passed_all = True
    while True:
        in_file = os.path.join(folder_name, f"input{i}.txt")
        out_file = os.path.join(folder_name, f"output{i}.txt")
        if not os.path.exists(in_file):
            if i == 1:
                console.print("[yellow]No test cases found.[/yellow]")
            break
            
        console.print(f"\n[bold]Test {i}[/bold]")
        with open(in_file, "r", encoding="utf-8") as f:
            inp_data = f.read()
            
        try:
            res = subprocess.run(run_cmd_list, cwd=folder_name, input=inp_data, text=True, capture_output=True, shell=False, timeout=5)
            if res.returncode != 0:
                console.print(f"[bold red][RE] Runtime Error on Test {i}[/bold red]")
                console.print(Panel(res.stderr, title="stderr", border_style="red"))
                passed_all = False
            else:
                match, expected, actual = compare_outputs(out_file, res.stdout)
                if match:
                    console.print(f"[bold green][OK] [AC] Accepted[/bold green]")
                else:
                    passed_all = False
                    console.print(f"[bold red][FAILED] [WA] Wrong Answer[/bold red]")
                    
                    max_len = max(len(expected), len(actual))
                    for idx in range(max_len):
                        exp_val = expected[idx] if idx < len(expected) else "<EOF>"
                        act_val = actual[idx] if idx < len(actual) else "<EOF>"
                        if exp_val != act_val:
                            console.print(f"\n[bold yellow]Mismatch at Line {idx + 1}:[/bold yellow]")
                            console.print(f"[green]Expected:[/green] {exp_val}")
                            console.print(f"[red]Actual  :[/red] {act_val}")
                            break
        except subprocess.TimeoutExpired:
            console.print(f"[bold yellow][TLE] Time Limit Exceeded on Test {i}[/bold yellow]")
            passed_all = False
            
        i += 1

    if passed_all and i > 1:
        console.print("\n[bold green][SUCCESS] All test cases passed! Great job![/bold green]")
        
    # Cleanup executable
    if lang == "cpp":
        for exe_name in ["main", "main.exe"]:
            exe_path = os.path.join(folder_name, exe_name)
            if os.path.exists(exe_path):
                try:
                    os.remove(exe_path)
                except Exception:
                    pass
                
    return passed_all
