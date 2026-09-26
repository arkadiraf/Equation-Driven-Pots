"""Headless run of the woven-pot regression check (tests/woven-regression.js).

    python tests/run_regression.py

Serves the project folder on a local port, opens EquationDrivenWovenPots.html?regression in
headless Chrome (or Edge) with a throwaway profile, and prints the result panel. Exit code 0
when every case passes, 1 on any FAIL / NEW, 2 when no result came back. Needs an internet
connection: the page loads three.js and Manifold from their CDNs, exactly as it does normally.
"""
import functools
import http.server
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_browser():
    for b in BROWSERS:
        if os.path.isfile(b) or shutil.which(b):
            return b
    sys.exit("No Chrome/Edge found - open EquationDrivenWovenPots.html?regression in a browser instead.")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    # Diffs contain arrows; a Windows console's default code page cannot print them.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    handler = functools.partial(QuietHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/EquationDrivenWovenPots.html?regression"
    profile = tempfile.mkdtemp(prefix="woven-regression-")
    try:
        # --virtual-time-budget lets the page run its (synchronous, CPU-bound) cases to the end
        # before the DOM is dumped; the result panel is then read out of that DOM.
        dom = subprocess.run(
            [find_browser(), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
             "--virtual-time-budget=900000", "--dump-dom", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900).stdout
    finally:
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)

    summary = re.search(r"Regression: (\d+) passed, (\d+) failed, (\d+) new", dom)
    if not summary:
        print("No regression result in the page (did the geometry engine load?)")
        return 2
    for row in re.findall(r"<div><b style=\"color:[^\"]+\">(.*?)</div>", dom, re.S):
        row = re.sub(r"<span[^>]*>\d+ ms</span>", "", row)   # timings are meaningless under virtual time
        text = unescape(re.sub(r"<br>", "\n    ", re.sub(r"<(?!br)[^>]+>", "", row))).replace("\xa0", " ")
        print(text)
    passed, failed, new = map(int, summary.groups())
    print(f"\n{passed} passed, {failed} failed, {new} new")
    return 0 if failed == 0 and new == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
