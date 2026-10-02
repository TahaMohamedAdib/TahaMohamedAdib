from pathlib import Path
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

USERNAME = "TahaMohamedAdib"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"

r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 GitHubProfileReadme/1.0"}, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

days = {}
for node in soup.select("[data-date]"):
    d = node.get("data-date")
    if not d:
        continue
    try:
        level = int(node.get("data-level") or 0)
    except ValueError:
        level = 0
    days[d] = {"date": d, "level": max(0, min(4, level))}

if not days:
    raise SystemExit("No contribution cells found in GitHub response.")

payload = {
    "username": USERNAME,
    "fetched_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    "days": [days[k] for k in sorted(days)],
}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Wrote {len(days)} contribution days.")
