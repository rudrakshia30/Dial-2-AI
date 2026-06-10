import os
import json
import httpx
from pathlib import Path


DATA_GOV_KEY = os.getenv("DATA_GOV_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SCHEMES_PATH = Path(__file__).resolve().parents[1] / "schemes.json"


async def get_mandi_price(
        crop: str,
        location: str
):
    try:

        url = (
            "https://api.data.gov.in/resource/"
            "9ef84268-d588-465a-a308-a864a43d0070"
        )

        params = {
            "api-key": DATA_GOV_KEY,
            "format": "json",
            "filters[commodity]": crop,
            "filters[market]": location
        }

        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)

        data = r.json()

        records = data.get("records", [])

        if records:
            price = records[0]["modal_price"]

            return (
                f"Aaj {location} mandi mein "
                f"{crop} ka modal daam "
                f"{price} rupaye prati quintal hai."
            )

    except Exception:
        pass

    return (
        f"Maaf kijiye, "
        f"{crop} ka daam uplabdh nahi hai."
    )


async def get_weather(location):

    try:

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
        )

        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
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
