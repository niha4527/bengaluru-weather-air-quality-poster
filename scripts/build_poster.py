import sys
import pandas as pd

root = sys.argv[1]
df = pd.read_csv(f"{root}/data/bengaluru_daily_clean.csv", parse_dates=["date"])

# ---- numbers quoted on the poster (computed, never typed by hand) ----
n = len(df)
mon, oth = df[df.season == "Monsoon"], df[df.season != "Monsoon"]
good_mon = (mon.aqi_cat == "Good").mean() * 100
good_oth = (oth.aqi_cat == "Good").mean() * 100
med_dry, med_rain = df[~df.rainy].pm25.median(), df[df.rainy].pm25.median()
rho = df.pm25.corr(df.rainfall_mm, method="spearman")
who_days = (df.pm25 > 15).sum(); who_pct = (df.pm25 > 15).mean() * 100
cpcb_days = (df.pm25 > 60).sum()
mm = df.groupby("month").agg(pm=("pm25", "mean"), h=("humidity_mean", "mean"), t=("temp_mean", "mean"))
months_above = int((mm.pm > 15).sum())
aqi100 = int((df.aqi_us > 100).sum()); aqi100_pct = aqi100 / n * 100
aqi100_mon = int((mon.aqi_us > 100).sum())
oz = df.groupby("season").ozone.mean()
peak = df.loc[df.aqi_us.idxmax()]
tmax = df.loc[df.temp_max.idxmax()]
MN = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
assert aqi100_mon == 0 and months_above == 8  # claims the text relies on

cells = n * 10
neg = f"−{abs(rho):.2f}" if rho < 0 else f"{rho:.2f}"

# Type scale (px, A1 landscape at 96 dpi): 74 title / 32 subtitle+heading / 25 body / 22 caption / 19 fine print.
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
@page{size:841mm 594mm;margin:0}
:root{--ink:#16202e;--muted:#4b5565;--line:#d5dbe5;--accent:#2a78d6;--navy:#0f2747;--tint:#eaf2fc;--bg:#eef1f5}
html,body{width:3178px;height:2240px;overflow:hidden;background:var(--bg);color:var(--ink);
  font-family:Arial,"Helvetica Neue",Helvetica,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:3178px;height:2240px;padding:40px;display:flex;flex-direction:column;gap:24px}
.header{flex:none;height:196px;display:grid;grid-template-columns:1fr 1000px;gap:24px}
.title{background:var(--navy);color:#fff;border-radius:14px;padding:0 52px;display:flex;flex-direction:column;justify-content:center}
.title h1{font-size:74px;line-height:1.1;font-weight:700;letter-spacing:-.5px;white-space:nowrap}
.title p{font-size:32px;margin-top:10px;color:#c9d8ef}
.team{background:#fff;border:2px solid var(--line);border-top:6px solid var(--accent);border-radius:14px;padding:14px 28px;font-size:22px;line-height:1.45}
.team .meta{color:var(--muted);font-size:20px}
.team .lab{font-weight:700;color:var(--navy);font-size:22px;margin-top:2px}
.team .row{display:grid;grid-template-columns:1fr 1fr;column-gap:14px;white-space:nowrap}
.body{flex:1;min-height:0;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:580px 1fr;gap:24px}
.stack{display:flex;flex-direction:column;gap:24px;min-height:0}
.wrap{display:flex;min-height:0}
.card{background:#fff;border:2px solid var(--line);border-top:6px solid var(--accent);border-radius:14px;padding:22px 26px 20px;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.card.tint{background:var(--tint)}
.grow,.wrap>.card{flex:1}
.h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
.no{font-size:32px;font-weight:700;color:var(--accent);white-space:nowrap}
.h h2{font-size:32px;font-weight:700;color:var(--navy);line-height:1.15}
p,li,td,th{font-size:25px;line-height:1.4}
ul{padding-left:28px}
li{margin-bottom:6px}
b{font-weight:700}
.chart img{display:block;width:100%}
.cap{font-size:22px;line-height:1.4;color:var(--muted);margin-top:12px}
.cap b{color:var(--ink)}
.note{font-size:19px;line-height:1.4;color:var(--muted);margin-top:auto;padding-top:10px}
table{border-collapse:collapse;width:100%}
td,th{border-bottom:2px solid var(--line);padding:2px 4px;text-align:left}
th{font-size:20px;font-weight:700;color:var(--muted);letter-spacing:.6px;text-transform:uppercase}
.stat{display:grid;grid-template-columns:150px 1fr;column-gap:14px;margin-bottom:26px;align-items:start}
.stat .n{font-size:46px;font-weight:700;line-height:1.05;color:var(--accent);white-space:nowrap}
.stat p{font-size:24px;line-height:1.35}
.rec{margin-bottom:18px}
.big p{font-size:27px;line-height:1.45;margin-bottom:14px}
.refs{flex:none;height:104px;background:#fff;border:2px solid var(--line);border-radius:14px;padding:12px 28px;
  display:grid;grid-template-columns:200px 1fr 1fr 1fr;column-gap:28px;font-size:19px;line-height:1.45;color:var(--muted)}
.refs h2{font-size:28px;font-weight:700;color:var(--navy)}
"""


def card(num, title, body, extra=""):
    return (f'<section class="card {extra}"><div class="h"><span class="no">{num}</span>'
            f'<h2>{title}</h2></div>{body}</section>')


def fig(tag, title, img, caption, extra=""):
    return (f'<section class="card chart {extra}"><div class="h"><span class="no">{tag}</span>'
            f'<h2>{title}</h2></div><img src="fig/{img}.png" alt="{title}">'
            f'<p class="cap">{caption}</p></section>')


problem = card("01", "Problem statement", f"""
<p>Bengaluru has hot dry spells, a heavy monsoon, and PM2.5 above the WHO guideline on <b>{who_pct:.0f}% of days</b>.
How do daily temperature, humidity and rainfall go with air quality across the year, and <b>when is the air worst?</b></p>""")

objectives = card("02", "Objectives", """<ul>
<li>Describe seasonal weather patterns.</li>
<li>Measure how air quality varies by month and season.</li>
<li>Compare air quality on rainy and dry days.</li>
<li>Check the data against WHO and CPCB limits.</li></ul>""")

source = card("03", "Data collection and source", """
<p><b>Public data, not collected by our group.</b></p><ul style="margin-top:8px">
<li><b>Weather:</b> Open-Meteo Historical API (ERA5).</li>
<li><b>Air quality:</b> Open-Meteo Air Quality API (CAMS).</li>
<li><b>Place:</b> Bengaluru (12.97° N, 77.59° E).</li>
<li><b>Period:</b> 1 Jan 2023 – 31 Dec 2025.</li>
<li><b>Sampling:</b> all hourly values, made daily.</li>
<li><b>Downloaded:</b> 11 Nov 2026.</li></ul>
<p class="note">Limit: modelled grid values, not readings from a ground station.</p>""")

dataset = card("04", "Dataset description", f"""
<p style="margin-bottom:6px"><b>{n:,} daily records · 10 attributes</b></p>
<table>
<tr><th>Attribute</th><th>Unit</th></tr>
<tr><td>Temperature: mean, max, min</td><td>°C</td></tr>
<tr><td>Relative humidity (mean)</td><td>%</td></tr>
<tr><td>Rainfall (daily total)</td><td>mm</td></tr>
<tr><td>PM2.5, PM10, NO₂, ozone (mean)</td><td>µg/m³</td></tr>
<tr><td>US AQI (mean)</td><td>0–500</td></tr>
</table>
<p style="margin-top:10px"><b>Derived:</b> season, AQI category, rainy-day flag (≥ 2.5 mm).</p>""")

cleaning = card("05", "Data cleaning and checks", f"""<ul>
<li><b>Missing values:</b> 0 of {cells:,} cells.</li>
<li><b>Duplicate dates:</b> 0.</li>
<li><b>Temperature order:</b> min ≤ mean ≤ max.</li>
<li><b>Valid ranges:</b> humidity 0–100 %, no negatives.</li>
<li><b>Outliers:</b> kept as real extremes (e.g. {tmax.temp_max:.1f} °C, {tmax.date:%-d %b %Y}).</li></ul>""", "grow")

cal = fig("Fig 1", "Daily air quality, 2023–2025", "calendar",
          f"<b>Heatmap.</b> Each square is one day. Pale (low AQI) squares fill Jun–Sep every year; darker squares dominate Jan–May and Oct–Dec. "
          f"Highest day: {peak.date:%-d %b %Y} (AQI {peak.aqi_us:.0f}).")

findings = card("06", "Key findings", f"""
<div class="stat"><div class="n">{good_mon:.0f}%</div><p><b>Monsoon air was cleanest.</b> {good_mon:.0f}% of Jun–Sep days rated “Good”, against {good_oth:.0f}% of other days.</p></div>
<div class="stat"><div class="n">{med_dry/med_rain:.1f}×</div><p><b>Dry days had higher PM2.5.</b> Median {med_dry:.1f} vs {med_rain:.1f} µg/m³ on rainy days (Spearman ρ = {neg}).</p></div>
<div class="stat"><div class="n">{who_pct:.0f}%</div><p><b>Above the WHO guideline.</b> PM2.5 passed 15 µg/m³ on {who_days} of {n:,} days, and the monthly mean in {months_above} of 12 months. CPCB limit (60): {cpcb_days} days.</p></div>
<div class="stat"><div class="n">{aqi100}</div><p><b>Days with AQI above 100,</b> none in Jun–Sep. Ozone: {oz['Summer']:.0f} (summer) vs {oz['Monsoon']:.0f} µg/m³ (monsoon).</p></div>
<p class="note">Associations in observational data, not proof of cause and effect: wind, traffic and burning are not in this dataset.</p>""", "tint")

hm = mm.h
climate = fig("Fig 2", "Temperature, humidity, rain", "climate",
              f"<b>Line and bar.</b> Temperature peaks in {MN[int(mm.t.idxmax())]} ({mm.t.max():.1f} °C) and is lowest in {MN[int(mm.t.idxmin())]} ({mm.t.min():.1f} °C). "
              f"Humidity is lowest in {MN[int(hm.idxmin())]} ({hm.min():.0f}%) and highest in {MN[int(hm.idxmax())]} ({hm.max():.0f}%). Rain falls mostly May–Oct.")

category = fig("Fig 3", "AQI category by season", "category",
               f"<b>Stacked bar.</b> Monsoon: {good_mon:.0f}% Good, none above Moderate. "
               "Other seasons: 54–74% Moderate, 23–30% Unhealthy for sensitive groups.", "grow")

monthly = fig("Fig 4", "PM2.5 by month", "monthly",
              f"<b>Bar.</b> Only Jun–Sep are at or below the WHO guideline. Lowest: {MN[int(mm.pm.idxmin())]} ({mm.pm.min():.1f}); highest: {MN[int(mm.pm.idxmax())]} ({mm.pm.max():.1f}). "
              "May has heavy rain yet stays above the guideline, so rain alone does not explain the pattern.")

conclusion = card("07", "Conclusion", f"""
<p>Over {n:,} days, Bengaluru’s air quality followed the seasons. It was cleanest in the monsoon (Jun–Sep) and above the WHO PM2.5 guideline in the other eight months.</p>
<p>Rainy and humid days went with lower PM2.5, but this is an association in modelled data. Next step: check it against ground-station data over more years.</p>""", "grow big")

box = fig("Fig 5", "PM2.5 on dry and rainy days", "box",
          f"<b>Box plot.</b> Median PM2.5 is {med_rain:.1f} on rainy days and {med_dry:.1f} on dry days. Dry days spread wider and reach higher values.")

recs = card("08", "Recommendations", f"""
<p class="rec"><b>1. Time health advisories to the dry months.</b> All {aqi100} days with AQI above 100 fell in Oct–May. Warn sensitive groups and plan outdoor events around it.</p>
<p class="rec"><b>2. Do not wait for rain.</b> Plan emission and dust control for Oct–May, and collect source data (traffic, construction, burning) to decide where to act.</p>
<p class="rec"><b>3. Validate before policy use.</b> Compare with CPCB station readings and extend to 5+ years.</p>""", "grow tint")

refs = """<section class="refs"><h2>References</h2>
<div>1. Open-Meteo. Historical Weather API (ERA5). open-meteo.com/en/docs/historical-weather-api<br>
2. Open-Meteo. Air Quality API (CAMS). open-meteo.com/en/docs/air-quality-api</div>
<div>3. Hersbach, H. et al. (2020). The ERA5 global reanalysis. Q. J. R. Meteorol. Soc., 146, 1999–2049.<br>
4. WHO (2021). WHO global air quality guidelines. World Health Organization, Geneva.</div>
<div>5. CPCB. National Ambient Air Quality Standards (NAAQS). cpcb.nic.in<br>
6. US EPA. AQI basics (US AQI categories). airnow.gov/aqi/aqi-basics</div></section>"""

team = """<div class="team"><div class="meta">RV University · IDA · Unit 5 Data Visualization Group Assignment</div>
<div class="lab">Team members</div><div class="row"><div>1. Hiranamyi Kiran Gudekota · 1RUA25CSE0191<br>2. Neharika Anantha Gowda · 1RUA25CSE0290<br>3. Niharika K P · 1RUA25CSE0292</div>
<div>4. Sai Yasasvi Kancharla · 1RUA25CSE0407<br>5. Sonali Ayyappa · 1RUA25CSE0455</div></div></div>"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Weather and Air Quality in Bengaluru, 2023–2025</title><style>{CSS}</style></head><body>
<div class="page">
<header class="header"><div class="title"><h1>Weather and Air Quality in Bengaluru, 2023–2025</h1>
<p>Do rainy, humid days go with cleaner air? Daily temperature, humidity, rainfall and air-quality data</p></div>{team}</header>
<main class="body">
<div class="stack" style="grid-row:1/3;grid-column:1">{problem}{objectives}{source}{dataset}{cleaning}</div>
<div class="wrap" style="grid-row:1;grid-column:2/4">{cal}</div>
<div class="wrap" style="grid-row:1;grid-column:4">{findings}</div>
<div class="stack" style="grid-row:2;grid-column:2">{climate}{category}</div>
<div class="stack" style="grid-row:2;grid-column:3">{monthly}{conclusion}</div>
<div class="stack" style="grid-row:2;grid-column:4">{box}{recs}</div>
</main>{refs}</div></body></html>"""

open(f"{root}/poster/poster.html", "w").write(html)
print("poster.html written")
