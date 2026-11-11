"""Build version 2 of the project report (.docx) from the RV University report template.

Same data, tables and figures as build_report.py. Only the prose changed: plainer wording, no decorative bold,
no en or em dashes, straight quotes.

Usage: python build_report_v2.py <project dir> [pages_v2.json]
Needs python-docx and scipy. pages_v2.json (optional) holds TOC page numbers from a first render.
"""
import copy
import json
import os
import re
import sys

import docx
import pandas as pd
import scipy.stats as st
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

root = sys.argv[1]
pages = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
df = pd.read_csv(f"{root}/data/bengaluru_daily_clean.csv", parse_dates=["date"])
TEMPLATE = f"{root}/report template  (1).docx"
OUT = f"{root}/report/Bengaluru_Weather_AQ_Report_v2.docx"

TITLE = "Weather and Air Quality in Bengaluru, 2023-2025: A Data Visualization Study"
MEMBERS = [("Hiranamyi Kiran Gudekota", "1RUA25CSE0191"), ("Neharika Anantha Gowda", "1RUA25CSE0290"),
           ("Niharika K P", "1RUA25CSE0292"), ("Sai Yasasvi Kancharla", "1RUA25CSE0407"), ("Sonali Ayyappa", "1RUA25CSE0455")]
FACULTY = "Priyanka S Shivaramaiah"
COURSE, CODE = "Introduction to Data Analysis", "CS2214"

# ------------------------------------------------------------------ statistics
n = len(df)
SEAS = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
MN = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September",
      "October", "November", "December"]
mon, oth = df[df.season == "Monsoon"], df[df.season != "Monsoon"]
good_mon = (mon.aqi_cat == "Good").mean() * 100
good_oth = (oth.aqi_cat == "Good").mean() * 100
good_mon_n, good_oth_n = int((mon.aqi_cat == "Good").sum()), int((oth.aqi_cat == "Good").sum())
dry, rainy = df[~df.rainy], df[df.rainy]
mw = st.mannwhitneyu(dry.pm25, rainy.pm25, alternative="two-sided")
rho = lambda a, b: df[a].corr(df[b], method="spearman")
who_days, who_pct = int((df.pm25 > 15).sum()), (df.pm25 > 15).mean() * 100
cpcb_days = int((df.pm25 > 60).sum())
pm10_who, pm10_cpcb = int((df.pm10 > 45).sum()), int((df.pm10 > 100).sum())
aqi100 = int((df.aqi_us > 100).sum()); aqi100_pct = aqi100 / n * 100
assert int((mon.aqi_us > 100).sum()) == 0
mm = df.groupby("month").agg(t=("temp_mean", "mean"), tmax=("temp_max", "mean"), tmin=("temp_min", "mean"),
                            h=("humidity_mean", "mean"), pm=("pm25", "mean"), aqi=("aqi_us", "mean"))
mm["rain"] = df.groupby("month").rainfall_mm.sum() / df.year.nunique()
months_above = int((mm.pm > 15).sum())
assert months_above == 8 and set(mm.index[mm.pm <= 15]) == {6, 7, 8, 9}
ss = df.groupby("season").mean(numeric_only=True).loc[SEAS]
ss_rain = (df.groupby("season").rainfall_mm.sum() / df.year.nunique()).loc[SEAS]
yr = df.groupby("year").agg(t=("temp_mean", "mean"), h=("humidity_mean", "mean"), pm=("pm25", "mean"),
                           aqi=("aqi_us", "mean"), rain=("rainfall_mm", "sum"))
tmax_row, tmin_row = df.loc[df.temp_max.idxmax()], df.loc[df.temp_min.idxmin()]
pm_peak, aqi_peak = df.loc[df.pm25.idxmax()], df.loc[df.aqi_us.idxmax()]
rain_peak = df.loc[df.rainfall_mm.idxmax()]
d = lambda ts: f"{ts:%-d %B %Y}"
pm_mon_mean, pm_oth_mean = mon.pm25.mean(), oth.pm25.mean()
ozone = df.groupby("season").ozone.mean()
sig = "p < 0.001" if mw.pvalue < 0.001 else f"p = {mw.pvalue:.3f}"
mx = lambda x: f"−{abs(x):.2f}" if x < 0 else f"{x:.2f}"
cat_ct = pd.crosstab(df.season, df.aqi_cat).reindex(SEAS)
outl = {c: int(((df[c] < df[c].quantile(.25) - 1.5 * (df[c].quantile(.75) - df[c].quantile(.25))) |
                (df[c] > df[c].quantile(.75) + 1.5 * (df[c].quantile(.75) - df[c].quantile(.25)))).sum())
        for c in ["rainfall_mm", "temp_mean", "no2", "pm25", "pm10"]}
n_days_40 = int((df.pm25 > 40).sum())
assert int((df[df.pm25 > 40].season == "Monsoon").sum()) == 0

# ------------------------------------------------------------------ document helpers
doc = docx.Document(TEMPLATE)
body = doc.element.body
logo_cover = copy.deepcopy(doc.paragraphs[21]._p)
logo_cert = copy.deepcopy(doc.paragraphs[69]._p)
for child in list(body):
    if child.tag != qn("w:sectPr"):
        body.remove(child)
FONT = "Times New Roman"
st_normal = doc.styles["Normal"]
st_normal.font.name = FONT
st_normal.font.size = Pt(12)
st_normal.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)

reg = []   # TOC registry: (level, num, title)
figs = []  # figure registry: (num, caption)


def plain(text):
    """Straight quotes, hyphens instead of en dashes."""
    return (text.replace("–", "-").replace("—", ", ").replace("“", '"').replace("”", '"')
            .replace("’", "'").replace("‘", "'"))


def run(p, text, size=12, bold=False, italic=False, color=None, font=FONT):
    r = p.add_run(plain(text))
    r.font.name = font
    r._r.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    r.font.size = Pt(size)
    r.bold, r.italic = bold, italic
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def rich(p, text, size=12, bold=False, italic=False, font=FONT, markup=True):
    """**bold** (only when markup=True) and //italic// markup."""
    for tok in re.split(r"(\*\*.*?\*\*|//.*?//)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            run(p, tok[2:-2], size, bold or markup, italic, font=font)
        elif tok.startswith("//"):
            run(p, tok[2:-2], size, bold, True, font=font)
        else:
            run(p, tok, size, bold, italic, font=font)


def para(text="", size=12, bold=False, italic=False, align="j", before=0, after=6, spacing=1.5,
         keep_next=False, break_before=False, indent=None, markup=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), spacing
    pf.keep_with_next, pf.page_break_before = keep_next, break_before
    if indent is not None:
        pf.left_indent = Cm(indent)
    p.alignment = {"j": WD_ALIGN_PARAGRAPH.JUSTIFY, "c": WD_ALIGN_PARAGRAPH.CENTER,
                   "l": WD_ALIGN_PARAGRAPH.LEFT, "r": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    if text:
        rich(p, text, size, bold, italic, markup=markup)
    return p


def centred(text, size, bold=False, italic=False, before=0, after=6, break_before=False):
    p = para("", align="c", before=before, after=after, spacing=1.0, break_before=break_before)
    run(p, text, size, bold, italic)
    return p


def bullets(items, size=12):
    for it in items:
        p = para("", size, align="j", after=3, spacing=1.5, indent=1.2)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        rich(p, "• " + it, size, markup=False)


def h1(num, title):
    reg.append((1, num, title))
    para(f"{num}  {title}", 14, True, align="l", before=0, after=10, keep_next=True, break_before=True)


def h2(num, title):
    reg.append((2, num, title))
    para(f"{num}  {title}", 12, True, align="l", before=8, after=4, keep_next=True)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


def borders(tbl, sz=4, color="808080"):
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz)); e.set(qn("w:space"), "0"); e.set(qn("w:color"), color)
        b.append(e)
    tbl._tbl.tblPr.append(b)


def fix_widths(t, widths):
    """Fixed layout so Word and LibreOffice both honour the column widths."""
    t.autofit = False
    for col, w in zip(t.columns, widths):
        col.width = Cm(w)
    for row in t.rows:
        for c, w in zip(row.cells, widths):
            c.width = Cm(w)


def table(caption, headers, rows, widths, align=None, size=10, note=None):
    para(f"**Table {caption[0]}:** {caption[1]}", 11, align="c", before=8, after=4, spacing=1.0, keep_next=True, markup=True)
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(t)
    align = align or ["l"] + ["c"] * (len(headers) - 1)
    for c, htxt in zip(t.rows[0].cells, headers):
        shade(c, "D9E2F3")
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(c.paragraphs[0], htxt, size, True)
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true")
    t.rows[0]._tr.get_or_add_trPr().append(th)
    for r in rows:
        cells = t.add_row().cells
        for c, v, a in zip(cells, r, align):
            p = c.paragraphs[0]
            p.alignment = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER}[a]
            rich(p, str(v), size, markup=False)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.line_spacing = 1.0
    fix_widths(t, widths)
    for row in t.rows[:-1]:  # keep the table on one page
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    if note:
        para(note, 10, italic=True, align="l", before=3, after=8, spacing=1.0)
    else:
        para("", 6, after=6, spacing=1.0)


def figure(path, width_cm, caption):
    num = f"4.{len(figs) + 1}"
    figs.append((num, caption))
    p = para("", align="c", before=6, after=2, spacing=1.0, keep_next=True)
    p.add_run().add_picture(f"{root}/figures/{path}", width=Cm(width_cm))
    para(f"**Figure {num}:** {caption}", 11, align="c", before=2, after=10, spacing=1.0, markup=True)


def set_pgnum(section, fmt, start=1):
    sp = section._sectPr
    for old in sp.findall(qn("w:pgNumType")):
        sp.remove(old)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt); pg.set(qn("w:start"), str(start))
    sp.find(qn("w:pgMar")).addnext(pg)


def footer_number(section):
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.font.name, r.font.size = FONT, Pt(11)
    for kind, txt in (("begin", None), (None, " PAGE "), ("end", None)):
        if kind:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), kind); r._r.append(f)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)


def insert_logo(logo_xml):
    body.findall(qn("w:sectPr"))[-1].addprevious(copy.deepcopy(logo_xml))


names_usn = [f"{a} ({b})" for a, b in MEMBERS]

# ================================================================== COVER
centred(TITLE, 18, True, after=14)
centred("A PROJECT REPORT", 14, True, before=6, after=10)
centred("Submitted by", 14, True, after=8)
for nm in names_usn:
    centred(nm, 14, True, after=2)
p = para("", align="c", before=12, after=0, spacing=1.0)
run(p, "as part of the ", 14, italic=True); run(p, "Continuous Internal Evaluation", 14, True, True)
centred("for the course", 14, italic=True, before=8, after=6)
centred(f"{CODE} {COURSE}", 16, True, after=6)
centred("Offered in", 14, italic=True, after=0)
centred("Semester III", 16, True, after=0)
centred("of", 16, italic=True, after=0)
centred("B.Tech. (Hons.)", 16, True, after=8)
insert_logo(logo_cover)
centred("School of Computer Science and Engineering", 16, True, before=8, after=0)
centred("RV University", 16, True, after=0)
centred("RV Vidyaniketan, 8th Mile, Mysore Road, Bengaluru, Karnataka, India - 560059", 14, True, after=8)
centred("November 2026", 14, True, after=0)

# ================================================================== DECLARATION
centred("DECLARATION", 16, True, after=14, break_before=True)
p = para("", align="j", after=10)
rich(p, f"We, the students listed below, of the 3rd semester **B.Tech in Computer Science & Engineering** at the School of "
        f"Computer Science and Engineering, **RV University**, hereby declare that the project work titled \"**{TITLE}**\" "
        "has been carried out by us and submitted in partial fulfilment for the award of degree in "
        "**Bachelor of Technology in Computer Science & Engineering** during the academic year **2026-2027**. "
        "Further, the matter presented in the project has not been submitted previously by anybody for the award of any "
        "degree or any diploma to any other University, to the best of our knowledge and faith.")
para("", after=6)
t = doc.add_table(rows=1, cols=3)
borders(t)
for cell, htxt in zip(t.rows[0].cells, ["Name", "USN", "Signature"]):
    shade(cell, "D9E2F3"); run(cell.paragraphs[0], htxt, 12, True)
for a, b in MEMBERS:
    cells = t.add_row().cells
    run(cells[0].paragraphs[0], a, 12); run(cells[1].paragraphs[0], b, 12)
for row in t.rows:
    row.height = Cm(1.1)
fix_widths(t, [7.2, 4.3, 4.5])
para("", after=14)
para("Place: Bengaluru", 12, align="l", after=10, spacing=1.0)
para("Date:", 12, align="l", after=0, spacing=1.0)

# ================================================================== CERTIFICATE
page_start = para("", 2, after=0, spacing=1.0, break_before=True)
insert_logo(logo_cert)
centred("School of Computer Science and Engineering", 16, True, before=8, after=0)
centred("RV University", 12, after=0)
centred("RV Vidyaniketan, 8th Mile, Mysore Road, Bengaluru, Karnataka, India - 560059", 12, after=20)
centred("CERTIFICATE", 16, True, before=14, after=16)
p = para("", align="j", after=14)
rich(p, f"This is to certify that the project work titled \"**{TITLE}**\" is performed by " +
        "; ".join(f"**{a} ({b})**" for a, b in MEMBERS) +
        f", bonafide students of Bachelor of Technology at the School of Computer Science and Engineering, RV University, "
        f"Bengaluru, as part of the **Continuous Internal Evaluation** for the course **{CODE} {COURSE}** offered in "
        "Semester III of Bachelor of Technology in Computer Science & Engineering, during the Academic year **2026-2027**.")
para("", after=18)
p = para("", 12, align="l", after=26, spacing=1.0)
rich(p, f"Name of Course Faculty: **{FACULTY}**", 12)
para("Signature with date of Faculty:", 12, align="l", after=0, spacing=1.0)

# ================================================================== TOC page (table inserted at the end)
centred("TABLE OF CONTENTS", 16, True, after=14, break_before=True)
toc_anchor = para("", 6, after=0, spacing=1.0)

# ================================================================== LISTS (section 2, roman numerals)
sec1 = doc.sections[0]
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
centred("LIST OF FIGURES", 16, True, after=14)
lof_anchor = para("", 6, after=0, spacing=1.0)
centred("LIST OF SYMBOLS AND ABBREVIATIONS", 16, True, after=14, break_before=True)
abbr = [("AQI", "Air Quality Index (here, the US AQI, scale 0-500)"),
        ("API", "Application Programming Interface"),
        ("CAMS", "Copernicus Atmosphere Monitoring Service"),
        ("CPCB", "Central Pollution Control Board, India"),
        ("CSV", "Comma-separated values (file format)"),
        ("ECMWF", "European Centre for Medium-Range Weather Forecasts"),
        ("ERA5", "Fifth-generation ECMWF atmospheric reanalysis"),
        ("IMD", "India Meteorological Department"),
        ("IQR", "Interquartile range"),
        ("NAAQS", "National Ambient Air Quality Standards (India)"),
        ("NO₂", "Nitrogen dioxide"),
        ("O₃", "Ozone"),
        ("PM2.5", "Particulate matter with diameter below 2.5 µm"),
        ("PM10", "Particulate matter with diameter below 10 µm"),
        ("ρ (rho)", "Spearman rank correlation coefficient"),
        ("SD", "Standard deviation"),
        ("USN", "University Seat Number"),
        ("US EPA", "United States Environmental Protection Agency"),
        ("WHO", "World Health Organization"),
        ("µg/m³", "Micrograms per cubic metre (unit of pollutant concentration)"),
        ("°C", "Degrees Celsius"),
        ("mm", "Millimetres (rainfall depth)")]
t = doc.add_table(rows=1, cols=2); borders(t)
for cell, htxt in zip(t.rows[0].cells, ["Symbol / abbreviation", "Meaning"]):
    shade(cell, "D9E2F3"); run(cell.paragraphs[0], htxt, 11, True)
for a, b in abbr:
    cells = t.add_row().cells
    run(cells[0].paragraphs[0], a, 11, True); run(cells[1].paragraphs[0], b, 11)
for row in t.rows:
    for cell in row.cells:
        cell.paragraphs[0].paragraph_format.space_after = Pt(2)
fix_widths(t, [4.2, 11.8])

# ================================================================== BODY (section 3, arabic numerals)
sec3 = doc.add_section(WD_SECTION.NEW_PAGE)

# ---- 1.0 INTRODUCTION
h1("1.0", "INTRODUCTION")
h2("1.1", "Background")
para("Temperature, humidity and rainfall describe the weather. Particulate matter (PM2.5 and PM10), nitrogen dioxide (NO₂) "
     "and ozone (O₃) describe the air people breathe. The two are connected in several ways: rain can remove particles from "
     "the air, and heat and sunlight help ozone form. Looking at both together, day by day, shows when the air is cleaner "
     "or dirtier and which weather goes with each.")
para("Bengaluru sits about 914 m above sea level and has a moderate climate with a clear monsoon season. Two benchmarks help "
     "judge the air. The World Health Organization (WHO) 2021 guideline for the 24-hour mean of PM2.5 is 15 µg/m³, and "
     "India's National Ambient Air Quality Standards (NAAQS) set a 24-hour limit of 60 µg/m³. We compare the observed "
     "levels with both.")
h2("1.2", "Problem Statement")
para("Using public daily data for Bengaluru from January 2023 to December 2025, we ask three questions. How do temperature, "
     "humidity and rainfall change through the year? How does air quality change alongside them? And in which seasons is "
     "the air worst compared with health guidelines?")
h2("1.3", "Objectives")
bullets(["Describe the seasonal pattern of temperature, humidity and rainfall in Bengaluru.",
         "Measure how PM2.5, PM10, NO₂, ozone and the US AQI vary by month and by season.",
         "Compare air quality on rainy days and dry days.",
         "Check the observed air quality against WHO and CPCB benchmarks.",
         "Present the results as labelled Python charts, with evidence-based findings and practical recommendations."])
h2("1.4", "Scope and Limitations")
para("The study covers one location (Bengaluru), three years (1,096 days) and ten daily variables. The data are modelled "
     "grid values from a public service. They are not readings from a ground monitor, and our group did not collect "
     "them. The analysis is observational, so it shows patterns and associations but cannot show cause and effect. "
     "Three years are enough to describe the yearly cycle and too few to judge long-term trends.")
h2("1.5", "Organisation of the Report")
para("Chapter 2 covers the dataset and how we prepared it, and Chapter 3 the analysis methods. Chapter 4 gives the results, "
     "findings and recommendations. Chapters 5 and 6 are the conclusion and the future scope.")

# ---- 2.0 DATASET AND METHODOLOGY
h1("2.0", "DATASET AND METHODOLOGY")
h2("2.1", "Data Source and Selection")
para("We did not collect these data. We downloaded them from two public application programming interfaces (APIs) run by "
     "Open-Meteo (open-meteo.com). Open-Meteo states that its data are licensed under CC BY 4.0, so we credit it here and "
     "on the poster. Table 2.1 lists the two products.")
table(("2.1", "Data sources used"),
      ["Product", "Underlying data", "Variables used", "Resolution"],
      [["Open-Meteo Historical Weather API", "ERA5 reanalysis (ECMWF)", "Temperature at 2 m, relative humidity at 2 m, precipitation", "Hourly"],
       ["Open-Meteo Air Quality API", "CAMS atmospheric composition model (Copernicus / ECMWF)", "PM2.5, PM10, NO₂, ozone, US AQI", "Hourly"]],
      [4.2, 4.6, 5.2, 2.0], ["l", "l", "l", "c"])
para("We chose Open-Meteo because the topic asks for temperature, humidity, rainfall and air-quality readings from reliable "
     "sources, and Open-Meteo has all four for the same place and dates. The format is consistent, no access key is needed, "
     "and anyone can repeat the download. Its inputs, ERA5 and CAMS, come from established meteorological centres.")
h2("2.2", "Location, Period and Sampling Approach")
bullets(["Location: Bengaluru, India (latitude 12.97° N, longitude 77.59° E, elevation about 914 m).",
         "Period: 1 January 2023 to 31 December 2025, which is 1,096 days.",
         "Time zone: Asia/Kolkata (IST).",
         "Download date: 11 November 2026.",
         "Sampling approach: none. We downloaded every hourly value for the period and combined them into one row per day."])
h2("2.3", "Dataset Description")
para(f"The prepared dataset has {n:,} daily records and 10 attributes, with no missing values. Each attribute uses a single "
     "unit throughout. Table 2.2 gives the meaning, unit and daily aggregation of each one.")
table(("2.2", "Attributes of the daily dataset"),
      ["Attribute", "Meaning", "Unit", "Daily value from hourly data"],
      [["date", "Calendar date (YYYY-MM-DD)", "-", "-"],
       ["temp_mean", "Air temperature at 2 m", "°C", "mean"],
       ["temp_max", "Highest hourly temperature", "°C", "maximum"],
       ["temp_min", "Lowest hourly temperature", "°C", "minimum"],
       ["humidity_mean", "Relative humidity at 2 m", "%", "mean"],
       ["rainfall_mm", "Precipitation", "mm", "sum"],
       ["pm25", "Particulate matter below 2.5 µm", "µg/m³", "mean"],
       ["pm10", "Particulate matter below 10 µm", "µg/m³", "mean"],
       ["no2", "Nitrogen dioxide", "µg/m³", "mean"],
       ["ozone", "Ozone", "µg/m³", "mean"],
       ["aqi_us", "US Air Quality Index", "0-500", "mean of hourly values"]],
      [3.2, 6.2, 2.2, 4.2], ["l", "l", "c", "c"])
h2("2.4", "Data Preparation and Cleaning")
para("We joined the two hourly series on the date and aggregated them to daily values as shown in Table 2.2. We then ran the "
     "checks in Table 2.3, which also shows how each was handled.")
table(("2.3", "Data-quality checks and handling"),
      ["Check", "Result", "Handling"],
      [["Missing values", f"0 of {n * 10:,} cells", "None needed"],
       ["Duplicate dates", "0", "None needed"],
       ["Temperature order (min ≤ mean ≤ max)", "Holds on all days", "None needed"],
       ["Humidity between 0 and 100 %", "All values valid", "None needed"],
       ["Rainfall and pollutants not negative", "All values valid", "None needed"],
       ["Temperature between −10 and 50 °C", "All values valid", "None needed"],
       ["Outliers (1.5 × IQR rule)",
        f"Present: {outl['rainfall_mm']} days for rainfall, {outl['temp_mean']} for mean temperature, {outl['no2']} for NO₂, "
        f"{outl['pm25']} for PM2.5 and {outl['pm10']} for PM10",
        "Kept. They are real extremes, not errors"],
       ["Units", "One unit per column", "None needed"]],
      [5.4, 5.4, 5.0], ["l", "l", "l"])
para(f"Rainfall has many outliers under the 1.5 × IQR rule because most days have little or no rain, so any wet day sits far "
     f"above the interquartile range. The highest daily maximum temperature was {tmax_row.temp_max:.1f} °C on {d(tmax_row.date)}. "
     "We kept all of these values. The dataset has no personal or sensitive information.")
h2("2.5", "Derived Variables and Benchmarks")
para("We derived four variables.")
bullets(["Season: Winter (December to February), Summer (March to May), Monsoon (June to September) and Post-monsoon (October to November).",
         "AQI category: the US AQI band of each day. Good (0-50), Moderate (51-100), Unhealthy for sensitive groups (101-150) "
         "and Unhealthy (151-200). No day reached 201 or above.",
         "Rainy day: a day with 2.5 mm of rain or more. All other days are dry days.",
         "Year and month: taken from the date."])
table(("2.4", "Air-quality benchmarks used"),
      ["Pollutant", "WHO 2021 guideline (24-hour)", "CPCB NAAQS limit (24-hour)"],
      [["PM2.5", "15 µg/m³", "60 µg/m³"], ["PM10", "45 µg/m³", "100 µg/m³"]],
      [4.0, 6.0, 6.0])
h2("2.6", "Tools and Reproducibility")
para("We used Python 3 throughout: pandas and NumPy for data handling, SciPy for the statistical test and Matplotlib for every "
     "chart. The whole workflow, from download to charts, is in a Google Colab notebook "
     "(//Bengaluru_Weather_AQ_Visualization.ipynb//) and in the project's scripts, so every number in this report can be "
     "regenerated. Appendix B lists the files.")

# ---- 3.0 METHOD OF ANALYSIS
h1("3.0", "METHOD OF ANALYSIS")
h2("3.1", "Descriptive Statistics")
para("For each variable we computed the mean, standard deviation, minimum, median and maximum over the 1,096 days (Table 4.1). "
     "These show the typical level and spread before any comparison.")
h2("3.2", "Seasonal and Monthly Aggregation")
para("We grouped the daily values by season and by calendar month. In the month-wise charts, rainfall is the average yearly "
     "total for that month (the three-year total divided by three) and the other variables are three-year means. Grouping "
     "smooths day-to-day noise and shows the yearly cycle.")
h2("3.3", "Comparison of Rainy and Dry Days")
para("We compared daily PM2.5 on rainy days (2.5 mm or more) and dry days using medians and a box plot. A two-sided "
     "Mann-Whitney U test gave an indicative check of whether the two groups differ; it does not assume normally "
     "distributed data. Consecutive days are not fully independent, so we read the p-value as a guide to the size of the "
     "difference and not as an exact probability.")
h2("3.4", "Correlation Analysis")
para("We measured relationships between variables with the Spearman rank correlation coefficient (ρ). We chose it over "
     "Pearson's coefficient because rainfall is heavily skewed with many zeros, and because the relationships only need to be "
     "monotonic, not linear. A value near +1 means two variables tend to rise together, near −1 means one tends to fall as "
     "the other rises, and near 0 means no consistent link. Correlation describes association only.")
h2("3.5", "Comparison with Benchmarks")
para("We counted the days above the WHO and CPCB limits (Table 2.4) for PM2.5 and PM10, and the days with a US AQI above 100, "
     "the point where air quality is rated unhealthy for sensitive groups.")
h2("3.6", "Visualization Design")
para("We drew seven charts with Matplotlib. Each has a title, labelled axes with units and readable scales, and a legend "
     "wherever more than one colour or line appears. The colours stay distinguishable for readers with colour-vision "
     "deficiency: one blue ramp for magnitude, blue and orange for two groups, and a blue-red scale centred on grey for "
     "correlations. No chart uses two vertical axes; variables with different units get separate panels. Table 3.1 lists "
     "the chart types and their purposes.")
table(("3.1", "Charts used"),
      ["Figure", "Chart type", "Purpose"],
      [["4.1", "Line plot with band, and bar chart", "Monthly temperature, humidity and rainfall"],
       ["4.2", "Calendar heatmap", "Daily AQI across three years"],
       ["4.3", "Line plot", "Daily PM2.5 and its 30-day average"],
       ["4.4", "Bar chart (two panels)", "Monthly PM2.5 against the WHO guideline, with rainfall"],
       ["4.5", "Box plot", "PM2.5 distribution on dry and rainy days"],
       ["4.6", "Stacked bar chart", "Share of days in each AQI category, by season"],
       ["4.7", "Correlation heatmap", "Relationships between weather and pollutants"]],
      [2.0, 5.4, 8.6], ["c", "l", "l"])

# ---- 4.0 RESULTS AND DISCUSSION
h1("4.0", "RESULTS AND DISCUSSION")
h2("4.1", "Overview of the Data")
rows = []
for col, label, unit in [("temp_mean", "Mean temperature", "°C"), ("temp_max", "Maximum temperature", "°C"),
                         ("temp_min", "Minimum temperature", "°C"), ("humidity_mean", "Relative humidity", "%"),
                         ("rainfall_mm", "Rainfall (daily total)", "mm"), ("pm25", "PM2.5", "µg/m³"),
                         ("pm10", "PM10", "µg/m³"), ("no2", "NO₂", "µg/m³"), ("ozone", "Ozone", "µg/m³"),
                         ("aqi_us", "US AQI", "index")]:
    s = df[col]
    rows.append([label, unit, f"{s.mean():.1f}", f"{s.std():.1f}", f"{s.min():.1f}", f"{s.median():.1f}", f"{s.max():.1f}"])
table(("4.1", "Descriptive statistics of the daily data (1,096 days)"),
      ["Variable", "Unit", "Mean", "SD", "Min", "Median", "Max"], rows, [4.6, 1.6, 1.8, 1.8, 1.8, 2.0, 1.8],
      ["l", "c", "c", "c", "c", "c", "c"])
para(f"Daily mean temperature averaged {df.temp_mean.mean():.1f} °C, with a hottest daily maximum of {tmax_row.temp_max:.1f} °C "
     f"({d(tmax_row.date)}) and a coldest daily minimum of {tmin_row.temp_min:.1f} °C ({d(tmin_row.date)}). Humidity ranged widely, from "
     f"{df.humidity_mean.min():.0f} % to {df.humidity_mean.max():.0f} %. The heaviest rain in one day was {rain_peak.rainfall_mm:.1f} mm "
     f"({d(rain_peak.date)}). Mean PM2.5 was {df.pm25.mean():.1f} µg/m³, with a highest daily value of {pm_peak.pm25:.1f} µg/m³ on {d(pm_peak.date)}. "
     f"The highest daily AQI was {aqi_peak.aqi_us:.0f} on {d(aqi_peak.date)}. Yearly rainfall totals were "
     f"{yr.rain[2023]:.0f} mm (2023), {yr.rain[2024]:.0f} mm (2024) and {yr.rain[2025]:.0f} mm (2025).")

h2("4.2", "Seasonal Pattern of Weather")
figure("01_monthly_climate.png", 11.0, "Monthly temperature, humidity and rainfall in Bengaluru, 2023-2025 (temperature in °C, humidity in %, rainfall in mm per year).")
para(f"Figure 4.1 shows the yearly cycle. Mean temperature peaks in {MN[int(mm.t.idxmax())]} ({mm.t.max():.1f} °C) and is lowest in "
     f"{MN[int(mm.t.idxmin())]} ({mm.t.min():.1f} °C). The gap between the daily minimum and maximum is widest in the dry months "
     f"February to April, when the daily maximum averages up to {mm.tmax.max():.1f} °C. Relative humidity is lowest in "
     f"{MN[int(mm.h.idxmin())]} ({mm.h.min():.0f} %) and highest in {MN[int(mm.h.idxmax())]} ({mm.h.max():.0f} %). Rain falls mostly "
     f"from May to October, with almost none in February. The Monsoon brings {ss_rain['Monsoon'] / ss_rain.sum() * 100:.0f} % of the yearly rain "
     f"(on average {ss_rain['Monsoon']:.0f} mm), against {ss_rain['Post-monsoon']:.0f} mm in Post-monsoon, {ss_rain['Summer']:.0f} mm in Summer and "
     f"{ss_rain['Winter']:.0f} mm in Winter (Table 4.2).")
rows = [[s, f"{ss.loc[s, 'temp_mean']:.1f}", f"{ss.loc[s, 'humidity_mean']:.0f}", f"{ss_rain[s]:.0f}", f"{ss.loc[s, 'pm25']:.1f}",
         f"{ss.loc[s, 'pm10']:.1f}", f"{ss.loc[s, 'no2']:.1f}", f"{ss.loc[s, 'ozone']:.0f}", f"{ss.loc[s, 'aqi_us']:.0f}"] for s in SEAS]
table(("4.2", "Seasonal means (rainfall is the average yearly total for the season)"),
      ["Season", "Temp (°C)", "Humidity (%)", "Rain (mm)", "PM2.5", "PM10", "NO₂", "Ozone", "AQI"], rows,
      [3.0, 1.7, 2.0, 1.7, 1.6, 1.6, 1.5, 1.6, 1.3], size=9.5,
      note="PM2.5, PM10, NO₂ and ozone are in µg/m³.")

h2("4.3", "Air Quality Through the Years")
figure("02_aqi_calendar.png", 15.5, "Calendar heatmap of the daily US AQI in Bengaluru, 2023-2025. Each square is one day; paler squares mean lower AQI.")
para(f"In Figure 4.2 the paler squares of the monsoon months, June to September, form a band that repeats every year, while "
     f"darker squares dominate January to May and October to December. The highest AQI day was {d(aqi_peak.date)} (AQI {aqi_peak.aqi_us:.0f}). "
     f"Across the whole period the AQI reached the \"unhealthy\" band (151-200) on only {int((df.aqi_us > 150).sum())} days.")
figure("07_pm25_timeseries.png", 16.0, "Daily PM2.5 (thin line) and its 30-day centred average (thick line), with the WHO guideline of 15 µg/m³ (dashed).")
para(f"Figure 4.3 shows the same cycle for PM2.5. The 30-day average falls below the WHO guideline in each monsoon "
     f"and rises above it for the rest of the year. All {n_days_40} days above 40 µg/m³ fall outside the monsoon. The highest day, "
     f"{d(pm_peak.date)}, reached {pm_peak.pm25:.1f} µg/m³. Yearly mean PM2.5 was {yr.pm[2023]:.1f}, {yr.pm[2024]:.1f} and "
     f"{yr.pm[2025]:.1f} µg/m³ in 2023, 2024 and 2025. These are close, so the three years show a stable seasonal pattern "
     "but no clear long-term trend.")

h2("4.4", "PM2.5 by Month and Rainfall")
figure("06_pm25_vs_rain_by_month.png", 12.0, "Mean PM2.5 by calendar month against the WHO guideline (top) and average yearly rainfall by month (bottom).")
para(f"Only June to September have a mean PM2.5 at or below 15 µg/m³ (Figure 4.4). July is lowest at {mm.pm[7]:.1f} µg/m³ and January "
     f"highest at {mm.pm[1]:.1f} µg/m³. The monthly mean is above the WHO guideline in {months_above} of the 12 months. May stands out: "
     f"it has heavy rain (about {mm.rain[5]:.0f} mm per year), yet its PM2.5 ({mm.pm[5]:.1f} µg/m³) stays above the guideline. Rainfall alone "
     "therefore does not explain the monthly pattern. Wind and the mixing of air, which also matter, are not in this dataset.")

h2("4.5", "Rainy Days and Dry Days")
figure("03_rain_vs_pm25.png", 9.5, "Distribution of daily PM2.5 on dry days and rainy days (rainy: 2.5 mm or more). Boxes show the interquartile range; the line is the median.")
rows = [["Dry days", f"{len(dry)}", f"{dry.pm25.median():.1f}", f"{dry.pm25.mean():.1f}", f"{dry.pm10.mean():.1f}", f"{dry.aqi_us.mean():.0f}", f"{dry.humidity_mean.mean():.0f}"],
        ["Rainy days", f"{len(rainy)}", f"{rainy.pm25.median():.1f}", f"{rainy.pm25.mean():.1f}", f"{rainy.pm10.mean():.1f}", f"{rainy.aqi_us.mean():.0f}", f"{rainy.humidity_mean.mean():.0f}"]]
table(("4.3", "Air quality on dry and rainy days"),
      ["Group", "Days", "PM2.5 median", "PM2.5 mean", "PM10 mean", "AQI mean", "Humidity (%)"], rows,
      [3.0, 1.6, 2.6, 2.4, 2.3, 2.0, 2.3], size=9.5, note="PM2.5 and PM10 in µg/m³.")
para(f"The median PM2.5 was {rainy.pm25.median():.1f} µg/m³ on rainy days and {dry.pm25.median():.1f} µg/m³ on dry days, so dry days ran "
     f"{dry.pm25.median() / rainy.pm25.median():.1f} times higher at the median (Figure 4.5, Table 4.3). Most rainy days lie below the WHO guideline, "
     f"and dry days spread much wider and reach higher values. A Mann-Whitney U test also finds a clear difference between the two groups "
     f"({sig}). The Spearman correlation between daily rainfall and PM2.5 is {mx(rho('rainfall_mm', 'pm25'))}, and the correlation with "
     f"the previous day's rainfall is {mx(df.pm25.corr(df.rainfall_mm.shift(1), method='spearman'))}. Rain goes with cleaner air here, "
     "but this is an association: rainy days also differ in humidity, cloud and wind in ways this dataset does not record.")

h2("4.6", "Air-Quality Categories by Season")
figure("05_aqi_category_by_season.png", 14.0, "Share of days in each US AQI category, by season.")
para(f"In the Monsoon, {good_mon:.0f} % of days ({good_mon_n} of {len(mon)}) were rated Good and none rose above Moderate (Figure 4.6). "
     f"In the other three seasons only {good_oth:.0f} % of days ({good_oth_n} of {len(oth)}) were rated Good. Moderate days made up 54 % to 74 % of those seasons, and "
     f"23 % to 30 % of days were rated Unhealthy for sensitive groups. Table 4.4 gives the day counts and Table 4.5 compares the days with the benchmarks.")
rows = [[s] + [int(cat_ct.loc[s].get(k, 0)) for k in ["Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy"]] + [int(cat_ct.loc[s].sum())] for s in SEAS]
table(("4.4", "Days in each AQI category, by season"),
      ["Season", "Good", "Moderate", "Unhealthy (sensitive)", "Unhealthy", "Total"], rows, [3.4, 2.0, 2.4, 3.8, 2.4, 2.0])
table(("4.5", "Days above air-quality benchmarks (1,096 days)"),
      ["Measure", "Days", "Share of days"],
      [["PM2.5 above WHO guideline (15 µg/m³)", who_days, f"{who_pct:.0f} %"],
       ["PM2.5 above CPCB limit (60 µg/m³)", cpcb_days, f"{cpcb_days / n * 100:.1f} %"],
       ["PM10 above WHO guideline (45 µg/m³)", pm10_who, f"{pm10_who / n * 100:.0f} %"],
       ["PM10 above CPCB limit (100 µg/m³)", pm10_cpcb, f"{pm10_cpcb / n * 100:.1f} %"],
       ["US AQI above 100", aqi100, f"{aqi100_pct:.0f} %"]],
      [8.0, 3.0, 3.6], ["l", "c", "c"])
para(f"PM2.5 passed the Indian limit on only {cpcb_days} days, but it passed the stricter WHO guideline on {who_pct:.0f} % of days. "
     f"All {aqi100} days with an AQI above 100 fell outside the monsoon.")

h2("4.7", "Relationships Between Variables")
figure("04_correlation.png", 12.0, "Spearman rank correlation between weather variables and pollutants (daily data, 1,096 days).")
rows = [["Rainfall and PM2.5", mx(rho("rainfall_mm", "pm25"))],
        ["Humidity and PM2.5", mx(rho("humidity_mean", "pm25"))],
        ["Humidity and ozone", mx(rho("humidity_mean", "ozone"))],
        ["Maximum temperature and ozone", mx(rho("temp_max", "ozone"))],
        ["Maximum temperature and humidity", mx(rho("temp_max", "humidity_mean"))],
        ["PM2.5 and PM10", mx(rho("pm25", "pm10"))],
        ["PM2.5 and NO₂", mx(rho("pm25", "no2"))]]
table(("4.6", "Selected Spearman correlations (ρ)"), ["Pair of variables", "ρ"], rows, [8.0, 3.0], ["l", "c"])
para(f"Humidity and rainfall run opposite to the particles (Figure 4.7). Humidity correlates with PM2.5 at {mx(rho('humidity_mean', 'pm25'))} and with ozone at "
     f"{mx(rho('humidity_mean', 'ozone'))}. Ozone rises with the daily maximum temperature (ρ = {mx(rho('temp_max', 'ozone'))}), and mean ozone is "
     f"{ozone['Summer']:.0f} µg/m³ in Summer against {ozone['Monsoon']:.0f} µg/m³ in the Monsoon. PM2.5 and PM10 move almost together "
     f"({mx(rho('pm25', 'pm10'))}), and PM2.5 closely tracks the AQI ({mx(rho('pm25', 'aqi_us'))}), because particles most often set the AQI. NO₂ is only "
     f"weakly related to humidity and rainfall ({mx(rho('humidity_mean', 'no2'))} and {mx(rho('rainfall_mm', 'no2'))}). All of these are correlations in observational "
     "data, so they do not show that one variable causes another.")

h2("4.8", "Main Findings")
bullets([f"Finding 1. The monsoon air was cleanest. {good_mon:.0f} % of June to September days were rated Good against {good_oth:.0f} % of other days. "
         f"Mean PM2.5 was {pm_mon_mean:.0f} µg/m³ in the Monsoon and {pm_oth_mean:.0f} µg/m³ in the rest of the year.",
         f"Finding 2. PM2.5 was lower on rainy days. The median was {rainy.pm25.median():.1f} µg/m³ on rainy days against {dry.pm25.median():.1f} µg/m³ on dry days "
         f"(Spearman ρ = {mx(rho('rainfall_mm', 'pm25'))} between rainfall and PM2.5; {sig}).",
         f"Finding 3. PM2.5 exceeded the WHO guideline on most days. It was above 15 µg/m³ on {who_days} of {n:,} days ({who_pct:.0f} %) and in {months_above} of 12 months, "
         f"but above the Indian limit of 60 µg/m³ on only {cpcb_days} days.",
         f"Finding 4. Days with a poor AQI fall in the dry months. All {aqi100} days ({aqi100_pct:.0f} %) with an AQI above 100 came between October and May.",
         f"Finding 5. The yearly cycle is stable. Mean PM2.5 was {yr.pm[2023]:.1f}, {yr.pm[2024]:.1f} and {yr.pm[2025]:.1f} µg/m³ in the three years, with the same "
         "seasonal shape each year."])
h2("4.9", "Recommendations")
bullets([f"Recommendation 1. Time health advisories to the dry months. All {aqi100} days with an AQI above 100 came between October and May, "
         "so advisories for sensitive groups (children, older adults and people with asthma) and the planning of outdoor events should focus on those months.",
         "Recommendation 2. Do not rely on rain to clean the air. The air meets the WHO guideline only in the monsoon months, so plans to cut emissions and dust "
         "should cover October to May. Data on likely sources (traffic, construction, burning) should be collected to decide where to act.",
         "Recommendation 3. Check the data against ground stations before using it for policy. The values here are modelled, so a comparison with CPCB monitor readings "
         "over five or more years should confirm the patterns before they guide decisions."])
h2("4.10", "Limitations of the Study")
bullets(["The data are modelled grid values for one point. They can differ from a single ground monitor and miss very local conditions.",
         "Only three years are covered, which is too short to separate seasonal variation from long-term trends.",
         "Correlations describe association only. Wind, traffic, industry and burning also affect air quality and are not in the dataset.",
         "Daily averages hide hourly peaks, such as rush-hour pollution, that matter for health."])

# ---- 5.0 CONCLUSION
h1("5.0", "CONCLUSION")
para(f"We analysed {n:,} days of public weather and air-quality data for Bengaluru (2023-2025). The weather followed a clear yearly cycle: "
     f"temperature peaked in {MN[int(mm.t.idxmax())]}, humidity was lowest in the dry months, and rain fell mostly from May to October. Air quality followed the "
     "seasons too. It was cleanest in the monsoon (June to September) and above the WHO PM2.5 guideline in the other eight months. PM2.5 was clearly lower on "
     f"rainy days (median {rainy.pm25.median():.1f} against {dry.pm25.median():.1f} µg/m³), and all {aqi100} days with a poor AQI fell outside the monsoon.")
para("We met all five objectives. We described the seasonal weather pattern, measured air quality by month and season, compared rainy and dry days, checked the "
     "values against WHO and CPCB benchmarks, and drew seven labelled charts. The findings are associations in observational, modelled "
     "data, and they do not show that rain makes the air cleaner. They do support the recommendations to time health advisories "
     "and plan emission control around the dry months.")

# ---- 6.0 FUTURE SCOPE
h1("6.0", "FUTURE SCOPE")
bullets(["Validate with ground stations. Compare the modelled values with CPCB monitor readings in Bengaluru to measure the difference.",
         "Extend the period and the places. Five to ten years of data from several cities would separate trends from the seasonal cycle.",
         "Add explanatory variables. Wind speed, boundary-layer height, traffic counts and fire activity could explain why May is rainy yet above the guideline.",
         "Use stronger models. Time-series or regression models can allow for the dependence between consecutive days, and can test whether rainfall adds explanatory power once season is controlled for.",
         "Look at hourly data. Hourly values would show daily cycles and rush-hour peaks that daily averages hide.",
         "Build an interactive dashboard. It could show the current day against the WHO and CPCB limits and the seasonal pattern."])

# ---- REFERENCES
reg.append((1, "", "REFERENCES"))
para("REFERENCES", 14, True, align="l", after=10, keep_next=True, break_before=True)
refs = ["Open-Meteo. Historical Weather API (ERA5). open-meteo.com/en/docs/historical-weather-api",
        "Open-Meteo. Air Quality API. open-meteo.com/en/docs/air-quality-api",
        "Zippenfenig, P. (2023). Open-Meteo.com Weather API [Computer software]. Zenodo. doi:10.5281/zenodo.7970649",
        "Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global reanalysis. //Quarterly Journal of the Royal Meteorological Society//, 146, 1999-2049.",
        "Copernicus Atmosphere Monitoring Service (CAMS), ECMWF. Global atmospheric composition forecasts. atmosphere.copernicus.eu",
        "World Health Organization (2021). //WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide//. Geneva: WHO.",
        "Central Pollution Control Board, India. National Ambient Air Quality Standards (NAAQS). cpcb.nic.in",
        "US Environmental Protection Agency. Air Quality Index (AQI) basics. airnow.gov/aqi/aqi-basics",
        "Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. //Annals of Mathematical Statistics//, 18(1), 50-60.",
        "Spearman, C. (1904). The proof and measurement of association between two things. //American Journal of Psychology//, 15(1), 72-101.",
        "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. //Computing in Science & Engineering//, 9(3), 90-95.",
        "McKinney, W. (2010). Data structures for statistical computing in Python. //Proceedings of the 9th Python in Science Conference//, 56-61.",
        "Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. //Nature//, 585, 357-362.",
        "Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. //Nature Methods//, 17, 261-272."]
for i, r in enumerate(refs, 1):
    p = para("", 12, align="j", after=5, spacing=1.15, indent=1.0)
    p.paragraph_format.first_line_indent = Cm(-1.0)
    rich(p, f"[{i}] " + r, markup=False)

# ---- APPENDICES
reg.append((1, "", "APPENDIX A: MONTHLY SUMMARY"))
para("APPENDIX A: MONTHLY SUMMARY", 14, True, align="l", after=10, keep_next=True, break_before=True)
rows = [[MN[m], f"{mm.t[m]:.1f}", f"{mm.tmax[m]:.1f}", f"{mm.tmin[m]:.1f}", f"{mm.h[m]:.0f}", f"{mm.rain[m]:.0f}", f"{mm.pm[m]:.1f}", f"{mm.aqi[m]:.0f}"]
        for m in range(1, 13)]
table(("A.1", "Monthly means over 2023-2025 (rainfall is the average yearly total for the month)"),
      ["Month", "Temp mean (°C)", "Temp max (°C)", "Temp min (°C)", "Humidity (%)", "Rain (mm)", "PM2.5 (µg/m³)", "AQI"], rows,
      [2.6, 1.9, 1.9, 1.9, 1.9, 1.7, 2.1, 1.3], size=9.5)

reg.append((1, "", "APPENDIX B: PROJECT FILES AND SOURCE CODE"))
para("APPENDIX B: PROJECT FILES AND SOURCE CODE", 14, True, align="l", after=10, keep_next=True, before=14)
table(("B.1", "Files submitted with this report"),
      ["File", "Content"],
      [["data/bengaluru_daily_2023_2025.csv", "Daily dataset (10 columns, 1,096 rows)"],
       ["data/bengaluru_daily_clean.csv", "Dataset with derived columns (season, AQI category, rainy-day flag)"],
       ["data/raw/weather.json, aq.json", "Hourly data exactly as returned by the APIs"],
       ["data/DATA_DICTIONARY.md", "Source, period, attribute meanings, quality checks"],
       ["Bengaluru_Weather_AQ_Visualization.ipynb", "Google Colab notebook: download, preparation, analysis and all charts"],
       ["scripts/build_daily.py, analyse.py, make_figures.py", "Python scripts for aggregation, analysis and the figures in this report"],
       ["poster/", "Poster (PDF) and its source files"]],
      [7.2, 8.8], ["l", "l"], size=9.5)
para("Core of the data-preparation step (hourly values to daily values):", 11, align="l", before=4, after=4, spacing=1.0)
code = ('daily_w = weather.groupby("date").agg(\n'
        '    temp_mean=("temperature_2m", "mean"), temp_max=("temperature_2m", "max"),\n'
        '    temp_min=("temperature_2m", "min"), humidity_mean=("relative_humidity_2m", "mean"),\n'
        '    rainfall_mm=("precipitation", "sum"))\n'
        'daily_a = air.groupby("date").agg(\n'
        '    pm25=("pm2_5", "mean"), pm10=("pm10", "mean"), no2=("nitrogen_dioxide", "mean"),\n'
        '    ozone=("ozone", "mean"), aqi_us=("us_aqi", "mean"))\n'
        'df = daily_w.join(daily_a, how="outer").round(2)\n'
        'assert df.isna().sum().sum() == 0\n'
        'df["rainy"] = df.rainfall_mm >= 2.5')
for line in code.split("\n"):
    p = para("", 9, align="l", after=0, spacing=1.0, indent=0.5)
    run(p, line, 9, font="Courier New")


# ================================================================== TOC TABLE + LIST OF FIGURES
def toc_table(anchor, rows, widths):
    t = doc.add_table(rows=0, cols=3)
    for lvl, a, b, c3 in rows:
        cells = t.add_row().cells
        for cell, txt in zip(cells, (a, b, c3)):
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1 if lvl == 2 else 2)
            p.paragraph_format.space_before = Pt(0 if lvl == 2 else 2)
            p.paragraph_format.line_spacing = 1.0
            if cell is cells[2]:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run(p, txt, 12 if lvl == 1 else 11.5, lvl == 1)
    fix_widths(t, widths)
    anchor._p.addnext(t._tbl)


pg = lambda key: str(pages.get(key, "0"))
toc_rows = [(1, "", "TITLE", ""),
            (1, "", "LIST OF FIGURES", pg("LIST OF FIGURES")),
            (1, "", "LIST OF SYMBOLS AND ABBREVIATIONS", pg("LIST OF SYMBOLS AND ABBREVIATIONS"))]
for lvl, num, title in reg:
    toc_rows.append((lvl, num, title.upper() if lvl == 1 else title, pg(f"{num} {title}".strip())))
toc_table(toc_anchor, toc_rows, [1.6, 12.2, 2.2])
short_caps = ["Monthly temperature, humidity and rainfall", "Calendar heatmap of daily AQI", "Daily PM2.5 and 30-day average",
              "Mean PM2.5 by month and average yearly rainfall", "PM2.5 on dry and rainy days", "AQI categories by season",
              "Spearman correlation heatmap"]
assert len(short_caps) == len(figs)
toc_table(lof_anchor, [(2, f"Figure 4.{i}", sc, pg(f"Figure 4.{i}:")) for i, sc in enumerate(short_caps, 1)], [2.6, 11.2, 2.2])

# ================================================================== SECTIONS: footers and numbering
footer_number(sec2); set_pgnum(sec2, "lowerRoman", 1)
footer_number(sec3); set_pgnum(sec3, "decimal", 1)
doc.core_properties.title = TITLE
doc.core_properties.author = "; ".join(a for a, _ in MEMBERS)
doc.core_properties.subject = f"{CODE} {COURSE}"
os.makedirs(f"{root}/report", exist_ok=True)
doc.save(OUT)
json.dump({"reg": reg, "figs": [n for n, _ in figs]}, open(f"{root}/report/_registry_v2.json", "w"))
print("saved", OUT, "| sections", len(doc.sections), "| figures", len(figs))
