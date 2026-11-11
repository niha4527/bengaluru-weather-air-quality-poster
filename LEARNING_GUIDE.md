# Learning Guide: Weather and Air Quality in Bengaluru, 2023–2025

This guide explains everything the project did, in the order you should learn it. Read it once from top to bottom, then use it as a reference while you prepare for the viva and the poster presentation. The companion file `checklist.md` tells you which files to open and what to verify.

All five members must be able to explain the dataset, methods, code, charts and conclusions. Part 11 gives each member a suggested talk track, and Part 10 has likely questions with model answers.

---

## Part 1. The project in one page

**Topic (from the assignment list, number 5):** Weather and Environment Monitoring: daily temperature, humidity, rainfall and air-quality readings from reliable sources.

**Question we asked:** Using public daily data for Bengaluru from 1 January 2023 to 31 December 2025, how do temperature, humidity and rainfall vary through the year, how does air quality vary alongside them, and when is the air worst compared with health guidelines?

**Data:** 1,096 daily records, 10 attributes, downloaded from the Open-Meteo public APIs. **We did not collect it ourselves.** Say this clearly, because the assignment forbids describing downloaded data as group-collected.

**What we did, in six steps:**
1. Downloaded hourly weather and air-quality data for Bengaluru.
2. Turned the hourly values into one row per day.
3. Checked the data for missing values, duplicates and impossible values.
4. Added helper columns (season, AQI category, rainy-day flag).
5. Analysed it: averages by season and month, rainy days against dry days, correlations, and comparison with WHO and CPCB limits.
6. Drew charts and wrote the findings, recommendations, poster and report.

**The short answer we found:**
- Air quality follows the seasons. It is cleanest in the monsoon (June to September).
- PM2.5 (fine dust) was above the WHO guideline on 62% of all days, and in 8 of 12 months.
- PM2.5 was lower on rainy days (median 9.0 against 23.7 µg/m³ on dry days).
- All 199 days with a poor AQI (above 100) fell outside the monsoon.
- These are **associations**. The data cannot prove that rain *causes* cleaner air.

---

## Part 2. Concepts you need (plain language)

### 2.1 Weather variables
- **Temperature (°C):** we have the daily mean, daily maximum and daily minimum.
- **Relative humidity (%):** how much water vapour the air holds compared with the most it could hold at that temperature. 100% means saturated.
- **Rainfall (mm):** depth of rain in a day. 1 mm over a square metre is 1 litre.
- **Rainy day:** we define it as 2.5 mm or more in a day. This follows the common meteorological cut-off. Days below it are "dry days" in our analysis (a drizzly day still counts as dry).

### 2.2 Air-quality variables
- **PM2.5:** particles smaller than 2.5 micrometres. They are tiny enough to reach deep into the lungs, so they matter most for health.
- **PM10:** particles smaller than 10 micrometres (includes PM2.5, plus coarser dust).
- **NO₂ (nitrogen dioxide):** a gas that comes mainly from burning fuel (traffic, industry).
- **Ozone (O₃):** a gas formed in sunlight from other pollutants. It tends to be higher in hot, sunny weather.
- **µg/m³:** micrograms per cubic metre of air, the unit for the pollutants.
- **US AQI:** a single index from 0 to 500 that summarises air quality. Bands: Good 0–50, Moderate 51–100, Unhealthy for sensitive groups 101–150, Unhealthy 151–200. In our data no day reached 201 or above.

### 2.3 The benchmarks
| Pollutant | WHO 2021 guideline (24-hour) | CPCB limit, India (24-hour) |
|---|---|---|
| PM2.5 | 15 µg/m³ | 60 µg/m³ |
| PM10 | 45 µg/m³ | 100 µg/m³ |

The WHO number is a health guideline and is much stricter than the Indian legal limit. That is why PM2.5 exceeded WHO on 675 days but exceeded the Indian limit on only 2.

### 2.4 Where the data came from, and what that means
- **ERA5** is a "reanalysis": a weather model (from ECMWF) combined with observations to reconstruct past weather on a grid, hour by hour.
- **CAMS** is the Copernicus Atmosphere Monitoring Service, which models air composition on a grid.
- **Open-Meteo** is a free service that serves both through a simple web API (a URL that returns data).
- Because both are **model values for a grid cell**, not readings from a monitor standing in a street, they can differ from a real station. This is the single most important limitation. Always say "modelled data".

### 2.5 Statistics used
- **Mean vs median:** the mean is the average. The median is the middle value. For skewed data (rainfall, with many zeros and a few huge days) the median describes a "typical day" better. We used the median to compare dry and rainy days.
- **Standard deviation (SD):** how spread out values are.
- **Outlier and the 1.5 × IQR rule:** the IQR is the range of the middle half of the data (25th to 75th percentile). A value more than 1.5 IQRs beyond that range is flagged as an outlier. Flagged does not mean wrong. Rainfall has 140 flagged days because most days have almost no rain, so any wet day looks extreme. We **kept** them: they are real weather.
- **Correlation:** a number from −1 to +1 for how two variables move together. +1: rise together. −1: one rises as the other falls. 0: no consistent link.
- **Spearman (ρ, "rho") vs Pearson:** Pearson assumes a straight-line relationship and is thrown off by skewed data. Spearman works on ranks and only needs the relationship to go consistently up or down. Rainfall is very skewed, so Spearman is the right choice.
- **Mann–Whitney U test:** compares two groups without assuming a normal distribution. We used it to check whether PM2.5 differs between dry and rainy days. The p-value was far below 0.001. **Caution:** consecutive days are not independent (a polluted day tends to be followed by a polluted day), so treat the p-value as a sign the difference is large, not as an exact probability.
- **Correlation is not causation:** two things moving together does not mean one causes the other. Rainy days are also more humid, cloudier and windier, and wind itself clears pollution. Our dataset has no wind, so we cannot separate these. The assignment explicitly forbids causal claims from simple correlations. Use words like "was lower on", "went with", "is associated with".

---

## Part 3. The data, file by file

| File | What it is |
|---|---|
| `data/raw/weather.json` | Hourly weather exactly as the API returned it. |
| `data/raw/aq.json` | Hourly air quality exactly as the API returned it. |
| `data/bengaluru_daily_2023_2025.csv` | The daily dataset: 1,096 rows, 10 columns. |
| `data/bengaluru_daily_clean.csv` | Same, plus 6 extra columns (year, month, season, aqi_cat, rainy, and so on). All charts use this. |
| `data/DATA_DICTIONARY.md` | Source, period, meaning of every column, quality checks. |
| `data/analysis_summary.txt` | The printed output of `scripts/analyse.py`. |

**The 10 main columns:**

| Column | Meaning | Unit | How the day's value is made from 24 hourly values |
|---|---|---|---|
| `date` | calendar date, YYYY-MM-DD | | |
| `temp_mean` | air temperature at 2 m | °C | mean |
| `temp_max` | highest hourly temperature | °C | maximum |
| `temp_min` | lowest hourly temperature | °C | minimum |
| `humidity_mean` | relative humidity at 2 m | % | mean |
| `rainfall_mm` | precipitation | mm | **sum** |
| `pm25` | PM2.5 | µg/m³ | mean |
| `pm10` | PM10 | µg/m³ | mean |
| `no2` | nitrogen dioxide | µg/m³ | mean |
| `ozone` | ozone | µg/m³ | mean |
| `aqi_us` | US AQI | 0–500 | mean of the hourly values |

Why rainfall is a **sum** and the others are means: rain is an amount that accumulates (total depth over the day), whereas temperature or concentration is a level, so the average is the right summary.

**Derived columns in the clean file:**
- `season`: Winter (Dec–Feb), Summer (Mar–May), Monsoon (Jun–Sep), Post-monsoon (Oct–Nov).
- `aqi_cat`: the AQI band of the day.
- `rainy`: True when `rainfall_mm` is 2.5 or more.
- `year`, `month`: taken from the date.

**What the raw download looks like:** open `data/raw/weather.json`. It is a JSON object with an `hourly` key holding lists: `time`, `temperature_2m`, `relative_humidity_2m`, `precipitation`. 1,096 days × 24 hours = 26,304 hourly values per variable.

---

## Part 4. The pipeline, step by step

You can see every step in the Colab notebook `Bengaluru_Weather_AQ_Visualization.ipynb`. The numbered sections follow this order.

### Step 1. Collect
The notebook calls two URLs with the same parameters (latitude 12.97, longitude 77.59, start date, end date, time zone):

```python
weather = fetch("https://archive-api.open-meteo.com/v1/archive",
                {**common, "hourly": "temperature_2m,relative_humidity_2m,precipitation"})
air = fetch("https://air-quality-api.open-meteo.com/v1/air-quality",
            {**common, "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone,us_aqi"})
```

`fetch` sends the request and turns the JSON answer into a table. **Why Open-Meteo:** one free source with no key gives all four measures for the same place and dates, so anyone can repeat the work.

**Sampling approach:** none. We took every hourly value in the period and then aggregated.

### Step 2. Aggregate hourly to daily
```python
daily_w = weather.groupby("date").agg(
    temp_mean=("temperature_2m", "mean"), temp_max=("temperature_2m", "max"),
    temp_min=("temperature_2m", "min"), humidity_mean=("relative_humidity_2m", "mean"),
    rainfall_mm=("precipitation", "sum"))
```
`groupby("date")` collects the 24 rows of each day, and `agg` applies the chosen summary to each. The air-quality table is done the same way, then the two are joined on the date.

### Step 3. Validate (checks that stop the script if the data is bad)
```python
assert df["date"].is_unique
assert df.isna().sum().sum() == 0
assert (df.temp_min <= df.temp_mean).all() and (df.temp_mean <= df.temp_max).all()
assert df.humidity_mean.between(0, 100).all()
assert (df[["rainfall_mm","pm25","pm10","no2","ozone","aqi_us"]] >= 0).all().all()
assert df.temp_mean.between(-10, 50).all()
```
An `assert` raises an error if the statement is false, so a problem cannot slip by silently. Results: **0 missing values out of 10,960 cells** (1,096 rows × 10 columns), **0 duplicate dates**, every temperature ordered correctly, every value in a valid range. So nothing needed fixing, and the report says that plainly ("none needed").

### Step 4. Add helper columns
Season from the month, AQI category from the AQI value using `pd.cut`, and the rainy-day flag from rainfall.

### Step 5. Analyse
Group averages by season and month, dry-versus-rainy comparison, Spearman correlations, counts of days above WHO and CPCB limits. See Part 6 for the results.

### Step 6. Visualise
Seven charts for the report and five for the poster, all drawn with Matplotlib. See Part 5.

---

## Part 5. The charts and how to read them

The assignment needs at least four charts and at least three chart types. We have seven report charts and five poster charts, using **line, bar, box plot, stacked bar and heatmap** types. The poster charts are re-drawn at poster size without in-image titles (the card heading is the title), but they show the same data.

Every chart has a title, labelled axes with units, readable scales, and a legend where more than one colour is used. No chart uses two vertical axes (a common mistake): different units go in separate panels.

### Report Figure 4.1: Monthly climate (`figures/01_monthly_climate.png`)
Three stacked panels. **Top:** monthly mean temperature (line) with the typical daily min to max range (shaded band). **Middle:** monthly mean humidity. **Bottom:** average yearly rainfall for each month (bars).
- Temperature peaks in **April (27.7 °C)** and is lowest in **January (21.1 °C)**.
- Humidity is lowest in **March (47%)** and highest in **July (82%)**.
- Rain is concentrated in **May to October**, with almost none in February.
- **How to say it:** "Bengaluru's dry, hot months are February to April; the monsoon months are humid and wet."

### Figure 4.2: Calendar heatmap (`02_aqi_calendar.png`)
Each small square is one day, laid out like a calendar, one block per year. Darker blue means higher AQI (worse air). One colour ramp from pale to dark is used because the variable is an amount.
- A **pale band appears every year in June to September**.
- Darker squares dominate January to May and October to December.
- Highest AQI day: 2 May 2025 (AQI 156).
- **How to say it:** "You can see the monsoon in the air quality without reading a number."

### Figure 4.3: PM2.5 time series (`07_pm25_timeseries.png`)
The thin line is each day's PM2.5; the thick line is a 30-day centred average that smooths the noise; the dashed line is the WHO guideline (15).
- The 30-day average dips below the guideline in every monsoon and rises above it otherwise.
- All 86 days above 40 µg/m³ fall outside the monsoon.
- Highest day: 66.3 µg/m³ on 26 October 2024.
- Yearly means were 21.4, 19.5 and 21.8 µg/m³ for 2023, 2024, 2025: similar, so **no clear long-term trend** can be claimed from three years.

### Figure 4.4: PM2.5 by month with rainfall (`06_pm25_vs_rain_by_month.png`)
Top: monthly mean PM2.5 as bars, orange if above the WHO guideline, blue if at or below. Bottom: monthly rainfall.
- Only **June to September** are at or below 15 µg/m³. That is 8 of 12 months above.
- Lowest month July (5.2), highest January (30.5).
- **Important nuance:** May has heavy rain (about 151 mm a year) yet PM2.5 stays above the guideline (24.5). So **rainfall alone does not explain the pattern**. This is a good point to raise yourself, because it shows you understand the limits of the analysis.

### Figure 4.5: Box plot, dry versus rainy days (`03_rain_vs_pm25.png`)
A box plot shows the **middle half of the data as a box**, the **median as the line inside**, and the typical range as whiskers (outliers are hidden in our version).
- Median PM2.5: **9.0 on rainy days (293 days)** against **23.7 on dry days (803 days)**.
- Dry days spread much wider and reach higher values.
- Mann–Whitney p < 0.001.
- **Say:** "PM2.5 is lower on rainy days", never "rain reduces PM2.5".

### Figure 4.6: AQI category by season (`05_aqi_category_by_season.png`)
A 100% stacked bar for each season: the share of days in Good, Moderate, Unhealthy for sensitive groups, Unhealthy.
- Monsoon: **64% Good** (233 of 366 days), none above Moderate.
- Other seasons together: only 6% Good (43 of 730 days). Moderate is 54–74% and Unhealthy-for-sensitive is 23–30% of days.

### Figure 4.7: Correlation heatmap (`04_correlation.png`)
Each cell is the Spearman correlation between two variables. Red is positive, blue is negative, grey near zero. The diagonal is always 1.00 (a variable with itself).
- Humidity vs PM2.5: **−0.61**. Rainfall vs PM2.5: **−0.58**. Humidity vs ozone: **−0.78**.
- Max temperature vs ozone: **+0.51**. Max temperature vs humidity: **−0.72**.
- PM2.5 vs PM10: **0.95**. PM2.5 vs AQI: **0.97** (particles usually set the AQI).
- NO₂ is only weakly related to humidity and rainfall (−0.17, −0.13).

### The poster's five charts
Fig 1 calendar heatmap, Fig 2 climate panels, Fig 3 AQI category stacked bar, Fig 4 PM2.5 by month bars, Fig 5 box plot. The correlation heatmap and the time series are in the report and notebook but not on the poster, to keep the poster uncluttered.

### Design choices you may be asked about
- **Colours:** blue for magnitude, blue and orange for two groups, blue-to-red around grey for correlations. Chosen so people with colour-vision deficiency can still tell them apart. Orange is used only to flag "above the guideline".
- **No dual axes:** two vertical axes on one chart can make unrelated things look related, so we use stacked panels.
- **Same font on the poster page and in the charts** so the poster looks consistent.

---

## Part 6. The findings, with the numbers and how each was computed

| # | Finding | Evidence | How computed |
|---|---|---|---|
| 1 | The monsoon air was cleanest. | 64% of Jun–Sep days rated Good against 6% of other days. Mean PM2.5 9 vs 27 µg/m³. | Share of days with `aqi_cat == "Good"` in each group; mean of `pm25`. |
| 2 | PM2.5 was lower on rainy days. | Median 9.0 vs 23.7; ρ = −0.58; p < 0.001. | Median by `rainy` flag; `corr(method="spearman")`; Mann–Whitney. |
| 3 | PM2.5 exceeded the WHO guideline on most days. | 675 of 1,096 days (62%); 8 of 12 monthly means; only 2 days above the Indian limit of 60. | Count of `pm25 > 15` and `pm25 > 60`; monthly means. |
| 4 | Poor-AQI days occur in the dry months. | All 199 days (18%) with AQI above 100 fell between October and May. None in Jun–Sep. | Count of `aqi_us > 100` by season. |
| 5 | The yearly cycle is stable. | Mean PM2.5 21.4, 19.5, 21.8 in the three years. | Mean of `pm25` per year. |

Other facts worth knowing: hottest day 39.5 °C on 1 May 2024; coldest 11.9 °C on 11 January 2023; most rain in a day 36.6 mm on 30 May 2023; yearly rain 796, 1,081 and 1,035 mm; the monsoon gives about 53% of the year's rain; ozone averages 92 µg/m³ in summer against 44 in the monsoon.

## Part 7. The recommendations and the reasoning

1. **Time health advisories to the dry months.** All 199 poor-AQI days fell between October and May. Warnings for sensitive groups (children, older adults, people with asthma) and planning of outdoor events should focus there.
2. **Do not rely on rain to clean the air.** The air meets the WHO guideline only in the monsoon, so emission and dust control should be planned for October to May. Collect source data (traffic, construction, burning) to decide where to act. *Note the wording: we recommend collecting source data because our data cannot say which sources matter.*
3. **Validate before policy use.** Compare with CPCB station readings over five or more years.

The assignment asks for two practical recommendations. We give three.

## Part 8. Limitations (be upfront about these)

- The data are **modelled grid values for one point**, not station readings.
- **Only three years**, which is too short to separate seasonal variation from long-term trends.
- Correlations show association only. **Wind, traffic, industry and burning are not in the data.**
- Daily averages hide hourly peaks such as rush-hour pollution.

---

## Part 9. The code, script by script

All scripts take the project folder as their one argument, for example `python3 scripts/analyse.py "$PWD"`.

| File | What it does |
|---|---|
| `scripts/build_daily.py` | Reads the two raw JSON files, aggregates hourly to daily, writes `data/bengaluru_daily_2023_2025.csv`. |
| `scripts/analyse.py` | Reads the daily CSV, runs the validation checks, adds helper columns, writes `data/bengaluru_daily_clean.csv`, and prints the analysis (season means, correlations, counts, extremes). |
| `scripts/make_figures.py` | Draws the 7 report charts into `figures/`. |
| `scripts/make_poster_figures.py` | Draws the 5 poster-sized charts into `poster/fig/`. |
| `scripts/build_poster.py` | Computes every number on the poster from the clean CSV and writes `poster/poster.html`. Chrome then prints the HTML to the poster PDF. |
| `scripts/build_report.py` | Opens the RV University template with python-docx, fills it, writes all chapters, tables and figures, and saves `report/Bengaluru_Weather_AQ_Report.docx`. |
| `Bengaluru_Weather_AQ_Visualization.ipynb` | The whole workflow in one Colab notebook, with outputs saved. This is the file to show for "code". |

**Two ideas worth understanding in the code:**
- **Numbers are computed, not typed.** In `build_poster.py` and `build_report.py`, every statistic in the text is a variable calculated from the data and inserted into the sentence. If the data changed, the text would update. The scripts also contain a few `assert` lines that stop the build if a claim in the text (for example "none in June to September") stops being true.
- **The report's contents-page numbers** come from a two-pass build: build once, convert to PDF, search the PDF for each heading's page, rebuild with those numbers.

## Part 10. Likely viva questions, with model answers

**1. Did you collect this data?** No. It is public data downloaded from Open-Meteo, which serves ERA5 weather reanalysis and CAMS air-quality model data. Our work was choosing it, preparing it, analysing it and visualising it.

**2. Why did you choose this source?** The topic asks for weather and air-quality readings from reliable sources. Open-Meteo gives all four measures for the same place and dates in one format, needs no key, and is built on data from established centres (ECMWF, Copernicus).

**3. Are these real measurements?** They are modelled values on a grid, not readings from a ground station. They can differ from a monitor at one street. We say so on the poster and in the report.

**4. Why Bengaluru and why 2023 to 2025?** Bengaluru is the city where our university is, and it has a clear monsoon cycle. Three complete years give three full seasonal cycles, so we can see whether the pattern repeats.

**5. How did you turn hourly data into daily data?** Group by date, then take the mean for temperature, humidity and pollutants, the maximum and minimum for temperature extremes, and the **sum** for rainfall.

**6. How did you check data quality?** Checked for missing values (0 of 10,960 cells), duplicate dates (0), temperature ordering (min ≤ mean ≤ max), humidity between 0 and 100, and no negative rainfall or pollutant values. All passed, so nothing needed to be fixed or removed.

**7. What about outliers?** We flagged them with the 1.5 × IQR rule. Rainfall had 140 flagged days because most days are dry. They are real weather, so we kept them.

**8. What is PM2.5 and why does it matter?** Particles smaller than 2.5 micrometres. They are small enough to reach deep into the lungs, so health guidelines focus on them.

**9. What does the AQI mean?** A 0 to 500 index that summarises air quality. Up to 50 is Good, 51 to 100 Moderate, 101 to 150 Unhealthy for sensitive groups, 151 to 200 Unhealthy.

**10. Why did you use the median for dry and rainy days?** Daily PM2.5 is skewed, so the median describes a typical day better than the mean. We also report means in the table.

**11. Why Spearman and not Pearson?** Rainfall is heavily skewed with many zeros, and Pearson assumes a straight-line relationship. Spearman uses ranks and only needs a consistent upward or downward trend.

**12. What does ρ = −0.58 between rainfall and PM2.5 mean?** A moderate negative association: days with more rain tend to have lower PM2.5. It does not mean rain causes the drop.

**13. Can you say rain cleans the air?** No. We can say PM2.5 is lower on rainy days. Rainy days also differ in humidity, cloud and wind, and we have no wind data. May shows this: it is rainy, yet its PM2.5 is above the guideline.

**14. What does the Mann–Whitney test tell you?** Whether two groups differ without assuming a normal distribution. Our p-value was below 0.001, so the difference is large. Because consecutive days are not independent, we treat it as a guide to size, not an exact probability.

**15. Why is the WHO number so different from the Indian limit?** The WHO figure (15 µg/m³) is a health guideline; the Indian limit (60) is a legal standard. We exceeded WHO on 675 days but the Indian limit on only 2.

**16. What was your most important finding?** The monsoon months are the only months at or below the WHO guideline, and every day with an AQI above 100 fell outside the monsoon.

**17. Is air quality getting better or worse over the years?** We cannot say. The yearly means (21.4, 19.5, 21.8) are similar, and three years are too short for a trend.

**18. Why these recommendations?** Each comes from a finding: advisories from the timing of poor days, dry-month control from the monsoon-only compliance, and validation from the data's limits.

**19. What would you do with more time?** Compare with CPCB station data, extend to more years and cities, add wind and traffic data, and use models that allow for day-to-day dependence.

**20. Why no chart with two y-axes?** Two scales on one chart can make unrelated series look related, so we use separate panels.

**21. How can someone reproduce your work?** Run the Colab notebook: it downloads the data, cleans it and redraws every chart. The scripts and the CSVs are in the repository.

**22. What did the code do that a spreadsheet could not?** The same steps are repeatable, checkable and documented in code, and the checks (`assert`) stop the run if the data is wrong.

---

## Part 11. A suggested talk track for five members

About 1.5 minutes each, about 7 minutes in all. Adjust to the time your faculty announces.

| Member | Section | Say |
|---|---|---|
| 1 | Problem and objectives | The question, why air quality and weather together, and that the data are public. |
| 2 | Data source and dataset | Open-Meteo, ERA5 and CAMS, the period, the 10 columns, the "modelled, not measured" limit. |
| 3 | Cleaning and checks | The checks, the results (all clean), why outliers were kept. |
| 4 | Charts | Calendar heatmap, monthly PM2.5, box plot: what each shows and how to read it. |
| 5 | Findings, recommendations, conclusion | The five findings with numbers, the recommendations, the limits and the future scope. |

Everyone should still know the whole project: any member can be asked anything.

## Part 12. Glossary

| Term | Meaning |
|---|---|
| API | A web address that returns data when you request it. |
| Reanalysis | A model plus observations that rebuilds past weather on a grid. |
| Aggregation | Combining many values into one summary (here, 24 hourly values into a day). |
| Median | The middle value when sorted. |
| IQR | Interquartile range: the spread of the middle half of the data. |
| Outlier | A value far from the rest. Not necessarily an error. |
| Correlation | How two variables move together, from −1 to +1. |
| Spearman ρ | A correlation based on ranks, good for skewed data. |
| p-value | The chance of seeing a difference at least this large if there were truly none (a guide only here). |
| Guideline vs limit | A guideline is a health recommendation (WHO). A limit is a legal standard (CPCB). |
| Association | Two things go together. It does not say one causes the other. |
| Heatmap | A grid of coloured cells where colour shows the value. |
| Box plot | A chart of the median, the middle half of the data and the typical range. |

---

## Part 13. If something looks different when you re-run it

The notebook downloads data fresh. Open-Meteo can revise its model data over time, so a fresh download may differ by small amounts from the files in `data/raw/`, which we downloaded on 11 November 2026. The numbers in the poster and report come from those saved files. To reproduce them exactly, use the scripts with the saved CSVs instead of re-downloading.

Next: open `checklist.md` for the list of files to check and the commands to verify the numbers yourself.
