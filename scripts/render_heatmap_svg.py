from pathlib import Path
import json
from datetime import date, datetime, timedelta
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

W, H = 860, 205
LEFT, TOP = 38, 34
CELL, GAP = 11, 3
PITCH = CELL + GAP
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
TEXT, BRIGHT, BG, BORDER = "#8b949e", "#c9d1d9", "#0d1117", "#30363d"

payload = json.loads(DATA.read_text(encoding="utf-8"))
items = {}
for x in payload.get("days", []):
    try:
        items[datetime.strptime(x["date"], "%Y-%m-%d").date()] = x
    except Exception:
        pass

end = max(items) if items else date.today()
start = end - timedelta(days=52 * 7 + end.weekday() + 1)
start -= timedelta(days=(start.weekday() + 1) % 7)

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>',
    '<style>@keyframes reveal{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}.d{animation:reveal .28s ease-out both}</style>',
    f'<text x="22" y="24" fill="{BRIGHT}" font-size="13" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">TahaMohamedAdib / contributions</text>'
]

seen_months = set()
for w in range(53):
    for dow in range(7):
        d = start + timedelta(days=w * 7 + dow)
        item = items.get(d, {"count": 0, "level": 0})
        lv = max(0, min(4, int(item.get("level", 0) or 0)))
        x, y = LEFT + w * PITCH, TOP + dow * PITCH
        delay = 0.012 * (w + dow)
        svg.append(
            f'<rect class="d" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{PALETTE[lv]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{escape(d.isoformat())}: {int(item.get("count",0) or 0)} contributions</title></rect>'
        )
        if d.day <= 7 and d.month not in seen_months and dow == 0:
            seen_months.add(d.month)
            svg.append(f'<text x="{x}" y="{TOP-7}" fill="{TEXT}" font-size="10" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{d.strftime("%b")}</text>')

for idx, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
    svg.append(f'<text x="8" y="{TOP + idx*PITCH + 9}" fill="{TEXT}" font-size="9" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{label}</text>')

stats = payload.get("stats", {})
footer = f'{stats.get("total",0):,} contributions · current streak {stats.get("current_streak",0)}d · longest {stats.get("longest_streak",0)}d'
svg.append(f'<text x="22" y="{H-18}" fill="{TEXT}" font-size="11" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{escape(footer)}</text>')
svg.append("</svg>")
OUT.write_text("\n".join(svg), encoding="utf-8")
print("Rendered contrib-heatmap.svg")
