# People Analytics & Behavioral Data Portfolio

**Nwafor Martins** — People Analytics Engineer | Psychology background | Python, SQL, Power BI

[Live site](https://martins-portfolio.net/) · (coming soon)


[Email](mailto:nwaforchubby@gmail.com) · [WhatsApp](https://wa.me/2349135615687)

---

## About

I build data pipelines that explain *why* people leave, stall, or convert — not just that they did. My background is in psychology, and I use that lens on the data itself: survey scores and behavioral logs as measures of how people actually experience something, not just columns to average.

This repo holds the three case studies behind my portfolio site. Each one starts from a single behavioral hypothesis, walks through a messy synthetic dataset, and ends in a dashboard or app a non-technical stakeholder could use without me in the room. All companies and data are fictional, built with Python's Faker library to mimic the mess of a real export — duplicates, inconsistent formatting, missing values and all.

## Case studies

### 1. People Analytics — `project-1-people-analytics/` · `app_meridian.py`
**Why employees at Meridian Works leave.**
A full Ask → Prepare → Analyze → Share → Act workflow on employee attrition and engagement data. Treats satisfaction, involvement and work-life balance as psychological constructs rather than raw scores, and traces attrition down to specific roles and tenure points.
`17.4%` attrition traced to specific roles and tenure windows.
**Stack:** Psychology · Excel · SQL · Python · Power BI · Streamlit

### 2. Customer Analytics — `project-2-behavioral-churn/` · `app_solmere.py`
**Whether one bad moment predicts cancellation better than average satisfaction does.**
Tests Kahneman's peak-end rule against 8,400 synthetic subscribers of a fictional D2C subscription business, Solmere. Rebuilds a flat export into relational tables, engineers a "days since last negative support ticket" field, and correlates it with renewal outcomes. Includes a Streamlit app that lets you explore the sentiment-churn relationship interactively rather than off a fixed chart.
`41%` cancellation rate following a negative peak moment before renewal, vs. `9%` without one.
**Stack:** Psychology · Python · SQL · Power BI · Streamlit · Behavioral Economics

### 3. Digital Product UX — `project-3-funnel-testing/` · `app_tallywell.py`
**Whether a broken onboarding funnel was a motivation problem or a friction problem.**
Applies BJ Fogg's behavior model to an A/B test on a fictional finance app's signup form — a 12-field control against a 4-field variant using progressive profiling. ~40,000 synthetic sessions, funnel built step-by-step in SQL, field-level drop-off isolated to separate an ability problem from a motivation problem.
`+51%` signup lift from cutting form friction, tested against a parallel copy-only change.
**Stack:** Psychology · Python · SQL · A/B Testing · Data Visualization

## Repo structure

```
portfolio-data/
├── project-1-people-analytics/   # Meridian Works — attrition & engagement
├── project-2-behavioral-churn/   # Solmere — subscription churn
├── project-3-funnel-testing/     # Tallywell — onboarding A/B test
├── app_meridian.py                # Streamlit app for case study 1
├── app_solmere.py                 # Streamlit app for case study 2
├── app_tallywell.py                # Streamlit app for case study 3
├── requirements.txt
└── README.md
```

Each project folder contains the pipeline for that case study: synthetic data generation, the SQL used to clean and restructure it, and the analysis behind the dashboard.

## Running locally

```bash
git clone https://github.com/professorpasqua-byte/portfolio-data.git
cd portfolio-data
pip install -r requirements.txt
streamlit run app_solmere.py   # or app_meridian.py / app_tallywell.py
```

## Why synthetic data

None of the three datasets are downloaded from an existing source. Each one is generated to carry the kind of noise a real export has — duplicate rows, inconsistent free text, mixed currency formats, missing values where a field genuinely wasn't collected — so the cleaning and modeling work reflects what an analyst actually deals with on the job, not a dataset that's already been handed over clean.

## Beyond the data

I also work in strategic organizational consulting — culture diagnostics and change management using frameworks like Schein's culture model and the Job Demands-Resources model. Details on the [portfolio site](https://martins-portfolio.net/#consulting). (coming soon)

## Contact

Open to global remote opportunities (GMT+1).

- Email: [nwaforchubby@gmail.com](mailto:nwaforchubby@gmail.com)
- WhatsApp: [+234 913 561 5687](https://wa.me/2349135615687)
- Portfolio: [martins-portfolio.net](https://martins-portfolio.net/)



---

## License

© 2026 Nwafor Martins. All rights reserved.
This repository is shared for portfolio and demonstration purposes only.
