import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Patch

root = sys.argv[1]
df = pd.read_csv(f"{root}/data/bengaluru_daily_clean.csv", parse_dates=["date"])
out = f"{root}/figures"

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ORD = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # ordinal, none lighter than step 250
MID = "#f0efec"

mpl.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "sans-serif", "font.size": 13, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.titlelocation": "left", "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "legend.frameon": False,
})
MON = list("JFMAMJJASOND")
SEAS = ["Winter", "Summer", "Monsoon", "Post-monsoon"]


def save(fig, name):
    fig.savefig(f"{out}/{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# 1. Climate by month: small multiples, one axis each
m = df.groupby("month").agg(t=("temp_mean", "mean"), tmax=("temp_max", "mean"), tmin=("temp_min", "mean"),
                           h=("humidity_mean", "mean"), pm=("pm25", "mean"))
m["rain"] = df.groupby("month").rainfall_mm.sum() / 3
fig, ax = plt.subplots(3, 1, figsize=(8, 8.5), sharex=True)
x = np.arange(1, 13)
ax[0].fill_between(x, m.tmin, m.tmax, color=BLUE, alpha=0.18, lw=0)
ax[0].plot(x, m.t, color=BLUE, lw=2.5, marker="o", ms=7, mec=SURF, mew=2)
ax[0].set(ylabel="Temperature (°C)", title="Temperature: mean line, daily min–max band")
ax[1].plot(x, m.h, color=BLUE, lw=2.5, marker="o", ms=7, mec=SURF, mew=2)
ax[1].set(ylabel="Relative humidity (%)", title="Humidity")
ax[2].bar(x, m.rain, color=BLUE, width=0.7)
ax[2].set(ylabel="Rainfall (mm / yr)", title="Rainfall (average per year)")
ax[2].set_xticks(x, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
for a in ax: a.margins(x=0.03)
fig.tight_layout(); save(fig, "01_monthly_climate")

# 2. Calendar heatmap of daily AQI (sequential, one hue)
cmap = LinearSegmentedColormap.from_list("seq", SEQ)
fig, axs = plt.subplots(3, 1, figsize=(13, 6.3), sharex=True)
for ax, (yr, g) in zip(axs, df.groupby("year")):
    jan1 = pd.Timestamp(f"{yr}-01-01")
    wk = ((g.date - jan1).dt.days + jan1.dayofweek) // 7
    grid = np.full((7, 54), np.nan)
    grid[g.date.dt.dayofweek.values, wk.values] = g.aqi_us.values
    im = ax.pcolormesh(grid, cmap=cmap, vmin=0, vmax=160, edgecolors=SURF, linewidth=1.5)
    ax.invert_yaxis(); ax.set_aspect("equal"); ax.grid(False)
    ax.set_yticks([0.5, 2.5, 4.5], ["Mon", "Wed", "Fri"]); ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_ylabel(str(yr), rotation=0, labelpad=28, fontweight="bold", color=INK)
    ticks = [((pd.Timestamp(f"{yr}-{mo:02d}-01") - jan1).days + jan1.dayofweek) / 7 + 0.5 for mo in range(1, 13)]
    ax.set_xticks(ticks, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
axs[0].set_title("Daily US AQI, Bengaluru: monsoon (Jun–Sep) is the pale band every year")
cb = fig.colorbar(im, ax=axs, orientation="horizontal", fraction=0.04, pad=0.08, aspect=40)
cb.set_label("US AQI (daily mean)"); cb.outline.set_visible(False)
save(fig, "02_aqi_calendar")

# 3. Rain washes the air: PM2.5 dry vs rainy days
fig, ax = plt.subplots(figsize=(6, 6))
data = [df[~df.rainy].pm25, df[df.rainy].pm25]
bp = ax.boxplot(data, widths=0.5, patch_artist=True, showfliers=False, medianprops=dict(color=INK, lw=2),
                whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
for patch, c in zip(bp["boxes"], [ORANGE, BLUE]):
    patch.set(facecolor=c, edgecolor=SURF, alpha=0.9)
ax.axhline(15, color=INK2, ls=(0, (4, 3)), lw=1.3)
ax.text(1.5, 15.8, "WHO limit 15", ha="center", color=INK2, fontsize=11)
for i, d in enumerate(data, 1):
    ax.text(i, d.median() + 1.2, f"median {d.median():.1f}", ha="center", color=INK, fontsize=12, fontweight="bold")
ax.set_xticks([1, 2], [f"Dry days\n(n={len(data[0])})", f"Rainy days ≥2.5 mm\n(n={len(data[1])})"])
ax.set(ylabel="PM2.5 (µg/m³)", title="PM2.5 is lower on rainy days (median 23.7 vs 9.0)")
ax.grid(axis="x", visible=False)
save(fig, "03_rain_vs_pm25")

# 4. Correlation heatmap: diverging blue-red, gray midpoint
cols = ["temp_max", "humidity_mean", "rainfall_mm", "pm25", "pm10", "no2", "ozone", "aqi_us"]
names = ["Max temp", "Humidity", "Rainfall", "PM2.5", "PM10", "NO₂", "Ozone", "US AQI"]
c = df[cols].corr(method="spearman").values
div = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#6da7ec", MID, "#ee8a87", "#c0302f"])
fig, ax = plt.subplots(figsize=(8, 7))
q = ax.pcolormesh(c, cmap=div, vmin=-1, vmax=1, edgecolors=SURF, linewidth=2)
cb = fig.colorbar(q, ax=ax, shrink=0.78, pad=0.03)
cb.set_label("Spearman correlation (ρ)"); cb.outline.set_visible(False)
ax.invert_yaxis(); ax.set_aspect("equal"); ax.grid(False); ax.tick_params(length=0)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks(np.arange(8) + .5, names, rotation=40, ha="right"); ax.set_yticks(np.arange(8) + .5, names)
for i in range(8):
    for j in range(8):
        v = c[i, j]
        ax.text(j + .5, i + .5, f"{v:.2f}", ha="center", va="center", fontsize=10.5,
                color="#ffffff" if abs(v) > .6 else INK)
ax.set_title("Humidity and rainfall are negatively correlated with PM2.5 and AQI")
save(fig, "04_correlation")

# 5. AQI category share by season (100% stacked, ordinal ramp)
cats = ["Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy"]
ct = pd.crosstab(df.season, df.aqi_cat).reindex(SEAS)[cats]
pct = ct.div(ct.sum(1), axis=0) * 100
fig, ax = plt.subplots(figsize=(9, 4.8))
left = np.zeros(4)
for cat, col in zip(cats, ORD):
    ax.barh(SEAS, pct[cat], left=left, color=col, edgecolor=SURF, linewidth=2, label=cat, height=0.62)
    for i, (l, v) in enumerate(zip(left, pct[cat])):
        if v >= 7:
            ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=12, fontweight="bold",
                    color=INK if col == ORD[0] else "#ffffff")
    left += pct[cat].values
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.grid(False)
ax.set_xlabel("Share of days (%)"); ax.set_title("Monsoon: 64% of days rate 'Good'; other seasons 2–15%")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.18), fontsize=11)
save(fig, "05_aqi_category_by_season")

# 6. PM2.5 by month vs WHO guideline, with rainfall beneath (two axes, not dual-axis)
fig, ax = plt.subplots(2, 1, figsize=(8, 6.5), sharex=True, gridspec_kw=dict(height_ratios=[1.3, 1]))
cols_m = [ORANGE if v > 15 else BLUE for v in m.pm]
ax[0].bar(x, m.pm, color=cols_m, width=0.7)
ax[0].axhline(15, color=INK2, ls=(0, (4, 3)), lw=1.3)
ax[0].text(7.5, 16.2, "WHO guideline 15", ha="center", color=INK2, fontsize=11)
ax[0].set(ylabel="PM2.5 (µg/m³)", title="Mean PM2.5 by month")
ax[0].legend(handles=[Patch(color=ORANGE, label="Above WHO guideline (15)"),
                      Patch(color=BLUE, label="At or below guideline")],
             loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=11)
ax[1].bar(x, m.rain, color=BLUE, width=0.7)
ax[1].set(ylabel="Rainfall (mm / yr)", title="Rainfall")
ax[1].set_xticks(x, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
fig.tight_layout(); save(fig, "06_pm25_vs_rain_by_month")

# 7. Daily PM2.5 vs rainfall scatter-free trend: 30-day rolling PM2.5 with rain shading
r = df.set_index("date")
fig, ax = plt.subplots(figsize=(13, 4.2))
ax.plot(r.index, r.pm25, color=BLUE, lw=0.7, alpha=0.35, label="Daily mean")
ax.plot(r.index, r.pm25.rolling(30, center=True).mean(), color=BLUE, lw=2.8, label="30-day average")
ax.legend(loc="upper left", ncol=2, fontsize=11)
ax.axhline(15, color=INK2, ls=(0, (4, 3)), lw=1.3)
ax.text(r.index[5], 16.3, "WHO guideline 15", color=INK2, fontsize=11)
ax.set(ylabel="PM2.5 (µg/m³)", title="Daily PM2.5 (thin) and 30-day average (thick), 2023–2025")
ax.margins(x=0.01)
save(fig, "07_pm25_timeseries")
print("ok")
