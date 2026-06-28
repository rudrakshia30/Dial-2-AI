"""
One-time script: Download the crop-wise weighted average mandi prices dataset
(Arhar, Urad, Moong, 2016-2020) from data.gov.in and save it locally.

Run once from the backend directory:
    python download_mandi_data.py

This creates app/mandi_prices.json which is loaded at runtime instead of
making slow live API calls.
"""
import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=str(env_path))

API_KEY = os.getenv("MANDI_PRICES")
if not API_KEY:
    raise SystemExit("ERROR: MANDI_PRICES not found in .env")

URL = "https://api.data.gov.in/resource/03b71569-8739-4d6d-9788-b472ea0b8893"
OUT_PATH = Path(__file__).resolve().parent / "app" / "mandi_prices.json"

all_records = []
limit = 100
offset = 0

print(f"Downloading mandi prices data from data.gov.in...")

while True:
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }
    print(f"  Fetching offset={offset} ...", end=" ", flush=True)
    try:
        with httpx.Client(timeout=90.0) as client:
            r = client.get(URL, params=params)
        r.raise_for_status()
        data = r.json()
        records = data.get("records", [])
        total = int(data.get("total", 0))
        print(f"got {len(records)} records (total={total})")
        all_records.extend(records)
        if offset + limit >= total or not records:
            break
        offset += limit
    except Exception as e:
        print(f"\nFailed at offset={offset}: {e}")
        break

print(f"\nTotal records downloaded: {len(all_records)}")

# Save to file
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=2, ensure_ascii=False)

print(f"Saved to: {OUT_PATH}")
print("Done! The backend will now use this local cache instead of live API calls.")
