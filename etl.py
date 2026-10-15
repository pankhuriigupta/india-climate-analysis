"""
Step 1 - ETL: clean the raw IMD-style temperature and rainfall files,
load them into a SQLite database, and export Tableau-ready CSVs.

Run:  python etl.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

RAIN_FILE = "rainfall_area-wt_India_1901-2015.csv.xlsx"
TEMP_FILE = "temperatures.csv.xlsx"
DB_PATH = "climate.db"
OUT_DIR = Path("tableau_exports")

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.drop(columns=[c for c in ["REGION"] if c in df.columns])
    df = df.drop_duplicates(subset="YEAR").sort_values("YEAR")
    value_cols = [c for c in df.columns if c != "YEAR"]
    df[value_cols] = df[value_cols].apply(pd.to_numeric, errors="coerce")
    return df.reset_index(drop=True)


def main() -> None:
    rain = load_and_clean(RAIN_FILE)
    temp = load_and_clean(TEMP_FILE)

    # --- data quality checks (worth mentioning in the README) -------------
    print(f"Rain rows: {len(rain)}  ({rain.YEAR.min()}-{rain.YEAR.max()})")
    print(f"Temp rows: {len(temp)}  ({temp.YEAR.min()}-{temp.YEAR.max()})")
    print("Nulls  rain/temp:", int(rain.isna().sum().sum()), "/", int(temp.isna().sum().sum()))
    gap = (rain[MONTHS].sum(axis=1) - rain["ANNUAL"]).abs()
    print(f"Rain: max |sum(months) - annual| = {gap.max():.1f} mm")

    # Only 1901-2015 exists in BOTH files, so analysis uses the overlap.
    annual = temp.merge(rain, on="YEAR", suffixes=("_TEMP", "_RAIN"), how="inner")
    annual = annual.rename(columns={
        "YEAR": "year",
        "ANNUAL_TEMP": "temp_annual_c", "ANNUAL_RAIN": "rain_annual_mm",
        "JUN-SEP_TEMP": "temp_jjas_c", "JUN-SEP_RAIN": "rain_jjas_mm",
        "JAN-FEB_TEMP": "temp_janfeb_c", "JAN-FEB_RAIN": "rain_janfeb_mm",
        "MAR-MAY_TEMP": "temp_marmay_c", "MAR-MAY_RAIN": "rain_marmay_mm",
        "OCT-DEC_TEMP": "temp_octdec_c", "OCT-DEC_RAIN": "rain_octdec_mm",
    })
    annual = annual[["year", "temp_annual_c", "rain_annual_mm",
                     "temp_janfeb_c", "temp_marmay_c", "temp_jjas_c", "temp_octdec_c",
                     "rain_janfeb_mm", "rain_marmay_mm", "rain_jjas_mm", "rain_octdec_mm"]]
    annual["decade"] = (annual["year"] // 10) * 10

    # Long/tidy monthly table: one row per year-month (best shape for Tableau)
    t_long = temp.melt(id_vars="YEAR", value_vars=MONTHS, var_name="month", value_name="temp_c")
    r_long = rain.melt(id_vars="YEAR", value_vars=MONTHS, var_name="month", value_name="rain_mm")
    monthly = t_long.merge(r_long, on=["YEAR", "month"], how="inner").rename(columns={"YEAR": "year"})
    monthly["month_num"] = monthly["month"].map({m: i + 1 for i, m in enumerate(MONTHS)})
    monthly["decade"] = (monthly["year"] // 10) * 10
    monthly = monthly.sort_values(["year", "month_num"]).reset_index(drop=True)

    # --- load to SQLite ----------------------------------------------------
    Path(DB_PATH).unlink(missing_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        annual.to_sql("climate_annual", con, index=False)
        monthly.to_sql("climate_monthly", con, index=False)
        con.execute("CREATE INDEX idx_annual_year ON climate_annual(year)")
        con.execute("CREATE INDEX idx_monthly_year ON climate_monthly(year, month_num)")

    OUT_DIR.mkdir(exist_ok=True)
    annual.to_csv(OUT_DIR / "climate_annual.csv", index=False)
    monthly.to_csv(OUT_DIR / "climate_monthly.csv", index=False)
    print(f"Loaded {len(annual)} annual rows and {len(monthly)} monthly rows into {DB_PATH}")


if __name__ == "__main__":
    main()
