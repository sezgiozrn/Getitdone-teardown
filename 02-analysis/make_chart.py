# Renders the README chart from the q1 findings output.
# Source of truth: 02-analysis/output/q1_district_vs_category.md (written by analysis.py)
import re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
SRC = HERE / "output" / "q1_district_vs_category.md"
OUT = HERE / "output" / "chart_sidewalk_district_medians.png"

CITY_MEDIAN = None
rows = []
for line in SRC.read_text().splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 6 and cells[1] == "Sidewalk Repair Issue":
        district, _, n, dmed, cmed, _ = cells
        rows.append((int(district), int(n), float(dmed)))
        CITY_MEDIAN = float(cmed)

rows.sort(key=lambda r: r[2])  # ascending so largest ends up on top in barh

ACCENT = "#b03a2e"   # districts named in the memo
BASE = "#b8b8b8"

labels = [f"District {d}  (n={n})" for d, n, _ in rows]
values = [m for _, _, m in rows]
colors = [ACCENT if d in (2, 7) else BASE for d, _, _ in rows]

fig, ax = plt.subplots(figsize=(9, 4.2), facecolor="white")
ax.set_facecolor("white")
bars = ax.barh(labels, values, color=colors, height=0.62)

for bar, v in zip(bars, values):
    ax.text(v + 8, bar.get_y() + bar.get_height() / 2,
            f"{v:.0f}d", va="center", fontsize=10, color="#333333")

ax.axvline(CITY_MEDIAN, color="#333333", linestyle="--", linewidth=1)
ax.text(CITY_MEDIAN + 8, -0.55, f"citywide median: {CITY_MEDIAN:.0f} days",
        fontsize=9, color="#333333")

ax.set_title("Sidewalk repair: Districts 2 and 7 run 14\u201318\u00d7 the citywide median",
             fontsize=13, loc="left", pad=14, color="#1a1a1a")
ax.set_xlabel("Median days, request \u2192 resolution notice (2025 closed requests)",
              fontsize=9.5, color="#555555")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=10)
ax.margins(x=0.08)
fig.tight_layout()
fig.savefig(OUT, dpi=200, facecolor="white", bbox_inches="tight")
print(f"wrote {OUT}")
