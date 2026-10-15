-- ============================================================
-- India Climate Analytics: SQL analysis (SQLite)
-- Tables: climate_annual(year, temp_annual_c, rain_annual_mm, ..., decade)
--         climate_monthly(year, month, month_num, temp_c, rain_mm, decade)
-- ============================================================

-- Q1. Decade-over-decade change in temperature and rainfall
WITH d AS (
    SELECT decade,
           ROUND(AVG(temp_annual_c), 2)  AS avg_temp_c,
           ROUND(AVG(rain_annual_mm), 0) AS avg_rain_mm
    FROM climate_annual
    GROUP BY decade
)
SELECT decade, avg_temp_c, avg_rain_mm,
       ROUND(avg_temp_c  - LAG(avg_temp_c)  OVER (ORDER BY decade), 2) AS temp_change_vs_prev,
       ROUND(avg_rain_mm - LAG(avg_rain_mm) OVER (ORDER BY decade), 0) AS rain_change_vs_prev
FROM d
ORDER BY decade;

-- Q2. Which months warmed the most? Early baseline vs recent period
SELECT month, month_num,
       ROUND(AVG(CASE WHEN year BETWEEN 1901 AND 1950 THEN temp_c END), 2) AS base_temp,
       ROUND(AVG(CASE WHEN year BETWEEN 1991 AND 2015 THEN temp_c END), 2) AS recent_temp,
       ROUND(AVG(CASE WHEN year BETWEEN 1991 AND 2015 THEN temp_c END)
           - AVG(CASE WHEN year BETWEEN 1901 AND 1950 THEN temp_c END), 2) AS warming_c,
       ROUND(AVG(CASE WHEN year BETWEEN 1991 AND 2015 THEN rain_mm END)
           - AVG(CASE WHEN year BETWEEN 1901 AND 1950 THEN rain_mm END), 1) AS rain_change_mm
FROM climate_monthly
GROUP BY month, month_num
ORDER BY warming_c DESC;

-- Q3. Ten hottest years, with deviation from the 1901-1950 baseline
WITH base AS (
    SELECT AVG(temp_annual_c) AS base_temp
    FROM climate_annual WHERE year BETWEEN 1901 AND 1950
)
SELECT RANK() OVER (ORDER BY temp_annual_c DESC) AS hot_rank,
       year, temp_annual_c,
       ROUND(temp_annual_c - base_temp, 2) AS anomaly_c
FROM climate_annual, base
ORDER BY hot_rank
LIMIT 10;

-- Q4. Rolling 10-year average temperature (smooths year-to-year noise)
SELECT year, temp_annual_c,
       ROUND(AVG(temp_annual_c) OVER (ORDER BY year ROWS BETWEEN 9 PRECEDING AND CURRENT ROW), 2) AS temp_10yr_avg,
       ROUND(AVG(rain_annual_mm) OVER (ORDER BY year ROWS BETWEEN 9 PRECEDING AND CURRENT ROW), 0) AS rain_10yr_avg
FROM climate_annual
ORDER BY year;

-- Q5. Monsoon (Jun-Sep) dependence and variability by decade
--     (SQLite has no STDDEV, so variance = E[x^2] - E[x]^2)
SELECT decade,
       ROUND(AVG(rain_jjas_mm), 0)                                  AS avg_monsoon_mm,
       ROUND(100.0 * AVG(rain_jjas_mm / rain_annual_mm), 1)        AS monsoon_share_pct,
       ROUND(SQRT(AVG(rain_jjas_mm * rain_jjas_mm)
                - AVG(rain_jjas_mm) * AVG(rain_jjas_mm)), 1)       AS monsoon_std_mm
FROM climate_annual
GROUP BY decade
ORDER BY decade;

-- Q6. Deficient monsoon years (> 1 std below the long-run mean), counted per decade
--     Useful framing for agriculture and water-planning stakeholders.
WITH stats AS (
    SELECT AVG(rain_jjas_mm) AS mu,
           SQRT(AVG(rain_jjas_mm * rain_jjas_mm) - AVG(rain_jjas_mm) * AVG(rain_jjas_mm)) AS sd
    FROM climate_annual
)
SELECT decade,
       COUNT(*) AS years_in_decade,
       SUM(CASE WHEN rain_jjas_mm < mu - sd THEN 1 ELSE 0 END) AS deficient_years,
       SUM(CASE WHEN rain_jjas_mm > mu + sd THEN 1 ELSE 0 END) AS excess_years
FROM climate_annual, stats
GROUP BY decade
ORDER BY decade;
