#!/usr/bin/env python3
"""Render a GitHub-style language breakdown SVG from a {lang: bytes} JSON.

Output mimics the bar+legend shown on a GitHub repo page (thin rounded stacked
bar over a wrapped legend of color dot + "Lang  XX.X%").
"""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
totals = json.load(open(src))

COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Rust": "#dea584", "HTML": "#e34c26", "CSS": "#563d7c", "SCSS": "#c6538c",
    "Astro": "#ff5a03", "MDX": "#fcb32c", "Markdown": "#083fa1",
    "Shell": "#89e051", "Dockerfile": "#384d54", "Vue": "#41b883",
    "Jupyter Notebook": "#DA5B0B", "Go": "#00ADD8", "Java": "#b07219",
    "Scala": "#DC322F",
    "C": "#555555", "C++": "#f34b7d", "Lua": "#000080",
    "Makefile": "#427819", "Just": "#384d54", "TeX": "#3D6117",
    "PowerShell": "#012456", "Procfile": "#3B2F63", "Nix": "#7e7eff",
    "Smarty": "#f0c040", "Roff": "#ecdebe", "Batchfile": "#C1F12E",
    "Handlebars": "#f7931e",
}

THRESHOLD = 0.005

items = sorted(totals.items(), key=lambda kv: -kv[1])
total_all = sum(b for _, b in items) or 1
big = [(l, b) for l, b in items if b / total_all >= THRESHOLD]
small_sum = total_all - sum(b for _, b in big)
visible = list(big)
if small_sum > 0:
    visible.append(("Other", small_sum))
total = sum(b for _, b in visible) or 1

WIDTH = 480
PAD = 16
BAR_W = WIDTH - PAD * 2
BAR_H = 8
TITLE_Y = 26
BAR_Y = 42
LEGEND_Y = 70
LEGEND_LINE_H = 22
DOT_R = 5
ITEM_GAP = 14

def text_w(s):
    return len(s) * 6.8 + 4

lines = []
cur = []
cur_x = 0
for lang, b in visible:
    pct = b / total * 100
    label = f"{lang}  {pct:.1f}%"
    item_w = DOT_R * 2 + 6 + text_w(label) + ITEM_GAP
    if cur and cur_x + item_w > BAR_W:
        lines.append(cur)
        cur = []
        cur_x = 0
    cur.append((lang, pct, label, item_w))
    cur_x += item_w
if cur:
    lines.append(cur)

HEIGHT = LEGEND_Y + LEGEND_LINE_H * len(lines) + 4

out = []
out.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Languages">'
)
out.append(
    "<style>"
    ".t{font:600 14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#24292f}"
    ".l{font:12px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#57606a}"
    "</style>"
)
out.append(
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="6" ry="6" fill="#ffffff" stroke="#d0d7de"/>'
)
out.append(f'<text x="{PAD}" y="{TITLE_Y}" class="t">Languages</text>')

out.append(
    f'<clipPath id="b"><rect x="{PAD}" y="{BAR_Y}" width="{BAR_W}" height="{BAR_H}" rx="4" ry="4"/></clipPath>'
)
out.append('<g clip-path="url(#b)">')
x = PAD
for lang, b in visible:
    w = BAR_W * b / total
    color = COLORS.get(lang, "#8b949e")
    out.append(f'<rect x="{x:.2f}" y="{BAR_Y}" width="{w:.2f}" height="{BAR_H}" fill="{color}"/>')
    x += w
out.append("</g>")

for li, line in enumerate(lines):
    y = LEGEND_Y + li * LEGEND_LINE_H
    x = PAD
    for lang, pct, label, w in line:
        color = COLORS.get(lang, "#8b949e")
        out.append(f'<circle cx="{x + DOT_R}" cy="{y - 4}" r="{DOT_R}" fill="{color}"/>')
        out.append(f'<text x="{x + DOT_R * 2 + 6}" y="{y}" class="l">{label}</text>')
        x += w

out.append("</svg>")
open(dst, "w", encoding="utf-8").write("\n".join(out))
print(f"Wrote {dst}: {len(visible)} languages, total {total:,} bytes")
