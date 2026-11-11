import json, sys
import pandas as pd

root = sys.argv[1]
w = pd.DataFrame(json.load(open(f"{root}/data/raw/weather.json"))["hourly"])
a = pd.DataFrame(json.load(open(f"{root}/data/raw/aq.json"))["hourly"])
for d in (w, a):
    d["time"] = pd.to_datetime(d["time"])
    d["date"] = d["time"].dt.date

dw = w.groupby("date").agg(
    temp_mean=("temperature_2m", "mean"), temp_max=("temperature_2m", "max"),
    temp_min=("temperature_2m", "min"), humidity_mean=("relative_humidity_2m", "mean"),
    rainfall_mm=("precipitation", "sum"))
da = a.groupby("date").agg(
    pm25=("pm2_5", "mean"), pm10=("pm10", "mean"), no2=("nitrogen_dioxide", "mean"),
    ozone=("ozone", "mean"), aqi_us=("us_aqi", "mean"))
df = dw.join(da, how="outer").round(2)
df.index = pd.to_datetime(df.index)
df.index.name = "date"
df.to_csv(f"{root}/data/bengaluru_daily_2023_2025.csv")
print(df.shape); print(df.isna().sum()); print(df.describe().T[["mean","min","max"]])
