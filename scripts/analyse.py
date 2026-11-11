import sys
import numpy as np
import pandas as pd

root = sys.argv[1]
df = pd.read_csv(f"{root}/data/bengaluru_daily_2023_2025.csv", parse_dates=["date"])

# --- prepare ---
assert df["date"].is_unique and df.isna().sum().sum() == 0
assert (df.temp_min <= df.temp_mean).all() and (df.temp_mean <= df.temp_max).all()
assert df.humidity_mean.between(0, 100).all()
assert (df[["rainfall_mm", "pm25", "pm10", "no2", "ozone", "aqi_us"]] >= 0).all().all()
assert df.temp_mean.between(-10, 50).all()
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month
df["season"] = df.month.map(lambda m: "Winter" if m in (12, 1, 2) else "Summer" if m in (3, 4, 5)
                            else "Monsoon" if m in (6, 7, 8, 9) else "Post-monsoon")
df["aqi_cat"] = pd.cut(df.aqi_us, [0, 50, 100, 150, 200, 500],
                       labels=["Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy", "Very unhealthy"])
df["rainy"] = df.rainfall_mm >= 2.5
df["temp_range"] = df.temp_max - df.temp_min
df.to_csv(f"{root}/data/bengaluru_daily_clean.csv", index=False)

pd.set_option("display.width", 200)
num = ["temp_mean", "temp_max", "temp_min", "humidity_mean", "rainfall_mm", "pm25", "pm10", "no2", "ozone", "aqi_us"]

print("== OUTLIERS (IQR, count) ==")
for c in num:
    q1, q3 = df[c].quantile([.25, .75]); i = q3 - q1
    print(f"{c:14s}", int(((df[c] < q1 - 1.5*i) | (df[c] > q3 + 1.5*i)).sum()))

print("\n== SEASON MEANS ==")
order = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
print(df.groupby("season")[num].mean().loc[order].round(1))
print("\nseason rainfall total/yr (mm):")
print((df.groupby(["year", "season"]).rainfall_mm.sum().unstack()[order]).round(0))

print("\n== MONTHLY MEANS ==")
print(df.groupby("month")[["temp_mean", "humidity_mean", "pm25", "aqi_us"]].mean().round(1).join(
    df.groupby("month").rainfall_mm.sum().div(3).round(0).rename("rain_mm_per_yr")))

print("\n== YEARLY ==")
print(df.groupby("year")[["temp_mean", "humidity_mean", "pm25", "aqi_us"]].mean().round(2))
print("rain total:", df.groupby("year").rainfall_mm.sum().round(0).to_dict())

print("\n== CORRELATION (Spearman) ==")
print(df[num].corr(method="spearman").round(2))

print("\n== AQI CATEGORY DAYS ==")
print(df.aqi_cat.value_counts().reindex(["Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy", "Very unhealthy"]))
print(pd.crosstab(df.season, df.aqi_cat).loc[order])

print("\n== RAIN EFFECT ==")
print(df.groupby("rainy")[["pm25", "pm10", "aqi_us", "humidity_mean", "temp_mean"]].mean().round(1))
print("days >=2.5mm:", int(df.rainy.sum()), " heavy >=30mm:", int((df.rainfall_mm >= 30).sum()))
# lag: does rain yesterday lower pm25 today
print("corr(pm25, rain lag1) =", round(df.pm25.corr(df.rainfall_mm.shift(1), method="spearman"), 2))

print("\n== WHO / CPCB EXCEEDANCE ==")
print("PM2.5 > 15 (WHO24h):", int((df.pm25 > 15).sum()), f"({(df.pm25>15).mean()*100:.0f}%)")
print("PM2.5 > 60 (CPCB24h):", int((df.pm25 > 60).sum()))
print("PM10 > 45 (WHO24h):", int((df.pm10 > 45).sum()), "  >100 (CPCB):", int((df.pm10 > 100).sum()))

print("\n== EXTREMES ==")
for c, f in [("temp_max", "idxmax"), ("temp_min", "idxmin"), ("rainfall_mm", "idxmax"), ("pm25", "idxmax"), ("aqi_us", "idxmax")]:
    r = df.loc[getattr(df[c], f)()]
    print(c, r.date.date(), r[c])
print("\n== TREND (OLS slope per year, monthly anomalies) ==")
m = df.set_index("date")[["temp_mean", "pm25", "humidity_mean"]].resample("MS").mean()
anom = m - m.groupby(m.index.month).transform("mean")
t = np.arange(len(anom)) / 12
for c in anom: print(c, round(np.polyfit(t, anom[c], 1)[0], 3))
