# report.py
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.db import get_conn

# --- Läs data ur SQLite ---
with get_conn() as conn:
    df = pd.read_sql_query("SELECT * FROM agg_daily ORDER BY date", conn)
print(df)

# --- utput dir ---
Path("reports").mkdir(parents=True, exist_ok=True)

# --- Diagram 1: total per datum ---
df_total = df.groupby("date")["ad_count"].sum().reset_index()
plt.figure()
plt.plot(df_total["date"], df_total["ad_count"])
plt.title("Antal annonser per datum (total)")
plt.xlabel("Datum")
plt.ylabel("Antal")
plt.xticks(rotation=45)
plt.tight_layout()
out1 = os.path.join("reports", "daily_total.png")
plt.savefig(out1)
print("Sparat:", out1)

# --- Diagram 2: top-10 yrkesgrupper ---
top_occ = (
    df.groupby("occupation_group")["ad_count"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)
plt.figure()
plt.bar(top_occ["occupation_group"], top_occ["ad_count"])
plt.title("Top-10 yrkesgrupper (totalt antal annonser)")
plt.xlabel("Yrkesgrupp")
plt.ylabel("Antal")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
out2 = os.path.join("reports", "top10_occupations.png")
plt.savefig(out2)
print("Sparat:", out2)

# --- Diagram 3: top-10 län ---
top_counties = (
    df.groupby("county")["ad_count"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)
plt.figure()
plt.bar(top_counties["county"], top_counties["ad_count"])
plt.title("Top-10 län (totalt antal annonser)")
plt.xlabel("Län")
plt.ylabel("Antal")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
out3 = os.path.join("reports", "top10_counties.png")
plt.savefig(out3)
print("Sparat:", out3)

# --- Diagram 4: heatmap (yrkesgrupp × län) ---
top_occ_names = (
    df.groupby("occupation_group")["ad_count"].sum()
      .sort_values(ascending=False).head(12).index.tolist()
)
top_county_names = (
    df.groupby("county")["ad_count"].sum()
      .sort_values(ascending=False).head(10).index.tolist()
)
df_top = df[df["occupation_group"].isin(top_occ_names) & df["county"].isin(top_county_names)]
pivot = (
    df_top.pivot_table(index="occupation_group", columns="county",
                       values="ad_count", aggfunc="sum", fill_value=0)
      .reindex(index=top_occ_names, columns=top_county_names)
)

def shorten(s, n=28):
    if s is None: return ""
    s = str(s)
    return s if len(s) <= n else s[:n-1] + "…"

xlabels = [shorten(c) for c in pivot.columns]
ylabels = [shorten(r) for r in pivot.index]

fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
im = ax.imshow(pivot.values, aspect="auto")
cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("Antal annonser")
ax.set_title("Yrkesgrupp × Län (antal annonser)")
ax.set_xticks(np.arange(pivot.shape[1]))
ax.set_xticklabels(xlabels, rotation=35, ha="right", fontsize=9)
ax.set_yticks(np.arange(pivot.shape[0]))
ax.set_yticklabels(ylabels, fontsize=10)
fig.subplots_adjust(left=0.35, bottom=0.28, right=0.97, top=0.90)
out4 = os.path.join("reports", "heatmap_occupations_by_county.png")
plt.tight_layout()
plt.savefig(out4)
print("Sparat:", out4)



# --- 5) Trend-analys 7 dagar (CSV + terminal) ---
df["date"] = pd.to_datetime(df["date"], errors="coerce")
last_day = df["date"].max()

if pd.notna(last_day):
    start_day = last_day - pd.Timedelta(days=6)
    df7 = df[(df["date"] >= start_day) & (df["date"] <= last_day)].copy()

    def start_series(s):
        s = s.sort_index()
        return int(s.iloc[0]) if len(s) else 0

    def end_series(s):
        s = s.sort_index()
        return int(s.iloc[-1]) if len(s) else 0

    # yrkesgrupp
    occ_ts = (
        df7.groupby(["occupation_group", "date"])["ad_count"].sum()
           .unstack(fill_value=0)
           .sort_index(axis=1)
    )
    occ_daily = pd.DataFrame({
        "occupation_group": occ_ts.index,
        "start": occ_ts.apply(start_series, axis=1),
        "end":   occ_ts.apply(end_series,   axis=1),
    })
    occ_daily["delta"] = occ_daily["end"] - occ_daily["start"]
    occ_daily["pct"] = occ_daily.apply(lambda r: (r["delta"]/r["start"]) if r["start"]>0 else None, axis=1)
    occ_daily["pct"] = occ_daily.apply(
        lambda r: 1.0 if r["start"] == 0 and r["end"] > 0 else r["pct"], axis=1
    )
    occ_daily = occ_daily.sort_values(by="delta", ascending=False).reset_index(drop=True)

    # län
    county_ts = (
        df7.groupby(["county", "date"])["ad_count"].sum()
           .unstack(fill_value=0)
           .sort_index(axis=1)
    )
    county_daily = pd.DataFrame({
        "county": county_ts.index,
        "start": county_ts.apply(start_series, axis=1),
        "end":   county_ts.apply(end_series,   axis=1),
    })
    county_daily["delta"] = county_daily["end"] - county_daily["start"]
    county_daily["pct"] = county_daily.apply(lambda r: (r["delta"]/r["start"]) if r["start"]>0 else None, axis=1)
    county_daily["pct"] = county_daily.apply(
        lambda r: 1.0 if r["start"] == 0 and r["end"] > 0 else r["pct"], axis=1
    )
    county_daily = county_daily.sort_values(by="delta", ascending=False).reset_index(drop=True)

    # 
    occ_daily.to_csv(os.path.join("reports", "trend_occ_7d.csv"), encoding="utf-8-sig", index=False)
    county_daily.to_csv(os.path.join("reports", "trend_county_7d.csv"), encoding="utf-8-sig", index=False)

    print("\nTop 10 rast (yrkesgrupp) – 7d:")
    print(occ_daily.head(10)[["occupation_group", "start", "end", "delta", "pct"]])
    print("\nTop 10 pad (yrkesgrupp) – 7d:")
    print(occ_daily.tail(10)[["occupation_group", "start", "end", "delta", "pct"]])

    print("\nTop 10 rast (län) – 7d:")
    print(county_daily.head(10)[["county", "start", "end", "delta", "pct"]])
    print("\nTop 10 pad (län) – 7d:")
    print(county_daily.tail(10)[["county", "start", "end", "delta", "pct"]])
else:
    print("OBS: Inga giltiga datum i df['date'] – hoppar över 7d trend.")

# --- 6) Mini-forecast (MVG) ---
import pandas as pd
import matplotlib.pyplot as plt
import os

# Försök använda statsmodels; fallback till enkel 7-d medel om ej tillgängligt
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    USE_SM = True
except Exception:
    USE_SM = False

# Säkerställ datetime & sortering
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"]).sort_values("date")

# ===== 6.1 Totalprognos (7 dagar) =====
ts_total = df.groupby("date")["ad_count"].sum()
# gör daglig frekvens med 0 som fyllnad
ts_total = ts_total.asfreq("D", fill_value=0)

if USE_SM and len(ts_total) >= 7:
    try:
        model = ExponentialSmoothing(
            ts_total, trend="add", seasonal=None, initialization_method="estimated"
        )
        fit = model.fit(optimized=True)
        fc_total = fit.forecast(7)
    except Exception:
        fc_total = pd.Series(
            [ts_total.tail(7).mean()] * 7,
            index=pd.date_range(ts_total.index.max() + pd.Timedelta(days=1), periods=7, freq="D"),
        )
else:
    fc_total = pd.Series(
        [ts_total.tail(7).mean()] * 7,
        index=pd.date_range(ts_total.index.max() + pd.Timedelta(days=1), periods=7, freq="D"),
    )

# Plotta: senaste 30 dagar + prognos 7 dagar
plt.figure()
ax = plt.gca()
ts_total.tail(30).plot(ax=ax, label="Utfall (senaste 30 dagar)")
fc_total.plot(ax=ax, label="Prognos (7 dagar)")
plt.title("Prognos av totala annonser (7 dagar)")
plt.xlabel("Datum"); plt.ylabel("Antal")
plt.legend()
plt.tight_layout()
out_total = os.path.join("reports", "forecast_total_next7.png")
plt.savefig(out_total)
print("Sparat:", out_total)

# ===== 6.2 Prognos per yrkesgrupp (ranking nästa vecka) =====
# Välj kandidater: de 15 mest aktiva senaste 14 dagarna (stabilare serier)
recent_cut = df["date"].max() - pd.Timedelta(days=13)
recent = df[df["date"] >= recent_cut]
candidates = (
    recent.groupby("occupation_group")["ad_count"]
          .sum().sort_values(ascending=False).head(15).index
)

rows = []
for occ in candidates:
    s = (df[df["occupation_group"] == occ]
         .groupby("date")["ad_count"].sum()
         .asfreq("D", fill_value=0))

    # Prognos för varje serie
    if USE_SM and len(s) >= 7:
        try:
            m = ExponentialSmoothing(s, trend="add", seasonal=None, initialization_method="estimated")
            f = m.fit(optimized=True)
            fc = f.forecast(7)
        except Exception:
            fc = pd.Series([s.tail(7).mean()]*7,
                           index=pd.date_range(s.index.max()+pd.Timedelta(days=1), periods=7, freq="D"))
    else:
        fc = pd.Series([s.tail(7).mean()]*7,
                       index=pd.date_range(s.index.max()+pd.Timedelta(days=1), periods=7, freq="D"))

    hist7 = float(s.tail(7).sum())
    pred7 = float(fc.sum())
    rows.append({
        "occupation_group": occ,
        "hist_last7": hist7,
        "forecast_next7": pred7,
        "delta": pred7 - hist7,
        "pct": (pred7 - hist7)/hist7 if hist7 > 0 else None
    })

import pandas as pd
forecast_df = pd.DataFrame(rows).sort_values("forecast_next7", ascending=False)
out_csv = os.path.join("reports", "forecast_top_occ_7d.csv")
forecast_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
print("Sparat:", out_csv)
print("\nPrognos – topp yrkesgrupper (summa nästa 7 d):")
print(forecast_df.head(10)[["occupation_group","hist_last7","forecast_next7","delta","pct"]])

# Plotta topp 5 prognostiserade yrken
top5 = forecast_df.head(5)
plt.figure()
plt.bar(top5["occupation_group"], top5["forecast_next7"])
plt.title("Prognos nästa 7 dagar – toppyrken (summa annonser)")
plt.xlabel("Yrkesgrupp"); plt.ylabel("Prognos (antal)")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
out_top = os.path.join("reports", "forecast_top_occ_7d.png")
plt.savefig(out_top)
print("Sparat:", out_top)
