from pathlib import Path
import json
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup

USERNAME = "TahaMohamedAdib"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"

r = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0 GitHubProfileReadme/1.0"},
    timeout=30,
)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

days = []
for node in soup.select("[data-date]"):
    d = node.get("data-date")
    if not d:
        continue
    count = node.get("data-count")
    level = node.get("data-level")
    if count is None:
        label = node.get("aria-label", "")
        nums = "".join(ch if ch.isdigit() else " " for ch in label).split()
        count = nums[0] if nums else "0"
    try:
        c = int(count or 0)
    except ValueError:
        c = 0
    try:
        lv = int(level) if level is not None else min(4, c)
    except ValueError:
        lv = 0
    days.append({"date": d, "count": c, "level": lv})

by_date = {x["date"]: x for x in days}
days = [by_date[k] for k in sorted(by_date)]
if not days:
    raise SystemExit("No contribution cells found in GitHub response.")

counts = {x["date"]: x["count"] for x in days}
positive = sorted(
    datetime.strptime(k, "%Y-%m-%d").date()
    for k, v in counts.items() if v > 0
)

def streak_ending_at(end):
    n = 0
    cur = end
    while counts.get(cur.isoformat(), 0) > 0:
        n += 1
        cur -= timedelta(days=1)
    return n

today = date.today()
current = streak_ending_at(today)
if current == 0:
    current = streak_ending_at(today - timedelta(days=1))

longest = run = 0
prev = None
for d in positive:
    run = run + 1 if prev and d == prev + timedelta(days=1) else 1
    longest = max(longest, run)
    prev = d

best = max(days, key=lambda x: x["count"])
OUT.write_text(json.dumps({
    "username": USERNAME,
    "fetched_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    "days": days,
    "stats": {
        "total": sum(x["count"] for x in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
    }
}, indent=2), encoding="utf-8")
print(f"Wrote {len(days)} contribution days.")
