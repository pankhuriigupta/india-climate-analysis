# 🌦️ India Climate Analysis & Prediction (1901–2017)

A data science project analyzing over 116 years of India's temperature and rainfall data to identify long-term climate trends and forecast future patterns using time series models.

---

## 📌 Project Overview

Climate change is one of the most pressing issues of our time. This project dives into historical climate data for India — spanning from 1901 to 2017 — to uncover how temperatures and rainfall patterns have shifted over more than a century, and to forecast what the future might look like.

| Property | Value |
|---|---|
| Dataset | India Annual Temperature & Rainfall (1901–2017) |
| Time Span | 116 years |
| Data Source | Kaggle |
| Output | Cleaned dataset exported for Tableau visualization |

---

## 🔍 What This Project Does

- Loads and cleans historical temperature and rainfall CSV datasets
- Performs exploratory data analysis (EDA) with trend visualizations
- Analyzes monthly and annual climate patterns across India
- Builds time series forecasting models (Linear Regression, Prophet, ARIMA)
- Exports a cleaned, Tableau-ready dataset for dashboard visualization

---

## 📊 Analysis Highlights

- **Temperature Trends** — Monthly and annual average temperatures tracked across 116 years, revealing a clear warming trend in India
- **Rainfall Patterns** — Area-weighted rainfall data analyzed for seasonal and annual shifts
- **Forecasting** — Future temperature and rainfall values predicted using multiple models
- **Tableau Integration** — Cleaned dataset exported as `cleaned_national_climate_1901_2017_for_tableau.csv` for interactive dashboarding

---

## 🛠️ Tech Stack

- **Language:** Python
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, Prophet, pmdarima
- **Environment:** Google Colab
- **Visualization:** Matplotlib, Seaborn, Tableau (downstream)

---

## 📁 Project Structure

```
├── temp_rain.ipynb                              # Main analysis notebook
├── rainfall_area-wt_India_1901-2015.csv         # Rainfall dataset
├── annual_temperature_1901_2017.csv             # Temperature dataset
└── cleaned_national_climate_1901_2017_for_tableau.csv  # Tableau-ready output
```

---

## 🚀 How to Run

1. Clone this repository
   ```bash
   git clone https://github.com/YourUsername/india-climate-analysis
   cd india-climate-analysis
   ```

2. Open the notebook in Google Colab or Jupyter
   ```bash
   jupyter notebook temp_rain.ipynb
   ```

3. Install dependencies
   ```bash
   pip install prophet pmdarima pandas numpy matplotlib seaborn scikit-learn
   ```

4. Upload the dataset CSVs when prompted and run all cells

---

## 👩‍💻 Author

**Pankhuri Gupta**  
B.Tech, Computer Science and Engineering — Data Science  
SRM Institute of Science and Technology, Ghaziabad  
📧 pg0001@srmist.edu.in  
🔗 [LinkedIn](https://linkedin.com/in/yourprofile)
