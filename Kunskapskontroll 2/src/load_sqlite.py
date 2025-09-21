# src/load.py
import json
import pandas as pd

def save_raw_ads(conn, raw_ads):
    cur = conn.cursor()
    for ad in raw_ads:
        ad_id = str(ad.get("id"))
        cur.execute(
            "INSERT OR REPLACE INTO raw_ads (id, payload) VALUES (?, ?)",
            (ad_id, json.dumps(ad, ensure_ascii=False)),
        )
    conn.commit()

def save_agg_daily(conn, agg_df: pd.DataFrame):
    cur = conn.cursor()
    for _, row in agg_df.iterrows():
        cur.execute(
            """
            INSERT OR REPLACE INTO agg_daily (date, county, occupation_group, ad_count)
            VALUES (?, ?, ?, ?)
            """,
            (row["date"], row["county"], row["occupation_group"], int(row["ad_count"]))
        )
    conn.commit()

