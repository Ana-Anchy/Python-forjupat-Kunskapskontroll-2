
# Python-fördjupat  
## Python Knowledge Assessment (Kunskapskontroll 2) – Arbetsförmedlingen Job Ads API  

### 📌 Overview  
This repository contains my Python knowledge assessment (**Kunskapskontroll 2**), where I developed a complete **data pipeline** to fetch, store, analyze, and visualize job advertisements from the **Arbetsförmedlingen (Swedish Public Employment Service) Open JobTech API**.  

The pipeline demonstrates how **open labor market data** can be used to:  
- Identify the most in-demand **occupational groups** and **counties**  
- Analyze **short-term trends** (7-day horizon)  
- Visualize combinations of **occupation × county** using heatmaps  
- Produce a **7-day forecast** to anticipate upcoming labor demand  

The process automates data ingestion, transformation, storage in **SQLite**, and generates reports in both **CSV and graphical form (charts/plots)**.  

---

### 🛠️ Demonstrated Practical Skills  
- **API integration** – robust data retrieval with pagination and fallback  
- **ETL pipeline** – Extract, Transform, Load flow implemented in Python  
- **Database management** – Storing raw and aggregated data in SQLite  
- **Data cleaning & transformation** – Using Pandas for normalization of dates, occupations, and counties  
- **Data visualization** – Line plots, bar charts, heatmaps, and forecasts with Matplotlib  
- **Trend analysis** – 7-day comparison including delta and percentage change  
- **Prediction (mini-ML)** – Forecasting job demand using Holt-Winters (Exponential Smoothing)  

---

### 🔄 ETL Process  

#### 1️⃣ Extract  
**Purpose:** Fetch job advertisements from the Arbetsförmedlingen JobTech API.  
**Key Tasks:**  
- Connect to the API using `requests`  
- Handle pagination (`limit + offset`)  
- Apply local date filters (e.g., `since_days`)  
- Use sample data fallback when API is unavailable  

#### 2️⃣ Transform  
**Purpose:** Clean and normalize raw data for consistent analysis.  
**Key Tasks:**  
- Convert publication dates to `YYYY-MM-DD`  
- Normalize county and occupation group fields  
- Replace missing values with `"Unknown"` or exclude where appropriate  
- Aggregate ad counts by date, county, and occupation group  

#### 3️⃣ Load  
**Purpose:** Store both raw and aggregated data into a SQLite database.  
**Database tables:**  
- `raw_ads` – Raw API responses  
- `agg_daily` – Aggregated daily counts (date × county × occupation group)  

#### 4️⃣ Report  
**Purpose:** Generate analysis reports and visualizations.  
**Output files (stored in `/reports`):**  
- `daily_total.png` – Total job ads per day  
- `top10_occupations.png` – Top-10 occupational groups  
- `top10_counties.png` – Top-10 counties  
- `heatmap_occupations_by_county.png` – Heatmap of occupation × county  
- `trend_occ_7d.csv` / `trend_county_7d.csv` – 7-day trend analysis (growth/decline)  
- `forecast_total_next7.png` – Forecast of total job ads (next 7 days)  
- `forecast_top_occ_7d.png` / `forecast_top_occ_7d.csv` – Forecasted top occupational groups  

---

## 📊 Example Visualizations

**Total ads over time with forecast:**  
![forecast_total_next7](Kunskapskontroll%202/reports/forecast_total_next7.png)

**Top-10 occupational groups:**  
![top10_occupations](Kunskapskontroll%202/reports/top10_occupations.png)

**Top-10 counties:**  
![top10_counties](Kunskapskontroll%202/reports/top10_counties.png)

**Occupation × County heatmap:**  
![heatmap_occupations_by_county](Kunskapskontroll%202/reports/heatmap_occupations_by_county.png)

**7-day forecast – Top occupations:**  
![forecast_top_occ_7d](Kunskapskontroll%202/reports/forecast_top_occ_7d.png)




---

### 🚀 How to Run the Project  

1. Clone the repository  
   ```bash
   git clone <repo-url>
   cd <repo-folder>


   pip install -r requirements.txt
   python main.py
   python report.py



