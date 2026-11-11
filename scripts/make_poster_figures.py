import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

root = sys.argv[1]
df = pd.read_csv(f"{root}/data/bengaluru_daily_clean.csv", parse_dates=["date"])
out = f"{root}/poster/fig"

# Slot sizes in CSS px at 96 dpi; must match scripts/build_poster.py
SLOTS = {"calendar": (1481, 400), "climate": (700, 500), "monthly": (700, 540),
         "box": (700, 560), "category": (700, 300)}
PX = 1 / 96

SURF, INK, INK2, GRID = "#ffffff", "#16202e", "#4b5565", "#e3e7ee"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ORD = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SEAS = ["Winter", "Summer", "Monsoon", "Post-monsoon"]

mpl.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "Arial", "font.size": 18, "text.color": INK, "axes.labelcolor": INK2, "axes.labelsize": 19,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 18, "ytick.labelsize": 18,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 1,
    "axes.axisbelow": True, "axes.titlelocation": "left", "axes.titlesize": 20,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False,
    "legend.fontsize": 17,
})


def fig_for(name, **kw):
    w, h = SLOTS[name]
    return plt.subplots(figsize=(w * PX, h * PX), **kw)


def save(fig, name):
    fig.savefig(f"{out}/{name}.png", dpi=200)
    plt.close(fig)


m = df.groupby("month").agg(t=("temp_mean", "mean"), tmax=("temp_max", "mean"), tmin=("temp_min", "mean"),
                           h=("humidity_mean", "mean"), pm=("pm25", "mean"))
m["rain"] = df.groupby("month").rainfall_mm.sum() / df.year.nunique()
x = np.arange(1, 13)

# 1. calendar of daily AQI
cmap = LinearSegmentedColormap.from_list("seq", SEQ)
w, h = SLOTS["calendar"]
fig, axs = plt.subplots(3, 1, figsize=(w * PX, h * PX), sharex=True)
for ax, (yr, g) in zip(axs, df.groupby("year")):
    jan1 = pd.Timestamp(f"{yr}-01-01")
    wk = ((g.date - jan1).dt.days + jan1.dayofweek) // 7
    grid = np.full((7, 54), np.nan)
    grid[g.date.dt.dayofweek.values, wk.values] = g.aqi_us.values
    im = ax.pcolormesh(grid, cmap=cmap, vmin=0, vmax=160, edgecolors=SURF, linewidth=1)
    ax.invert_yaxis(); ax.grid(False); ax.tick_params(length=0)
    ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_ylabel(str(yr), rotation=0, labelpad=40, fontweight="bold", color=INK, va="center")
    ticks = [((pd.Timestamp(f"{yr}-{mo:02d}-01") - jan1).days + jan1.dayofweek) / 7 + 0.5 for mo in range(1, 13)]
    ax.set_xticks(ticks, MONTHS)
fig.subplots_adjust(left=0.06, right=0.90, top=0.99, bottom=0.12, hspace=0.12)
cax = fig.add_axes([0.925, 0.28, 0.01, 0.5])
cb = fig.colorbar(im, cax=cax)
cb.set_label("US AQI (daily mean)", fontsize=17); cb.outline.set_visible(False)
cb.ax.tick_params(labelsize=16)
save(fig, "calendar")

# 2. climate panels
fig, ax = fig_for("climate", nrows=3, sharex=True)
ax[0].fill_between(x, m.tmin, m.tmax, color=BLUE, alpha=0.18, lw=0)
ax[0].plot(x, m.t, color=BLUE, lw=3.5, marker="o", ms=9, mec=SURF, mew=2)
ax[0].set_ylabel("°C")
ax[1].plot(x, m.h, color=BLUE, lw=3.5, marker="o", ms=9, mec=SURF, mew=2)
ax[1].set_ylabel("%")
ax[2].bar(x, m.rain, color=BLUE, width=0.7)
ax[2].set_ylabel("mm")
ax[2].set_xticks(x, [mo[0] for mo in MONTHS])
for a, t in zip(ax, ["Temperature: mean (line), min–max (band)",
                     "Relative humidity: monthly mean",
                     "Rainfall: yearly average per month"]):
    a.set_title(t, fontsize=17); a.margins(x=0.03)
fig.tight_layout(h_pad=0.6)
save(fig, "climate")

# 3. monthly PM2.5 vs WHO guideline
fig, ax = fig_for("monthly")
ax.bar(x, m.pm, color=[ORANGE if v > 15 else BLUE for v in m.pm], width=0.7)
ax.axhline(15, color=INK2, ls=(0, (4, 3)), lw=2)
ax.text(7.5, 16.4, "WHO guideline: 15", ha="center", color=INK2, fontsize=15)
ax.set_xticks(x, [mo[0] for mo in MONTHS])
ax.set_ylabel("Mean PM2.5 (µg/m³)"); ax.set_xlabel("Month (average of 2023–2025)")
ax.legend(handles=[Patch(color=ORANGE, label="Above guideline"), Patch(color=BLUE, label="At or below")],
          loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2)
fig.tight_layout()
save(fig, "monthly")

# 4. dry vs rainy boxplot
fig, ax = fig_for("box")
data = [df[~df.rainy].pm25, df[df.rainy].pm25]
bp = ax.boxplot(data, widths=0.5, patch_artist=True, showfliers=False, medianprops=dict(color=INK, lw=3),
                whiskerprops=dict(color=INK2, lw=1.8), capprops=dict(color=INK2, lw=1.8))
for patch, c in zip(bp["boxes"], [ORANGE, BLUE]):
    patch.set(facecolor=c, edgecolor=SURF, alpha=0.9)
ax.axhline(15, color=INK2, ls=(0, (4, 3)), lw=2)
ax.text(1.5, 16.2, "WHO: 15", ha="center", color=INK2, fontsize=16)
for i, d in enumerate(data, 1):
    ax.text(i, d.median() + 1.6, f"median {d.median():.1f}", ha="center", color=INK, fontsize=18, fontweight="bold")
ax.set_xticks([1, 2], [f"Dry days\n(n={len(data[0])})", f"Rainy days ≥2.5 mm\n(n={len(data[1])})"])
ax.set_ylabel("Daily mean PM2.5 (µg/m³)")
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "box")

# 5. AQI category share by season
cats = ["Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy"]
ct = pd.crosstab(df.season, df.aqi_cat).reindex(SEAS)[cats]
pct = ct.div(ct.sum(1), axis=0) * 100
fig, ax = fig_for("category")
left = np.zeros(4)
for cat, col in zip(cats, ORD):
    ax.barh(SEAS, pct[cat], left=left, color=col, edgecolor=SURF, linewidth=2.5, label=cat, height=0.66)
    for i, (l, v) in enumerate(zip(left, pct[cat])):
        if v >= 7:
            ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=17, fontweight="bold",
                    color=INK if col == ORD[0] else "#ffffff")
    left += pct[cat].values
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.grid(False)
ax.set_xlabel("Share of days in season (%)")
ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.36, -0.30), fontsize=15, columnspacing=1.2)
ax.set_xticks([0, 25, 50, 75, 100])
fig.subplots_adjust(left=0.27, right=0.95, top=0.98, bottom=0.40)
save(fig, "category")
print("ok")
