import pandas as pd
from dateutil import parser
from typing import List, Dict

def normalize_ads(raw_ads: List[Dict]) -> pd.DataFrame:
    rows = []
    for ad in raw_ads:
        ad_id = str(ad.get("id"))
        pub = ad.get("publish_date")
        county = ad.get("county")
        occ = ad.get("occupation_group")
        date_only = None
        if pub:
            try:
                date_only = parser.parse(pub).date().isoformat()
            except Exception:
                date_only = None
        rows.append({"id": ad_id, "date": date_only, "county": county, "occupation_group": occ})
    return pd.DataFrame(rows)

def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["date", "county", "occupation_group"], dropna=False).size().reset_index(name="ad_count")
    return grouped
