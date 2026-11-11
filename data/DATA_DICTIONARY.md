# Dataset documentation: Bengaluru daily weather and air quality, 2023–2025

## Source and collection
This dataset was not collected by our group. It was downloaded from two public APIs run by Open-Meteo (https://open-meteo.com):

- Historical Weather API (https://open-meteo.com/en/docs/historical-weather-api): ERA5 reanalysis from ECMWF. Variables used: temperature at 2 m, relative humidity at 2 m, precipitation.
- Air Quality API (https://open-meteo.com/en/docs/air-quality-api): CAMS atmospheric composition model from ECMWF. Variables used: PM2.5, PM10, nitrogen dioxide, ozone, US AQI.

Open-Meteo states that its data is licensed CC BY 4.0 and must be attributed to Open-Meteo.

Important limitation: these values are modelled or reanalysed on a grid, not measured by a ground station. They describe the grid cell around the point below and can differ from readings at a single monitor, for example a CPCB station.

- Location: Bengaluru, India (latitude 12.97, longitude 77.59, elevation about 914 m)
- Period: 1 January 2023 to 31 December 2025 (1,096 days)
- Time zone: Asia/Kolkata (IST)
- Download date: 11 November 2026
- Sampling approach: all available hourly values for the period were downloaded (no sampling), then aggregated to one row per day.
- Selection reason: the topic requires daily temperature, humidity, rainfall and air-quality readings from reliable sources. Open-Meteo provides all four for the same place and period and needs no key.

## Files
- `raw/weather.json`, `raw/aq.json`: hourly data exactly as returned by the APIs.
- `bengaluru_daily_2023_2025.csv`: daily aggregated data (10 columns).
- `bengaluru_daily_clean.csv`: the same data plus derived columns (16 columns), used for all charts.
- `analysis_summary.txt`: printed output of the analysis script.

## Columns
| Column | Meaning | Unit | Daily aggregation of hourly values |
|---|---|---|---|
| date | Calendar date (YYYY-MM-DD) | n/a | n/a |
| temp_mean | Air temperature at 2 m | °C | mean |
| temp_max | Highest hourly temperature | °C | maximum |
| temp_min | Lowest hourly temperature | °C | minimum |
| humidity_mean | Relative humidity at 2 m | % | mean |
| rainfall_mm | Precipitation | mm | sum |
| pm25 | Particulate matter under 2.5 µm | µg/m³ | mean |
| pm10 | Particulate matter under 10 µm | µg/m³ | mean |
| no2 | Nitrogen dioxide | µg/m³ | mean |
| ozone | Ozone | µg/m³ | mean |
| aqi_us | US Air Quality Index (hourly value, then averaged) | index 0–500 | mean |

Derived columns in `bengaluru_daily_clean.csv`:

| Column | Meaning |
|---|---|
| year, month | Taken from date |
| season | Winter (Dec–Feb), Summer (Mar–May), Monsoon (Jun–Sep), Post-monsoon (Oct–Nov) |
| aqi_cat | US AQI band: Good (0–50), Moderate (51–100), Unhealthy for sensitive groups (101–150), Unhealthy (151–200), Very unhealthy (201+) |
| rainy | True when rainfall_mm is 2.5 or more (the usual definition of a rainy day) |

## Data quality checks
| Check | Result | Handling |
|---|---|---|
| Missing values | 0 of 10,960 cells | none needed |
| Duplicate dates | 0 | none needed |
| Consistency: temp_min ≤ temp_mean ≤ temp_max | holds on all days | none needed |
| Valid ranges: humidity 0–100 %, rainfall and pollutants not negative, temperature between −10 and 50 °C | all values valid | none needed |
| Outliers (1.5 × IQR rule) | present, mainly in rainfall (140 days, because most days have little or no rain), temperature and NO2 | kept: they are real weather extremes, not errors |
| Units | consistent within each column | none needed |

The data contains no personal or sensitive information.

## Known limits
- Modelled grid data, not station measurements.
- Three years is too short to judge climate trends. Only seasonal patterns are discussed.
- Relationships in the charts are correlations in observational data and do not show cause and effect.
