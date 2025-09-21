from src.db import init_db, get_conn
from src.fetch import fetch_ads
from src.load_sqlite import save_raw_ads, save_agg_daily
from src.transform import normalize_ads, aggregate_daily

def main():
    print("Init DB…")
    init_db()

    # 
    ads = fetch_ads(limit=500, use_sample=False, since_days=1)
    print("Fetched:", len(ads))

    with get_conn() as conn:
        save_raw_ads(conn, ads)

    df = normalize_ads(ads)
    agg = aggregate_daily(df)

    with get_conn() as conn:
        save_agg_daily(conn, agg)
        cur = conn.cursor()
        cur.execute("SELECT * FROM agg_daily ORDER BY date, county, occupation_group;")
        rows = cur.fetchall()

    print("agg_daily rows (sample):")
    for r in rows[:25]:
        print(r)

if __name__ == "__main__":
    main()