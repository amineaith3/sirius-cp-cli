CPP_TEMPLATE = """#include <bits/stdc++.h>
using namespace std;

void solve() {
    // Write your solution here
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int t = 1;
    {test_case_read}
    while (t--) {
        solve();
    }
    return 0;
}
"""

PY_TEMPLATE = """import sys

def solve():
    # Write your solution here
    print("YES")

if __name__ == '__main__':
    input_data = sys.stdin.read().split()
    if input_data:
        t = int(input_data[0])
        # Fast input parsing logic goes here
        for _ in range(t):
            solve()
"""

MATHJAX_BOILERPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codeforces Problem</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; background: #fff;}
        .problem-statement { margin-top: 20px; }
        .header { text-align: center; margin-bottom: 2em; border-bottom: 1px solid #eee; padding-bottom: 1em; }
        .title { font-size: 24px; font-weight: bold; color: #222;}
        .property-title { font-weight: bold; }
        .input-specification, .output-specification, .note { margin-top: 2em; }
        .section-title { font-size: 18px; font-weight: bold; margin-bottom: 0.5em; border-bottom: 1px solid #eee; padding-bottom: 5px;}
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: Consolas, monospace; }
        .sample-tests { margin-top: 2em; }
        .sample-test .input, .sample-test .output { border: 1px solid #ccc; margin-bottom: 1em; border-radius: 4px; overflow: hidden; }
        .sample-test .title { background: #eee; padding: 5px 10px; font-size: 14px; font-weight: bold; border-bottom: 1px solid #ccc;}
        .sample-test pre { margin: 0; border-radius: 0; border: none; }
        img { max-width: 100%; height: auto; display: block; margin: 10px auto; }
        .tex-font-style-tt { font-family: Consolas, monospace; background: #f8f8f8; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }
    </style>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
          tex2jax: {inlineMath: [['$$$','$$$']], displayMath: [['$$$$$$','$$$$$$']]}
        });
    </script>
    <script type="text/javascript" async
      src="https://assets.codeforces.com/mathjax/MathJax.js?config=TeX-AMS_HTML-full">
    </script>
</head>
<body>
{content}
</body>
</html>
"""
