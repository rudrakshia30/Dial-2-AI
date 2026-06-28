import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env from the backend directory, searching upward from this file's location
_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=str(_env_path))
else:
    load_dotenv(find_dotenv(usecwd=False))

SCHEMES_PATH = Path(__file__).resolve().parents[1] / "schemes.json"


def _data_gov_key():
    return os.getenv("MANDI_PRICES")


def _weather_key():
    return os.getenv("WEATHER_API_KEY")


def _news_key():
    return os.getenv("NEWS_API_KEY")

MANDI_CACHE_PATH = Path(__file__).resolve().parents[1] / "mandi_prices.json"


def _load_mandi_cache():
    """Load local mandi prices cache. Returns list of records or None."""
    if MANDI_CACHE_PATH.exists():
        try:
            with open(MANDI_CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[MandiAPI] Failed to load cache: {e}")
    return None


def _query_mandi_cache(records, canonical_crop, matched_state):
    """Query the local cache for crop/state price and return formatted string."""
    filtered = [
        r for r in records
        if r.get("crop", "").strip().lower() == canonical_crop.lower()
    ]
    if matched_state:
        state_filtered = [
            r for r in filtered
            if r.get("state", "").strip().lower() == matched_state.lower()
        ]
        filtered = state_filtered if state_filtered else filtered

    if not filtered:
        state_phrase = f" {matched_state} mein" if matched_state else ""
        return f"Maaf kijiye,{state_phrase} {canonical_crop} ka daam uplabdh nahi hai."

    # Sort by year descending
    filtered.sort(key=lambda x: float(x.get("year", 0)), reverse=True)

    if matched_state and any(r.get("state", "").strip().lower() == matched_state.lower() for r in filtered):
        latest = [r for r in filtered if r.get("state", "").strip().lower() == matched_state.lower()][0]
        year = int(float(latest.get("year", 2020)))
        price = int(float(latest.get("weighted_average_price_rs__quintal_", 0)))
        return (f"Saal {year} ke weighted average data ke mutabiq, "
                f"{matched_state} mein {canonical_crop} ka daam "
                f"{price} rupaye prati quintal tha.")
    else:
        latest_year = int(float(filtered[0].get("year", 2020)))
        latest = [r for r in filtered if int(float(r.get("year", 0))) == latest_year]
        state_prices = []
        for rec in latest[:3]:
            st = rec.get("state", "").strip()
            pr = int(float(rec.get("weighted_average_price_rs__quintal_", 0)))
            state_prices.append(f"{st} mein {pr}")
        summary = ", ".join(state_prices)
        return (f"Saal {latest_year} ke data ke mutabiq, "
                f"{canonical_crop} ka weighted average mandi daam: "
                f"{summary} rupaye prati quintal tha.")


async def get_mandi_price(crop: str, location: str):
    try:
        crop_lower = (crop or "").lower()
        canonical_crop = None
        if "arhar" in crop_lower or "tur" in crop_lower or "tuar" in crop_lower:
            canonical_crop = "Arhar"
        elif "urad" in crop_lower:
            canonical_crop = "Urad"
        elif "moong" in crop_lower:
            canonical_crop = "Moong"

        # Map location string to canonical state name
        states_list = [
            'Rajasthan', 'Andhra Pradesh', 'Tamil Nadu', 'Bihar', 'Uttar Pradesh',
            'Jharkhand', 'Karnataka', 'Gujarat', 'Chhattisgarh', 'Odisha',
            'West Bengal', 'Madhya Pradesh', 'Maharashtra', 'Telangana'
        ]
        matched_state = None
        if location:
            loc_lower = location.lower()
            for state in states_list:
                if state.lower() in loc_lower or loc_lower in state.lower():
                    matched_state = state
                    break

        # ── 1. Pulse crops (Arhar / Urad / Moong) ─────────────────────────────
        if canonical_crop:

            # A. Try local cache first (instant, no network)
            cache = _load_mandi_cache()
            if cache:
                print(f"[MandiAPI] Using local cache for crop: {canonical_crop}, state: {matched_state}")
                return _query_mandi_cache(cache, canonical_crop, matched_state)

            # B. Fall back to live API if cache not present
            DATA_GOV_KEY = _data_gov_key()
            if not DATA_GOV_KEY:
                print("[MandiAPI] ERROR: MANDI_PRICES key is not set.")
                return "Maaf kijiye, mandi price service abhi available nahi hai."

            url = "https://api.data.gov.in/resource/03b71569-8739-4d6d-9788-b472ea0b8893"
            params = {
                "api-key": DATA_GOV_KEY,
                "format": "json",
                "limit": 100,
                "filters[crop]": canonical_crop,
            }
            if matched_state:
                params["filters[state]"] = matched_state

            print(f"[MandiAPI] Live API query: crop={canonical_crop}, state={matched_state}")
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.get(url, params=params)

            if r.status_code != 200:
                print(f"[MandiAPI] HTTP error: {r.status_code}")
                return f"Maaf kijiye, {crop} ka daam fetch karne mein problem aayi."

            records = r.json().get("records", [])
            if not records:
                state_phrase = f" {matched_state} mein" if matched_state else ""
                return f"Maaf kijiye,{state_phrase} {canonical_crop} ka daam uplabdh nahi hai."

            return _query_mandi_cache(records, canonical_crop, matched_state)

        # ── 2. General crops: live daily mandi API ─────────────────────────────
        else:
            DATA_GOV_KEY = _data_gov_key()
            if not DATA_GOV_KEY:
                print("[MandiAPI] ERROR: MANDI_PRICES key is not set.")
                return "Maaf kijiye, mandi price service abhi available nahi hai."

            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": DATA_GOV_KEY,
                "format": "json",
                "filters[commodity]": crop or "",
            }
            if location:
                params["filters[market]"] = location

            print(f"[MandiAPI] Querying daily mandi API for crop: {crop}, location: {location}")
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.get(url, params=params)

            if r.status_code != 200:
                print(f"[MandiAPI] HTTP error: {r.status_code}")
                return f"Maaf kijiye, {crop} ka daam fetch karne mein problem aayi."

            records = r.json().get("records", [])
            if records:
                price = records[0].get("modal_price")
                loc_phrase = f" {location}" if location else ""
                return f"Aaj{loc_phrase} mandi mein {crop} ka modal daam {price} rupaye prati quintal hai."

    except Exception as e:
        print(f"[MandiAPI] Unexpected error: {repr(e)}")

    loc_phrase = f" {location}" if location else ""
    return f"Maaf kijiye,{loc_phrase} {crop or 'crop'} ka daam uplabdh nahi hai."


async def get_weather(location):

    try:

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
        )

        params = {
            "q": location,
            "appid": _weather_key(),
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)

        data = r.json()

        temp = data["main"]["temp"]

        desc = data["weather"][0]["description"]

        return (
            f"Aaj {location} mein "
            f"{temp} degree temperature hai "
            f"aur {desc} hai."
        )

    except Exception:
        return (
            "Maaf kijiye, mausam ki "
            "jaankari uplabdh nahi hai."
        )


async def get_govt_scheme(query):

    try:

        with open(SCHEMES_PATH, encoding="utf-8") as f:
            schemes = json.load(f)

        q = query.lower()

        for scheme in schemes:
            if any(
                keyword.lower() in q
                for keyword in scheme["keywords"]
            ):
                return (
                    f"{scheme['name']}\n\n"
                    f"{scheme['description_hindi']}\n\n"
                    f"Patrata: "
                    f"{scheme['eligibility_hindi']}\n\n"
                    f"Labh: "
                    f"{scheme['benefit_hindi']}"
                )

    except Exception:
        pass

    return (
        "Maaf kijiye, is yojana ki "
        "jaankari uplabdh nahi hai."
    )


async def get_news(query=None, category=None, country="in"):
    """Fetch live news from NewsAPI.

    Args:
        query: Search term for the 'everything' endpoint (e.g. "cricket").
        category: Category for top-headlines (e.g. "technology", "sports").
        country: Country code for top-headlines (default "in" for India).

    Returns:
        A short, spoken-friendly string summarising the top 3 headlines.
    """

    NEWS_API_KEY = _news_key()
    if not NEWS_API_KEY:
        print("[NewsAPI] ERROR: NEWS_API_KEY is not set in environment.")
        return "Maaf kijiye, news service abhi available nahi hai."

    try:
        # Build the request URL
        if query:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            }
            print(f"[NewsAPI] Searching news for query: {query}")
        else:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": country,
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            }
            if category:
                params["category"] = category
                print(f"[NewsAPI] Fetching {category} headlines for country: {country}")
            else:
                print(f"[NewsAPI] Fetching top headlines for country: {country}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)

        # Handle HTTP-level errors
        if r.status_code == 429:
            print("[NewsAPI] Rate limit exceeded.")
            return "Maaf kijiye, news service par bahut zyada requests ho gayi hain. Thodi der baad try karein."

        if r.status_code == 401:
            print("[NewsAPI] Invalid API key.")
            return "Maaf kijiye, news service ki API key valid nahi hai."

        if r.status_code != 200:
            print(f"[NewsAPI] HTTP error: {r.status_code}")
            return "Maaf kijiye, news fetch karne mein problem aayi. Thodi der baad try karein."

        data = r.json()

        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            print(f"[NewsAPI] API error: {error_msg}")
            return "Maaf kijiye, news service se response nahi mila."

        articles = data.get("articles", [])

        if not articles:
            print("[NewsAPI] No articles found.")
            topic = query or category or "top"
            return f"Maaf kijiye, {topic} news ke liye koi article nahi mila."

        # Format top 3 articles in a spoken-friendly way
        lines = []
        for i, article in enumerate(articles[:3], 1):
            title = article.get("title", "").strip()
            # Remove source suffix like " - NDTV" from title
            if " - " in title:
                title = title.rsplit(" - ", 1)[0].strip()
            if title:
                lines.append(f"Khabar {i}: {title}.")

        result = " ".join(lines)
        print(f"[NewsAPI] Returning {len(lines)} headlines.")
        return result

    except httpx.TimeoutException:
        print("[NewsAPI] Request timed out.")
        return "Maaf kijiye, news service se response nahi mila. Thodi der baad try karein."
    except Exception as e:
        print(f"[NewsAPI] Unexpected error: {repr(e)}")
        return "Maaf kijiye, news fetch karne mein problem aayi."
