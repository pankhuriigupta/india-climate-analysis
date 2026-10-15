# India Climate Analytics: End-to-End Pipeline (1901–2015)

An end-to-end analytics project on 115 years of India's national temperature and rainfall data: Python for cleaning, SQL for the analysis, a light regression model for trends, and an interactive dashboard for the results.

**Business question:** How has India's climate shifted over a century, and what does it mean for agriculture and water planning?

## Key findings

| Finding | Evidence |
|---|---|
| Warming is real and has accelerated | Linear trend of **+0.12 °C/decade** (1901–2015, R² = 0.70). Slope was **+0.06 °C/decade** in 1901–1950 (weak fit, R² = 0.11) vs **+0.19 °C/decade** in 1976–2015, roughly 3x faster |
| Winter and spring warmed most; monsoon months least | Feb +1.67 °C, Mar +1.37 °C, Dec +1.24 °C vs Jun +0.50 °C, Jul +0.60 °C (1991–2015 vs 1901–1950) |
| 9 of the 10 hottest years are after 1995 | Top year: 2009 (+1.53 °C above the 1901–1950 baseline) |
| **No significant long-term rainfall trend** | Annual rain slope ≈ −3 mm/decade, R² < 0.01. Monsoon share of annual rain stays ~75% |
| Monsoon variability matters more than the average | Deficient-monsoon years (> 1 std below mean): most in the 1900s (5 of 9 yrs) and 1910s (4 of 10); the 2000s had 3 of 10 after a quiet 1990s (0) |

**Conclusion:** the planning risk is cold-season heat plus year-to-year monsoon swings, not a falling rainfall average.

## Pipeline

```
Raw Excel files ──► etl.py ──► SQLite (climate.db) ──► queries.sql + analyze.py ──► CSV exports ──► Dashboard
 (temp + rainfall)  clean,       2 tables               6 SQL analyses +              tableau_exports/
                    validate,                           linear-regression trend
                    reshape
```

| Step | Tool | What it does |
|---|---|---|
| 1. Clean and load | Python (pandas) | Validates nulls, duplicates and month-vs-annual consistency (max gap 0.3 mm); reshapes monthly data to long format; loads SQLite |
| 2. Analyze | SQL (SQLite) | Window functions (`LAG`, `RANK`, rolling `AVG OVER`), baseline-vs-recent comparison, CTEs, monsoon variability, deficient-year counts |
| 3. Model | scikit-learn | Linear regression of temperature and rainfall on year; slope per decade and R² for three periods |
| 4. Visualize | Interactive dashboard (HTML, Chart.js) | Trend, monthly warming, rainfall and monsoon charts with insights (`climate-dashboard.html`) |

## Run it

```bash
pip install pandas openpyxl scikit-learn
python etl.py          # builds climate.db + tableau_exports/climate_*.csv
python analyze.py      # runs queries.sql, fits trends, exports result CSVs
```

The original exploratory notebook (`temp_rain.ipynb`) is kept for reference.

## Limitations

- **National-level data only.** No state or regional breakdown, so regional conclusions aren't possible.
- **Overlap period is 1901–2015.** Temperature runs to 2017, rainfall only to 2015.
- Decades 1900 (9 years) and 2010 (6 years) are partial.
- Linear trends are a simple summary, not a causal model. The rainfall result is "no detectable trend," not "no change."

## Dashboard

[Add your dashboard link here]

## Author

**Pankhuri**, B.Tech CSE (Data Science), SRM Institute of Science and Technology
[Add LinkedIn link]
