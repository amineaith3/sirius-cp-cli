import os
import re
import sys
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel

from sirius_cses_cli.api import get_problem_path

console = Console()

def compare_outputs(expected_file: str, actual_output: str) -> tuple[bool, str, str]:
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = f.read().strip().splitlines()
    
    actual = actual_output.strip().splitlines()
    
    if len(expected) != len(actual):
        return False, f"{len(expected)} lines", f"{len(actual)} lines"
        
    for i, (exp_line, act_line) in enumerate(zip(expected, actual)):
        if exp_line.strip() != act_line.strip():
            return False, exp_line.strip(), act_line.strip()
            
    return True, "", ""

def test_solution(task_id: str, lang: str = "cpp"):
    task_id = re.sub(r'[^a-zA-Z0-9_-]', '', task_id)
    folder_name = get_problem_path(task_id)
    
    if not os.path.exists(folder_name):
        console.print(f"[bold red][FAILED] Folder {folder_name} not found. Did you run fetch first?[/bold red]")
        return False
        
    is_windows = platform.system() == "Windows"
    use_wsl = False
    
    if lang == "cpp":
        src_file = os.path.join(folder_name, "main.cpp")
        if not os.path.exists(src_file):
            console.print(f"[bold red][FAILED] {src_file} not found.[/bold red]")
            return
            
        if is_windows:
            try:
                subprocess.run(["g++", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("Native g++ not found on Windows. Falling back to WSL...")
                use_wsl = True
                
        compile_cmd = ["g++", "main.cpp", "-o", "main"]
        if use_wsl:
            compile_cmd = ["wsl"] + compile_cmd
            
        with console.status("Compiling C++ code..."):
            try:
                subprocess.run(compile_cmd, cwd=folder_name, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red][FAILED] Compilation Error:[/bold red]\n{e.stderr.decode()}")
                return
    elif lang == "py":
        src_file = os.path.join(folder_name, "main.py")
        if not os.path.exists(src_file):
            console.print(f"[bold red][FAILED] {src_file} not found.[/bold red]")
            return

    # Run tests
    i = 1
    passed_all = True
    while True:
        in_file = os.path.join(folder_name, f"input{i}.txt")
        out_file = os.path.join(folder_name, f"output{i}.txt")
        
        if not os.path.exists(in_file) or not os.path.exists(out_file):
            break
            
        console.print(f"\nTest {i}")
        
        with open(in_file, "r", encoding="utf-8") as f:
            input_data = f.read()
            
        run_cmd = ["./main"] if not is_windows else ["main.exe"]
        if lang == "cpp" and use_wsl:
            run_cmd = ["wsl", "./main"]
        elif lang == "py":
            run_cmd = [sys.executable, "main.py"]
            
        try:
            res = subprocess.run(run_cmd, cwd=folder_name, input=input_data, text=True, capture_output=True, check=True)
            match, expected, actual = compare_outputs(out_file, res.stdout)
            if match:
                console.print("[bold green][OK] [AC] Accepted[/bold green]")
            else:
                console.print("[bold red][FAILED] [WA] Wrong Answer[/bold red]")
                
                # Find mismatch line roughly (we compare line by line in compare_outputs, so we just show the first mismatch)
                # To get the actual line number, we need a slightly different compare function, but let's just print the expected vs actual from the tuple
                console.print(f"\nMismatch:")
                console.print(f"Expected: {expected}")
                console.print(f"Actual  : {actual}")
                passed_all = False
                
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][FAILED] Runtime Error:[/bold red]\n{e.stderr}")
            passed_all = False
            
        i += 1

    if passed_all and i > 1:
        console.print("\n[bold green][SUCCESS] All test cases passed! Great job![/bold green]")
        
    # Cleanup executable
    if lang == "cpp":
        for exe_name in ["main", "main.exe"]:
            exe_path = os.path.join(folder_name, exe_name)
            if os.path.isfile(exe_path):
                try:
                    os.remove(exe_path)
                except Exception:
                    pass
