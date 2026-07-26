"""Regenerate the ASCII language bars between the stack section markers."""
import json
import os
import urllib.request

USER = "zacknguyn"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
WIDTH = 20
TOP_N = 8


def get(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return json.load(r)


repos = [r for r in get(f"{API}/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
totals = {}
for repo in repos:
    for lang, n in get(repo["languages_url"]).items():
        totals[lang] = totals.get(lang, 0) + n

top = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP_N]
total = sum(n for _, n in top) or 1

lines = []
for lang, n in top:
    filled = round(WIDTH * n / total)
    bar = "█" * filled + "░" * (WIDTH - filled)
    lines.append(f"{lang:<12}{bar}  {100 * n / total:5.1f}%")
if not lines:
    lines.append("no source detected (yet)")

block = "```text\n" + "\n".join(lines) + "\n```"
START, END = "<!--START_SECTION:stack-->", "<!--END_SECTION:stack-->"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
head, rest = readme.split(START)
_, tail = rest.split(END)
new = f"{head}{START}\n{block}\n{END}{tail}"

if new != readme:
    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("README updated")
else:
    print("No change")
