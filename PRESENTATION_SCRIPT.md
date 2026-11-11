# Poster Presentation Script

Poster: `poster/Bengaluru_Weather_Air_Quality_Poster.pdf`
Total talk time: about 7 minutes. Each member speaks for about 1.3 to 1.5 minutes.

The split follows the poster from left to right, so the audience never has to hunt for where you are. The speaking order matches the order the names appear on the poster. You can swap parts between members, but then swap the handover lines too.

## Timing plan

| # | Speaker | Poster sections | Spoken words | Time at a calm pace (about 135 words a minute) |
|---|---|---|---|---|
| 1 | Hiranamyi Kiran Gudekota | Title, 01 Problem, 02 Objectives | 166 | 1 min 14 s |
| 2 | Neharika Anantha Gowda | 03 Data source, 04 Dataset, 05 Cleaning | 196 | 1 min 27 s |
| 3 | Niharika K P | Fig 1 Calendar, Fig 2 Climate, Fig 4 PM2.5 by month | 173 | 1 min 17 s |
| 4 | Sai Yasasvi Kancharla | Fig 5 Dry vs rainy days, Fig 3 AQI categories | 184 | 1 min 22 s |
| 5 | Sonali Ayyappa | 06 Findings, 08 Recommendations, 07 Conclusion | 200 | 1 min 29 s |

Text in `[brackets]` is an action, not something to say. Point at the part of the poster you are talking about.

---

## Part 1. Hiranamyi Kiran Gudekota: opening, problem, objectives

*Stand beside the title. Greet the audience.*

Good morning, everyone. We are Hiranamyi, Neharika, Niharika, Sai and Sonali, and our project is "Weather and Air Quality in Bengaluru, 2023 to 2025". [Point to the title.]

Our question is simple. Bengaluru has hot dry spells and a heavy monsoon, and the fine dust in the air, called PM2.5, was above the World Health Organization guideline on 62 percent of days. [Point to section 01.] So we asked three things. How do temperature, humidity and rainfall change through the year? How does air quality change alongside them? And when is the air worst?

[Point to section 02.] We set four objectives. First, describe the seasonal weather pattern. Second, measure how air quality changes by month and by season. Third, compare air quality on rainy days and dry days. And fourth, check the numbers against the WHO guideline and the Indian CPCB limit.

One thing to say clearly before we go on. We did not collect this data ourselves. It is public data, and Neharika will now explain where it came from and how we prepared it.

*Handover: look at Neharika.*

---

## Part 2. Neharika Anantha Gowda: data source, dataset, cleaning

Thank you. [Point to section 03.] Our data comes from Open-Meteo, a free public service. The weather comes from its Historical Weather API, which is built on ERA5, and the air quality comes from its Air Quality API, which is built on the CAMS model. We took Bengaluru, from 1 January 2023 to 31 December 2025, and downloaded every hourly value on 11 November 2026.

One limit to remember. These are modelled values for a grid cell. They are not readings from a monitor on a street.

[Point to section 04.] We combined the hourly values into one row per day. That gives 1,096 daily records and 10 attributes: temperature, humidity, rainfall, four pollutants and the US air quality index. Rainfall is a daily total, and most of the rest are averages. We also added a season, an air quality category, and a rainy-day flag, where a rainy day means 2.5 millimetres of rain or more.

[Point to section 05.] Then we checked the data. Out of 10,960 cells, none were missing. There were no duplicate dates and no impossible values. We kept the outliers, such as 39.5 degrees on 1 May 2024, because they are real weather.

Niharika will show you what the data says.

*Handover: look at Niharika K P.*

---

## Part 3. Niharika K P: the seasonal pattern (Fig 1, Fig 2, Fig 4)

Thank you. Let me show you the yearly pattern. [Point to Fig 1.] This calendar has one square for each day, and darker blue means worse air. Look at June to September: a pale band appears in every year. That is the monsoon. Darker squares fill January to May and October to December. The worst day was 2 May 2025, with an AQI of 156.

[Point to Fig 2.] Now the weather. Temperature peaks in April at 27.7 degrees and is lowest in January at 21.1. Humidity is lowest in March, at 47 percent, and highest in July, at 82 percent. Rain falls mostly between May and October.

[Point to Fig 4.] Here is PM2.5 by month. Orange bars are above the WHO guideline of 15 micrograms per cubic metre. Only June to September are at or below it. July is the cleanest month at 5.2, and January the dirtiest at 30.5.

One point to notice. May has heavy rain, but its PM2.5 is still above the guideline. So rain alone does not explain the pattern.

Sai will now compare rainy days and dry days.

*Handover: look at Sai.*

---

## Part 4. Sai Yasasvi Kancharla: rainy days against dry days (Fig 5, Fig 3)

Thank you. [Point to Fig 5.] This box plot compares PM2.5 on dry days and on rainy days. The line inside each box is the median. On the 803 dry days, the median is 23.7. On the 293 rainy days, it is 9.0. So dry days run about 2.6 times higher, and they spread much wider. A statistical test, called the Mann-Whitney test, shows the difference is large.

Now, a careful point. This does not prove that rain cleans the air. Rainy days also differ in humidity, cloud and wind, and we have no wind data. So we say PM2.5 is lower on rainy days. We do not say that rain causes it.

[Point to Fig 3.] Finally, the air quality categories by season. In the monsoon, 64 percent of days were rated Good, and none was above Moderate. In the other seasons, most days were Moderate, and between 23 and 30 percent were unhealthy for sensitive groups.

We also measured how the variables move together, using a rank correlation. Humidity and rainfall both move opposite to PM2.5, at minus 0.61 and minus 0.58.

Sonali will give you our findings and recommendations.

*Handover: look at Sonali.*

---

## Part 5. Sonali Ayyappa: findings, recommendations, conclusion

Thank you. [Point to section 06.] We have four main findings. One: the monsoon air was cleanest. 64 percent of monsoon days were rated Good, against 6 percent of the other days. Two: PM2.5 was lower on rainy days, with a median of 9.0 against 23.7. Three: PM2.5 was above the WHO guideline on 62 percent of days, 675 of 1,096, and in 8 of the 12 months. It passed the Indian limit of 60 on only 2 days. Four: all 199 days with an AQI above 100 fell outside the monsoon.

[Point to section 08.] From this we recommend three things. First, time health advisories for sensitive groups to the dry months, October to May. Second, do not wait for rain to clean the air. Plan emission and dust control for those months, and collect data on traffic, construction and burning. Third, check our modelled data against ground-station readings before using it for policy.

[Point to section 07.] To conclude, Bengaluru's air quality follows the seasons. It is cleanest in the monsoon and above the WHO guideline in the other eight months. These are associations in modelled data, so the next step is to check them against station data over more years.

Thank you. We are happy to take questions.

*Stand together for questions.*

---

## If you have less time

Faculty may give you less than seven minutes. Cut these sentences first, in this order. Nothing else needs to change.

| Part | Cut |
|---|---|
| 4 | The paragraph about rank correlation (humidity and rainfall at minus 0.61 and minus 0.58) |
| 3 | The sentence about the weather in Fig 2 (temperature and humidity figures), keeping only "rain falls mostly from May to October" |
| 2 | The sentence about derived columns (season, category, rainy-day flag) |
| 1 | The sentence listing the four objectives, replaced by "our objectives are on the poster" |

Never cut: the sentence that the data was not collected by the group, the "modelled, not measured" limit, and "we do not say that rain causes it".

---

## Who answers which question

Anyone may add to an answer, but start with the owner. The model answers are in `LEARNING_GUIDE.md`, Part 10.

| Question is about | First answer from |
|---|---|
| Why this topic, what the problem and objectives are | Hiranamyi |
| Data source, ERA5 and CAMS, how hourly became daily, cleaning, outliers, the notebook | Neharika |
| The seasonal patterns, the calendar, monthly PM2.5, why May is an exception | Niharika |
| Statistics: median, correlation, the Mann-Whitney test, causation | Sai |
| Findings, recommendations, limits, future scope | Sonali |

If someone is unsure, say "that is covered in our report in chapter 4, and my teammate can add to it", then hand over. Do not guess.

---

## Rehearsal checklist

- [ ] Each person reads their part aloud twice, then says it again without looking, using the poster as a prompt.
- [ ] Time each part with a phone. Aim for 1 minute 15 seconds to 1 minute 30 seconds. If you run over, cut sentences from the table above.
- [ ] Practise the handover lines exactly. A clean handover makes the group look prepared.
- [ ] Do one full run-through together, in order, standing in front of the poster PDF on a screen.
- [ ] Practise pointing. Point at the part you mention before you start talking about it.
- [ ] Put the poster PDF and the Colab notebook open on a laptop in case you are asked to show the code.

## Delivery tips

- Speak slowly. The scripts are written to sound natural out loud, so pause at full stops.
- Do not read the poster word for word. Look at the audience, glance at the poster when you point.
- Say numbers clearly: "twenty-three point seven", not "twenty-three seven".
- Change any wording that does not sound like you. The facts and numbers must stay the same. The sentences should sound like your own speech.
- Four phrases to keep exactly: "we did not collect this data ourselves", "modelled values, not readings from a monitor", "PM2.5 is lower on rainy days", and "we do not say that rain causes it".
