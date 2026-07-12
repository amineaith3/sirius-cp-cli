# Sirius CP CLI 🚀

**Sirius CP CLI** is the ultimate unified local environment for competitive programming. Built in Python with Typer and Rich, it completely eliminates the friction of context-switching between your browser, your code editor, and the grading servers. It natively supports both **Codeforces** and the **CSES Problem Set** through two distinct modules.

---

## 🌟 Modules

### 1. The Codeforces Module (`sirius-cf`)
- **The `next` Tracker**: Type `sirius-cf next 1200` to instantly find an unsolved problem matching your target rating, skipping everything you've already solved.
- **Offline-First Fetching**: Scrapes the problem statement, injects MathJax for perfect offline math rendering, and extracts sample test cases.
- **Native & WSL Testing**: Instantly compiles your C++ code natively (or via WSL if on Windows) and runs it against local test cases with line-by-line mismatch diffing.
- **Live Direct Submission**: Authenticates via your session cookie to bypass Cloudflare, submits your solution directly to the Codeforces judging servers, and **polls the live grading status in real-time** right in your terminal.

### 2. The CSES Module (`sirius-cses`)
- **Categorized Workspace Architecture**: Keeps your code perfectly organized. When you fetch a problem, it automatically creates a beautiful, human-readable directory structure like: `~/Desktop/cses-offline/Introductory Problems/1068--Weird-Algorithm/`.
- **The Living Dashboard**: Run `sirius-cses sync` to build a local index of all 400 problems. A `stats.txt` file is dynamically generated in every category folder, tracking your `[x]` solved progress completely offline.
- **Smart Category Navigation**: Run `sirius-cses next graph` to automatically fetch your next unsolved problem in the Graph Algorithms category using fuzzy string matching.
- **Bulk Offline Mirror**: Run `sirius-cses download-all` to safely mirror all 400 problems, test cases, and HTML statements locally to your machine.
- **Live Direct Submission**: Submits your C++ code to the CSES grading server, polls the result table, and automatically updates your local dashboard upon an `ACCEPTED` verdict.

---

## 🛠️ Setup & Installation

### Requirements
- Python 3.9+
- C++ Compiler (`g++`) configured natively or via WSL.

### Installation
Clone this repository and install it globally in editable mode. Because the suite uses a Monorepo architecture, this single installation will give you access to both the `sirius-cf` and `sirius-cses` commands.

```bash
git clone https://github.com/amineaith3/CF-cli.git sirius-cp-cli
cd sirius-cp-cli
pip install -e .
```

---

## ⚙️ Configuration & Initialization

Once installed, you need to configure your workspaces and authentication cookies. You can configure the CLI to automatically dump your problems and code into a specific directory, ensuring your terminal doesn't get cluttered.

### Initializing Codeforces
```bash
sirius-cf init
```
It will prompt you for:
1. **Handle**: Used to track solved problems.
2. **Default Language**: `cpp` or `py`.
3. **CF_COOKIE**: Your Codeforces session string (Required for submitting).
4. **Custom C++ Template Path**: (Optional) Path to your personal C++ boilerplate.
5. **Workspace Path**: The absolute path where `sirius-cf` should download all contests. (Defaults to `~/Desktop/cf-offline`).

### Initializing CSES
```bash
sirius-cses init
```
It will prompt you for:
1. **Handle**: Your CSES username.
2. **Default Language**: `cpp` or `py`.
3. **CSES_COOKIE**: Your `PHPSESSID` cookie string (Required for submitting and syncing).
4. **Custom C++ Template Path**: (Optional).
5. **Workspace Path**: The absolute path where `sirius-cses` should build your Categorized Dashboard. (Defaults to `~/Desktop/cses-offline`).

> [!CAUTION]
> **Security Warning:** Your `CF_COOKIE` and `CSES_COOKIE` strings grant full access to your accounts. **Never** share these strings with anyone, and **never** commit your `.env` or configuration JSON files to a public GitHub repository.

---

## 💻 Codeforces Quickstart

**1. Find your next problem:**
```bash
sirius-cf next 800
```
**2. Fetch a specific problem (e.g. 1800B):**
```bash
sirius-cf fetch 1800 B
```
**3. Test your solution:**
```bash
sirius-cf test 1800 B
```
**4. Submit and track live grading:**
```bash
sirius-cf submit 1800 B
```

---

## 🌲 CSES Quickstart

**1. Build your local dashboard:**
*This maps all 400 problems and updates your `stats.txt` tracking files.*
```bash
sirius-cses sync
```
**2. Fetch your next Graph problem:**
```bash
sirius-cses next graph
```
**3. Test your Weird Algorithm solution:**
```bash
sirius-cses test 1068
```
**4. Submit to CSES:**
*If your solution is ACCEPTED, your `stats.txt` will automatically update!*
```bash
sirius-cses submit 1068
```
**5. Generate a report:**
*Get the exact timestamp and link to your last successful submission for a task.*
```bash
sirius-cses report 1068
```

---

## ⚠️ Ethical Use & Disclaimer
This CLI tool is designed strictly as a local workflow optimization tool to help you fetch problems and submit your **own, original code** without leaving your terminal. 

- **Be Polite:** Do not modify the script to spam or DDoS the servers. The `fetch` commands cache data locally by design. The `download-all` feature is safely rate-limited.
- **Fair Play:** Do not use this tool in conjunction with automated AI solvers during live, rated contests. 
- **Liability:** The authors of this tool are not responsible for any account bans or penalties resulting from the misuse of this CLI to violate community rules.
