

# src/fetch.py
from typing import List, Dict
import logging
from datetime import datetime, timedelta, timezone
import requests

SAMPLE_ADS: List[Dict] = [
    {
        "id": "sample-1",
        "publish_date": "2025-09-01T10:00:00+02:00",
        "county": "Stockholms län",
        "occupation_group": "Data/IT",
    },
    {
        "id": "sample-2",
        "publish_date": "2025-09-01T11:30:00+02:00",
        "county": "Västra Götalands län",
        "occupation_group": "Vård och omsorg",
    },
    {
        "id": "sample-3",
        "publish_date": "2025-09-02T09:00:00+02:00",
        "county": "Stockholms län",
        "occupation_group": "Data/IT",
    },
]

JOBSEARCH_URL = "https://jobsearch.api.jobtechdev.se/search"


def _pick(d: Dict, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return default


def _normalize_hit(hit: Dict) -> Dict:
    publish_date = _pick(hit, "publication_date", "published", default=None)
    wp = hit.get("workplace_address") or {}
    county = _pick(wp, "county", "region", "municipality", "county_name", default=None)
    occ = hit.get("occupation") or {}
    occupation_group = _pick(
        occ, "label", "field_label", "occupation_group", default=None
    )
    return {
        "id": str(hit.get("id")),
        "publish_date": publish_date,
        "county": county,
        "occupation_group": occupation_group,
    }


def fetch_ads(
    limit: int = 100, use_sample: bool = False, since_days: int | None = None
) -> List[Dict]:
    """
    Fetch job ads from JobTech Search API.
    - Uses q="*" to avoid 400 errors.
    - Paginates with limit+offset until 'limit' records are collected.
    - Applies local date filter if since_days is set.
    - Falls back to SAMPLE_ADS on any exception.
    """
    if use_sample:
        return SAMPLE_ADS[:limit]

    try:
        collected: List[Dict] = []
        page_size = max(1, min(100, limit))  # page size (API-friendly)
        offset = 0
        session = requests.Session()
        headers = {
            "accept": "application/json",
            "User-Agent": "KK2-Student-Project/1.0 (+python)",
        }

        while len(collected) < limit:
            params = {
                "q": "*",             # important: avoids 400 BAD REQUEST
                "limit": page_size,
                "offset": offset,
            }

            # basic retry once on transient errors
            last_exc = None
            for _ in range(2):
                try:
                    resp = session.get(JOBSEARCH_URL, headers=headers, params=params, timeout=30)
                    resp.raise_for_status()
                    break
                except Exception as e:
                    last_exc = e
            else:
                raise last_exc  # if both attempts failed

            data = resp.json() if resp.content else {}
            hits = data.get("hits", []) or []
            if not hits:
                break  # no more data

            normalized = [_normalize_hit(h) for h in hits]
            collected.extend(normalized)
            offset += page_size

            if len(hits) < page_size:
                break  # reached the end

        # trim to requested limit
        out = collected[:limit]

        # local date filter (YYYY-MM-DD prefix)
        if since_days is not None:
            cutoff = (
                datetime.now(timezone.utc) - timedelta(days=since_days)
            ).date().isoformat()
            out = [x for x in out if (x.get("publish_date") or "")[:10] >= cutoff]

        # keep only rows with id
        out = [x for x in out if x.get("id")]

        return out if out else SAMPLE_ADS[:limit]

    except Exception as e:
        logging.exception(f"Error fetching JobTech data: {e}")
        return SAMPLE_ADS[:limit]
