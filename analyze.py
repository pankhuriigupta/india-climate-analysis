"""
Step 2 - Run the SQL analysis, fit a light trend model, export results for Tableau.

Run:  python analyze.py      (after etl.py)
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression

DB_PATH = "climate.db"
OUT_DIR = Path("tableau_exports")
OUT_DIR.mkdir(exist_ok=True)

QUERY_NAMES = {
    1: "q1_decade_change",
    2: "q2_monthly_warming",
    3: "q3_hottest_years",
    4: "q4_rolling_avg",
    5: "q5_monsoon_by_decade",
    6: "q6_deficient_monsoon_years",
}


def split_queries(sql_text: str) -> dict[int, str]:
    """Split queries.sql on its '-- Qn.' headers."""
    parts = re.split(r"^-- Q(\d+)\.", sql_text, flags=re.M)
    return {int(parts[i]): parts[i + 1].split("\n", 1)[1].strip()
            for i in range(1, len(parts), 2)}


def trend_per_decade(df: pd.DataFrame, col: str, start: int, end: int) -> dict:
    """Simple linear regression of `col` on year; slope reported per decade."""
    sub = df[(df.year >= start) & (df.year <= end)]
    X, y = sub[["year"]], sub[col]
    model = LinearRegression().fit(X, y)
    return {"metric": col, "period": f"{start}-{end}",
            "slope_per_decade": round(model.coef_[0] * 10, 3),
            "r_squared": round(model.score(X, y), 3)}


def main() -> None:
    queries = split_queries(Path("queries.sql").read_text())
    with sqlite3.connect(DB_PATH) as con:
        for n, sql in queries.items():
            res = pd.read_sql_query(sql, con)
            res.to_csv(OUT_DIR / f"{QUERY_NAMES[n]}.csv", index=False)
            print(f"\n--- Q{n}: {QUERY_NAMES[n]} ---")
            print(res.head(12).to_string(index=False))

        annual = pd.read_sql_query("SELECT * FROM climate_annual", con)
        trends = pd.DataFrame(
            [trend_per_decade(annual, "temp_annual_c", 1901, 2015),
             trend_per_decade(annual, "temp_annual_c", 1901, 1950),
             trend_per_decade(annual, "temp_annual_c", 1976, 2015),
             trend_per_decade(annual, "rain_annual_mm", 1901, 2015),
             trend_per_decade(annual, "rain_jjas_mm", 1901, 2015)])
        trends.to_sql("trend_summary", con, index=False, if_exists="replace")
        trends.to_csv(OUT_DIR / "trend_summary.csv", index=False)
        print("\n--- Trend model (linear regression, slope per decade) ---")
        print(trends.to_string(index=False))


if __name__ == "__main__":
    main()
