from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
import requests
from PIL import Image, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "taha-ascii.svg"
AVATAR = "https://avatars.githubusercontent.com/u/196954846?v=4"

r = requests.get(AVATAR, headers={"User-Agent": "GitHubProfileReadme/1.0"}, timeout=30)
r.raise_for_status()

img = Image.open(BytesIO(r.content)).convert("L")
img = ImageOps.fit(img, (420, 420), method=Image.Resampling.LANCZOS)
img = ImageOps.autocontrast(img)
img = ImageEnhance.Contrast(img).enhance(1.25)

COLS, ROWS = 66, 34
img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
ramp = " .:-=+*#%@"
lines = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        p = img.getpixel((x, y))
        idx = round((255 - p) / 255 * (len(ramp) - 1))
        line.append(ramp[idx])
    lines.append("".join(line).rstrip())

W, H = 610, 390
PAD, LINE = 18, 10.5
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="18" fill="#0d1117" stroke="#30363d"/>',
    '<defs>'
]
for i in range(ROWS):
    y = PAD + i * LINE
    svg.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{y:.1f}" width="0" height="{LINE+2:.1f}"><animate attributeName="width" from="0" to="{W-PAD*2}" dur="0.55s" begin="{i*0.035:.3f}s" fill="freeze"/></rect></clipPath>')
svg.append('</defs>')

for i, line in enumerate(lines):
    y = PAD + (i + 1) * LINE
    svg.append(f'<text x="{PAD}" y="{y:.1f}" clip-path="url(#r{i})" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="#c9d1d9" xml:space="preserve">{escape(line)}</text>')

svg.append('<text x="18" y="374" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="14" fill="#58a6ff">Taha Mohamed Adib · Data Science &amp; AI</text>')
svg.append('</svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print("Rendered taha-ascii.svg from GitHub avatar")
