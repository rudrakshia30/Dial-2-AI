import os
import json
import httpx
from pathlib import Path


DATA_GOV_KEY = os.getenv("DATA_GOV_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
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
