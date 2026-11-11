# Project Checklist: what to open, what to check

Project folder: `/Users/nihakp/Documents/RVU/SEM3/IDA/Poster/`
Explanations of every concept and chart are in `LEARNING_GUIDE.md`. This file tells you **which file to open, what to look for, and how to verify it yourself.**

Tick each box as you go: `- [ ]` becomes `- [x]`.

---

## 1. Where everything is

```
Poster/
├── LEARNING_GUIDE.md                       ← read this first (explains everything)
├── checklist.md                            ← this file
├── Bengaluru_Weather_AQ_Visualization.ipynb  ← the Colab notebook (code + outputs)
├── data/
│   ├── raw/weather.json, aq.json           ← hourly data exactly as downloaded
│   ├── bengaluru_daily_2023_2025.csv       ← the dataset (1,096 rows, 10 columns)
│   ├── bengaluru_daily_clean.csv           ← dataset + helper columns (used for charts)
│   ├── DATA_DICTIONARY.md                  ← source, period, column meanings, checks
│   └── analysis_summary.txt                ← printed analysis output
├── figures/01…07_*.png                     ← the 7 report charts
├── poster/
│   ├── Bengaluru_Weather_Air_Quality_Poster.pdf   ← FINAL POSTER
│   ├── poster.html, fig/*.png              ← poster source and its 5 charts
├── report/
│   ├── Bengaluru_Weather_AQ_Report.pdf     ← FINAL REPORT (submit this)
│   └── Bengaluru_Weather_AQ_Report.docx    ← editable version
└── scripts/                                ← Python code that builds everything
```

**The four files you submit on Google Classroom:**
1. `report/Bengaluru_Weather_AQ_Report.pdf`
2. `data/bengaluru_daily_2023_2025.csv`
3. `Bengaluru_Weather_AQ_Visualization.ipynb`
4. `poster/Bengaluru_Weather_Air_Quality_Poster.pdf`

Not part of your work (course material, left out of GitHub): the screenshots, `1.png`, the sample poster PDF, the assignment `.docx` and `report template  (1).docx`.

---

## 2. Suggested review order (about 2 hours)

- [ ] **1. Poster PDF** (10 min). Open `poster/Bengaluru_Weather_Air_Quality_Poster.pdf`. Read it like a visitor. Can you explain each box?
- [ ] **2. `LEARNING_GUIDE.md`** (40 min). Read Parts 1 to 8 fully. Skim Parts 9 to 13.
- [ ] **3. `data/DATA_DICTIONARY.md` and the CSV** (15 min). Open the CSV in Excel or Numbers. Look at 10 rows. Match each column to the dictionary.
- [ ] **4. The notebook in Colab** (25 min). See section 5 below. Run it and read every cell's output.
- [ ] **5. The report PDF** (20 min). Skim chapters 1 to 6. Read chapter 4 properly.
- [ ] **6. The scripts** (10 min). Open `scripts/analyse.py` and `scripts/build_daily.py`. They are short. The others are for formatting.
- [ ] **7. Verify the numbers yourself** (15 min). Section 4 below.
- [ ] **8. Practise the viva questions** (20 min). `LEARNING_GUIDE.md`, Part 10. Answer out loud without reading.

---

## 3. File-by-file: what to check

### Data
| File | Check |
|---|---|
| `data/raw/weather.json` | Open it. Find `"hourly"`, `"time"`, `"temperature_2m"`. This is what the API returned, untouched. |
| `data/bengaluru_daily_2023_2025.csv` | Exactly **1,096 rows** plus a header. First date `2023-01-01`, last `2025-12-31`. 11 columns including `date`. No blanks. |
| `data/bengaluru_daily_clean.csv` | Same rows, extra columns `year, month, season, aqi_cat, rainy`. |
| `data/DATA_DICTIONARY.md` | Says the data was **not collected by the group**, names the sources, gives the download date (11 Nov 2026), lists units. |

- [ ] I can say where the data came from in one sentence.
- [ ] I can name all 10 columns and their units.
- [ ] I know why rainfall is summed but temperature is averaged.

### Notebook
| File | Check |
|---|---|
| `Bengaluru_Weather_AQ_Visualization.ipynb` | Has 6 numbered sections: Setup, Collect, Prepare, Analysis, Visualisation, Download. Every code cell shows its output. 7 charts appear. |

### Poster
| File | Check |
|---|---|
| `poster/Bengaluru_Weather_Air_Quality_Poster.pdf` | One page, A1 landscape. All five names and USNs. Sections 01 to 08, five figures, references strip. Every chart has a heading and a caption. |

- [ ] Names and USNs are spelled correctly.
- [ ] I can explain Fig 1 to Fig 5 without looking.

### Report
| File | Check |
|---|---|
| `report/Bengaluru_Weather_AQ_Report.pdf` | 25 pages. Cover, declaration, certificate, contents, list of figures, abbreviations, chapters 1.0 to 6.0, references, 2 appendices. |

- [ ] Cover, declaration and certificate show all five names and USNs, course `CS2214 Introduction to Data Analysis`.
- [ ] Faculty name on the certificate: Priyanka S Shivaramaiah.
- [ ] Chapter 4 has 7 figures, each followed by a paragraph explaining it.
- [ ] Section 4.8 has 5 findings and 4.9 has 3 recommendations.
- [ ] No sentence says rain "causes" or "cleans" the air.

### Code
| File | What it does |
|---|---|
| `scripts/build_daily.py` | Raw JSON to daily CSV. |
| `scripts/analyse.py` | Checks, helper columns, printed analysis. |
| `scripts/make_figures.py` | The 7 report charts. |
| `scripts/make_poster_figures.py` | The 5 poster charts. |
| `scripts/build_poster.py` | Builds the poster HTML (numbers computed from data). |
| `scripts/build_report.py` | Builds the Word report from the template. |

---

## 4. Verify the key numbers yourself

Open Terminal, then:

```bash
cd /Users/nihakp/Documents/RVU/SEM3/IDA/Poster
python3 - <<'EOF'
import pandas as pd
df = pd.read_csv("data/bengaluru_daily_clean.csv", parse_dates=["date"])
print("rows, missing cells      :", len(df), df.isna().sum().sum())
mon = df[df.season == "Monsoon"]; oth = df[df.season != "Monsoon"]
print("Good days monsoon / other:", round((mon.aqi_cat=="Good").mean()*100), round((oth.aqi_cat=="Good").mean()*100))
print("median PM2.5 dry / rainy :", round(df[~df.rainy].pm25.median(),1), round(df[df.rainy].pm25.median(),1))
print("days dry / rainy         :", (~df.rainy).sum(), df.rainy.sum())
print("PM2.5 > 15 (WHO) / > 60  :", (df.pm25>15).sum(), (df.pm25>60).sum())
print("AQI > 100 days / in monsoon:", (df.aqi_us>100).sum(), (mon.aqi_us>100).sum())
print("months with mean PM2.5>15:", (df.groupby("month").pm25.mean()>15).sum())
print("Spearman rain vs PM2.5   :", round(df.pm25.corr(df.rainfall_mm, method="spearman"),2))
EOF
```

**Expected output:**

| Line | Expected |
|---|---|
| rows, missing cells | `1096 0` |
| Good days monsoon / other | `64 6` |
| median PM2.5 dry / rainy | `23.7 9.0` |
| days dry / rainy | `803 293` |
| PM2.5 > 15 (WHO) / > 60 | `675 2` |
| AQI > 100 days / in monsoon | `199 0` |
| months with mean PM2.5 > 15 | `8` |
| Spearman rain vs PM2.5 | `-0.58` |

- [ ] All eight lines match the poster and the report.

Needs `pandas` (`pip3 install pandas`).

### Re-run the whole pipeline (optional)
```bash
python3 scripts/build_daily.py "$PWD"        # raw JSON to daily CSV
python3 scripts/analyse.py "$PWD"            # checks + clean CSV + printed analysis
python3 scripts/make_figures.py "$PWD"       # 7 report charts
python3 scripts/make_poster_figures.py "$PWD"  # 5 poster charts
python3 scripts/build_poster.py "$PWD"       # poster HTML
```
Then check nothing changed: `git status`. The two CSV files should show **no change**. The PNG charts may show as modified because your matplotlib version can write slightly different image bytes; they will look the same.

To print the poster HTML to PDF (needs Google Chrome):
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf=poster/Bengaluru_Weather_Air_Quality_Poster.pdf poster/poster.html
```

**About the report script:** `scripts/build_report.py` needs `pip3 install python-docx scipy pandas` and LibreOffice to make the PDF. Re-running it without the page-number file fills the contents page with zeros. **If you only need to change a few words, edit the `.docx` in Word and export to PDF instead.**

---

## 5. Run the notebook in Google Colab

- [ ] Go to colab.research.google.com, then **File → Upload notebook**, and pick `Bengaluru_Weather_AQ_Visualization.ipynb`.
- [ ] **Runtime → Run all.** It takes about a minute.
- [ ] Confirm each section prints a result and all 7 charts appear.
- [ ] The last cell offers a zip of the figures and the clean CSV to download. That is expected.
- [ ] If numbers differ slightly from the poster, that is because the notebook downloads **fresh** data and Open-Meteo may have revised its model values. The poster and report use the data saved on 11 Nov 2026. See `LEARNING_GUIDE.md`, Part 13.

---

## 6. Assignment requirements: where each one is met

### Dataset (assignment section 4)
| Requirement | Where |
|---|---|
| At least 30 records, with date | 1,096 daily rows with `date` |
| At least five attributes, clear headings, consistent units | 10 attributes. Units in `DATA_DICTIONARY.md` and report Table 2.2 |
| Document source, period, sampling approach, attribute meaning | `DATA_DICTIONARY.md`; report 2.1 to 2.3; poster section 03 and 04 |
| Check missing, duplicates, inconsistent, invalid; describe handling | Report 2.4 and Table 2.3; poster section 05; `scripts/analyse.py` |
| No sensitive personal data | Weather and air-quality data only |
| Cite public source, do not call it group-collected | Poster: "Public data, not collected by our group"; report 2.1; references |

### Analysis and visualisation (section 5)
| Requirement | Where |
|---|---|
| Python with Matplotlib | All scripts and the notebook |
| At least 4 charts, at least 3 types | 7 report charts, 5 poster charts: line, bar, box plot, stacked bar, heatmap |
| Title, labelled axes, units, legend when needed | Check each figure |
| Interpret each chart | A paragraph after every figure in chapter 4; a caption under every poster chart |
| At least 3 findings, 2 recommendations | 5 findings (4.8) and 3 recommendations (4.9) |
| No causal claims from correlations | Wording says "lower on", "associated with"; limitations stated in 4.10 |

### Poster (section 6)
| Requirement | Where |
|---|---|
| Title, names and USNs of all five | Poster header |
| Problem, objectives, method and source, dataset, cleaning, charts, findings, recommendations, conclusion, references | Poster sections 01 to 08 and the references strip |
| Own charts, no decorative images | Five data charts only |
| A1 or A2, readable PDF | A1 landscape, one page |

### Submission checklist (section 8)
- [ ] One consolidated report in PDF
- [ ] Original dataset in CSV
- [ ] Python code or Colab notebook with outputs
- [ ] Final poster in PDF
- [ ] All five names and USNs in the report and poster

---

## 7. Still to do before submitting

- [ ] **Faculty approval of the topic.** The assignment says to get it before starting. Confirm you have it.
- [ ] **Sign the report.** Open the `.docx`: add signatures in the declaration table and a date. The certificate needs the faculty's signature and date. Re-export to PDF if you edit.
- [ ] **Certificate wording.** It says "Continuous Internal Evaluation". If your course has a numbered one (for example CIE-3), change it.
- [ ] **Group number** is not on the poster. Add it if your faculty wants it.
- [ ] **Contents page numbers.** If you edit the Word file and pages shift, update the contents page by hand.
- [ ] **Choose one representative** to upload everything to Google Classroom before the deadline.

---

## 8. Presentation preparation

- [ ] Everyone has read `LEARNING_GUIDE.md` Parts 1 to 8.
- [ ] Split the talk (Part 11 of the guide has a suggested split). Time it once.
- [ ] Each member can answer: where did the data come from, how was it cleaned, what does each chart show, what are the findings, what are the limits.
- [ ] Everyone has practised the 22 viva questions in Part 10.
- [ ] Everyone has run the notebook in Colab at least once.
- [ ] Bring the poster PDF and the notebook open on a laptop in case you are asked to show the code.

**The three things never to say:**
1. "We collected the data." (It was downloaded.)
2. "Rain reduces pollution." (Say "PM2.5 is lower on rainy days".)
3. "These are measurements." (Say "modelled values".)

---

## 9. GitHub

- [ ] Create an empty repository `bengaluru-weather-air-quality-poster` on github.com (owner `niha4527`). Leave README, .gitignore and licence **unticked**.
- [ ] In the project folder:
  ```bash
  git remote add origin https://github.com/niha4527/bengaluru-weather-air-quality-poster.git
  git push -u origin main
  ```
  When asked for a password, paste a **personal access token** (github.com/settings/tokens, scope `repo`). Normal passwords no longer work.
- [ ] `LEARNING_GUIDE.md` and `checklist.md` are already committed, so that one push sends them too.
- [ ] Open the repository page and confirm the files are there. If you edit anything later: `git add -A`, `git commit -m "your message"`, `git push`.
