# Sirius CF-CLI 🚀

**Sirius CF-CLI** is the ultimate local environment for Codeforces competitive programming. Built in Python with Typer and Rich, it is designed to completely eliminate the friction of context-switching between your browser, your code editor, and the Codeforces grading servers.

## ✨ Features

- **The `next` Tracker**: Hooks directly into the Codeforces API. Type `sirius-cf next 1200` to instantly find an unsolved problem matching your target rating, skipping everything you've already solved.
- **Offline-First Fetching**: Scrapes the problem statement, downloads images locally, injects MathJax for perfect offline math rendering, and extracts sample test cases.
- **Smart Scaffolding**: Dynamically injects your custom C++ template and configures `cin >> t;` automatically based on the problem description.
- **Native & WSL Testing**: Instantly compiles your C++ code natively (or via WSL if on Windows) and runs it against local test cases with line-by-line mismatch diffing. Cleans up executables automatically.
- **Live Direct Submission**: Authenticates via your session cookie to bypass Cloudflare, submits your solution directly to the Codeforces judging servers, and **polls the live grading status in real-time** right in your terminal.

## 🛠️ Setup & Installation

### Requirements
- Python 3.9+
- C++ Compiler (`g++`) configured natively or via WSL.

### Installation
Clone this repository and install it globally in editable mode:
```bash
git clone https://github.com/amineaith3/CF-cli.git
cd CF-cli
pip install -e .
```

### Initialization
Once installed, run the initialization command from anywhere on your PC to set up your global configuration (`~/.sirius-cf-cli.json`):
```bash
sirius-cf init
```
It will prompt you for:
1. **Your Codeforces Handle** (Used for tracking your solved problems).
2. **Default Language** (`cpp` or `py`).
3. **CF_COOKIE** (Required for the `submit` command. You can leave this blank and use a local `.env` file instead).
4. **Custom C++ Template Path** (Optional absolute path to your personal C++ template).

### 🍪 Getting your `CF_COOKIE`
To use the `submit` command, the CLI needs to authenticate as you. It does this using your browser's session cookie.
1. Log into [Codeforces](https://codeforces.com) in your web browser.
2. Press `F12` to open Developer Tools and navigate to the **Network** tab.
3. Refresh the page and click on the very first request (usually `codeforces.com`).
4. Scroll down to **Request Headers** and find the `cookie:` field.
5. Copy the entire string (it will be very long and contain `JSESSIONID`, `cf_clearance`, etc.).

> [!CAUTION]
> **Security Warning:** Your `CF_COOKIE` grants full access to your Codeforces account. **Never** share this string with anyone, and **never** commit your `.env` or `~/.sirius-cf-cli.json` files to a public GitHub repository. If your cookie is compromised, others can submit code or change settings on your behalf!

## 💻 Usage

Because `sirius-cf` is installed globally, you can create a dedicated `CP-Vault` folder anywhere on your computer and run these commands!

### 1. Find Your Next Problem
Automatically finds your next unsolved problem for a given rating and scaffolds it.
```bash
sirius-cf next 800
```

### 2. Fetch a Specific Problem
If you already know the problem ID (e.g., Contest `1800`, Problem `B`), you can fetch it directly:
```bash
sirius-cf fetch 1800 B
```

### 3. Test Your Solution
Compiles your code and executes it against all local `input*.txt` files. Prints a clean line-by-line diff if you get a Wrong Answer.
```bash
sirius-cf test 1800 B
```

### 4. Submit & Track Live Grading
Authenticates your session, posts your file directly to the Codeforces grading server, and tracks the testing process in real-time!
```bash
sirius-cf submit 1800 B
```

---

## ⚠️ Ethical Use & Disclaimer
This CLI tool is designed strictly as a local workflow optimization tool to help you fetch problems and submit your **own, original code** without leaving your terminal. 

- **Be Polite:** Do not modify the script to spam or DDoS the Codeforces servers. The `fetch` command caches data locally by design.
- **Fair Play:** Do not use this tool in conjunction with automated AI solvers during live, rated contests. 
- **Liability:** The authors of this tool are not responsible for any account bans or penalties resulting from the misuse of this CLI to violate Codeforces community rules.
