"""
Step 3 - AI integration (Claude API).

Two features on top of the SQL database:
  1. ask      - natural-language question -> safe, read-only SQL -> result -> plain-English answer
  2. briefing - turns the SQL/trend outputs into a short stakeholder briefing (ai_briefing.md)

Setup:   pip install anthropic pandas
         export ANTHROPIC_API_KEY="your-key"      (Windows: set ANTHROPIC_API_KEY=your-key)
Run:     python ai_insights.py ask "Which decade had the most deficient monsoon years?"
         python ai_insights.py briefing
"""
import os
import re
import sqlite3
import sys
from pathlib import Path

import anthropic
import pandas as pd

MODEL = "claude-sonnet-5-5"   # change here if you want a different Claude model
DB_PATH = "climate.db"
EXPORT_DIR = Path("tableau_exports")

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum)\b", re.I)


def get_schema() -> str:
    """Describe tables and columns so the model writes valid SQL."""
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as con:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        lines = []
        for t in tables:
            cols = [f"{c[1]} ({c[2]})" for c in con.execute(f"PRAGMA table_info({t})")]
            lines.append(f"{t}: " + ", ".join(cols))
    return "\n".join(lines)


def is_safe_select(sql: str) -> bool:
    """Allow only a single read-only SELECT / WITH statement."""
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        return False
    if not re.match(r"^(select|with)\b", s, re.I):
        return False
    return not FORBIDDEN.search(s)


def _text(resp) -> str:
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def question_to_sql(question: str) -> str:
    system = (
        "You write SQLite queries for an India climate database (1901-2015, national level).\n"
        f"Schema:\n{get_schema()}\n\n"
        "Rules: return ONE read-only SELECT query and nothing else - no prose, no markdown fences. "
        "Temperatures are in deg C, rainfall in mm. SQLite has no STDDEV; use "
        "SQRT(AVG(x*x) - AVG(x)*AVG(x)) if you need a standard deviation. "
        "If the question cannot be answered from this schema, return exactly: UNANSWERABLE"
    )
    resp = client.messages.create(
        model=MODEL, max_tokens=500, system=system,
        messages=[{"role": "user", "content": question}])
    sql = re.sub(r"^```(?:sql)?|```$", "", _text(resp), flags=re.M).strip()
    return sql


def ask(question: str) -> None:
    sql = question_to_sql(question)
    if sql == "UNANSWERABLE":
        print("This dataset can't answer that (it only has national-level temperature and rainfall, 1901-2015).")
        return
    if not is_safe_select(sql):
        print("Blocked: the generated query was not a single read-only SELECT.\n", sql)
        return

    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as con:   # read-only connection
        try:
            df = pd.read_sql_query(sql, con)
        except Exception as e:  # bad SQL from the model
            print("Query failed:", e, "\n", sql)
            return

    resp = client.messages.create(
        model=MODEL, max_tokens=400,
        system=("You are a data analyst answering a stakeholder. Use ONLY the result table given. "
                "Answer in 2-4 sentences, include the key numbers, and note any caveat "
                "(e.g. national-level data, partial decades) if relevant. Do not speculate on causes."),
        messages=[{"role": "user", "content":
                   f"Question: {question}\n\nSQL used:\n{sql}\n\nResult:\n{df.head(40).to_string(index=False)}"}])
    print("SQL:\n", sql, "\n")
    print("Answer:", _text(resp))


def briefing() -> None:
    parts = []
    for f in ["trend_summary", "q1_decade_change", "q2_monthly_warming",
              "q5_monsoon_by_decade", "q6_deficient_monsoon_years"]:
        parts.append(f"## {f}\n" + pd.read_csv(EXPORT_DIR / f"{f}.csv").to_string(index=False))
    resp = client.messages.create(
        model=MODEL, max_tokens=900,
        system=("You are a data analyst writing a one-page briefing for a non-technical stakeholder "
                "(agriculture / water planning). Use ONLY the tables provided; do not invent numbers "
                "or causes. Structure: 3 key findings, 1 caveat paragraph (national-level data, "
                "partial first/last decades, R-squared values), 2 suggested next analyses. "
                "State clearly where there is NO significant trend."),
        messages=[{"role": "user", "content": "\n\n".join(parts)}])
    Path("ai_briefing.md").write_text(_text(resp))
    print("Saved ai_briefing.md")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "ask":
        ask(" ".join(sys.argv[2:]))
    elif len(sys.argv) >= 2 and sys.argv[1] == "briefing":
        briefing()
    else:
        print(__doc__)
