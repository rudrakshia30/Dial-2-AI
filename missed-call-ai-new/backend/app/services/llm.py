import os
from dotenv import load_dotenv
from google import genai

from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

import json
import re
from .data_fetch import get_weather, get_mandi_price, get_govt_scheme

SYSTEM_PROMPT = """You are a smart, friendly AI voice assistant. You help people over phone calls.

Rules:
1. Language: Detect user's language (Hindi, Hinglish, or English) and reply in same. For Hindi, use Roman script like "Namaste, kaise hain aap". NEVER use Devanagari.
2. Keep replies very short, 1-2 sentences max. This is a phone call.
3. Speak naturally. No asterisks, bullets, markdown, emojis, or special characters.
4. If you see [WEATHER:...] or [MANDI:...] or [SCHEME:...] tags, use that real data in your answer. Never invent numbers.
5. You can help with anything: general knowledge, math, health tips, education, jobs, technology, cooking, weather, crop prices, govt schemes, farming, and more.
6. Be warm and helpful. If the user sounds confused, guide them gently."""

# --- Keyword-based intent detection (saves 1 API call per message) ---
WEATHER_KEYWORDS = [
    "weather", "mausam", "temperature", "barish", "rain", "thand", "garmi", "dhoop", "toofan", "storm", "humidity", "hawa",
    # Devanagari
    "मौसम", "तापमान", "टेंपरेचर", "बारिश", "बरसात", "ठंड", "गर्मी", "धूप", "तूफान", "हवा", "नमी",
]
MANDI_KEYWORDS = [
    "price", "rate", "daam", "bhav", "mandi", "kilo", "quintal",
    # Devanagari
    "दाम", "भाव", "मंडी", "किलो", "क्विंटल", "रुपए", "रुपये", "कीमत", "रेट",
]
SCHEME_KEYWORDS = [
    "yojana", "scheme", "pm kisan", "ayushman", "fasal bima", "kcc", "credit card", "pmay", "awas", "mnrega", "nrega", "rojgar", "sinchai", "irrigation", "soil health", "enam",
    # Devanagari
    "योजना", "स्कीम", "किसान", "आयुष्मान", "फसल बीमा", "आवास", "रोजगार", "सिंचाई", "मनरेगा",
]

# Crop names: Roman + Devanagari
CROP_KEYWORDS_MAP = {
    # Roman -> API name
    "tomato": "Tomato", "tamatar": "Tomato", "onion": "Onion", "pyaz": "Onion", "pyaaz": "Onion",
    "potato": "Potato", "aloo": "Potato", "wheat": "Wheat", "gehun": "Wheat",
    "rice": "Rice", "chawal": "Rice", "dhan": "Paddy(Dhan)", "soybean": "Soyabean",
    "cotton": "Cotton", "kapas": "Cotton", "chana": "Bengal Gram(Gram)", "dal": "Arhar (Tur/Red Gram)",
    "moong": "Green Gram (Moong)", "urad": "Black Gram (Urd Beans)", "tur": "Arhar (Tur/Red Gram)",
    "arhar": "Arhar (Tur/Red Gram)", "jowar": "Jowar(Sorghum)", "bajra": "Bajra(Pearl Millet)",
    "maize": "Maize", "makka": "Maize", "sarson": "Mustard", "mustard": "Mustard",
    "groundnut": "Groundnut", "mungfali": "Groundnut", "sugarcane": "Sugarcane", "ganna": "Sugarcane",
    "banana": "Banana", "kela": "Banana", "apple": "Apple", "seb": "Apple",
    "mango": "Mango", "aam": "Mango", "brinjal": "Brinjal", "baingan": "Brinjal",
    "cabbage": "Cabbage", "gobi": "Cauliflower", "peas": "Peas", "matar": "Peas",
    "garlic": "Garlic", "lehsun": "Garlic", "ginger": "Ginger", "adrak": "Ginger",
    "turmeric": "Turmeric", "haldi": "Turmeric", "chilli": "Chillies", "mirch": "Chillies",
    "lemon": "Lemon", "nimbu": "Lemon", "papaya": "Papaya", "guava": "Guava",
    "amrud": "Guava", "grapes": "Grapes", "angoor": "Grapes", "pomegranate": "Pomegranate",
    "anar": "Pomegranate", "coconut": "Coconut", "nariyal": "Coconut",
    "carrot": "Carrot", "gajar": "Carrot", "radish": "Raddish", "mooli": "Raddish",
    "spinach": "Spinach", "palak": "Spinach", "coriander": "Corriander(Leaf)", "dhaniya": "Corriander(Leaf)",
    "okra": "Ladies Finger", "bhindi": "Ladies Finger", "karela": "Bitter gourd",
    "lauki": "Bottle gourd", "kaddu": "Pumpkin", "kheera": "Cucumber",
    "tarbooz": "Water Melon",
    # Devanagari -> API name
    "टमाटर": "Tomato", "प्याज": "Onion", "प्याज़": "Onion", "आलू": "Potato",
    "गेहूं": "Wheat", "गेहूँ": "Wheat", "चावल": "Rice", "धान": "Paddy(Dhan)",
    "सोयाबीन": "Soyabean", "कपास": "Cotton", "चना": "Bengal Gram(Gram)",
    "दाल": "Arhar (Tur/Red Gram)", "मूंग": "Green Gram (Moong)", "उड़द": "Black Gram (Urd Beans)",
    "तुअर": "Arhar (Tur/Red Gram)", "अरहर": "Arhar (Tur/Red Gram)",
    "ज्वार": "Jowar(Sorghum)", "बाजरा": "Bajra(Pearl Millet)", "मक्का": "Maize",
    "सरसों": "Mustard", "मूंगफली": "Groundnut", "गन्ना": "Sugarcane",
    "केला": "Banana", "सेब": "Apple", "आम": "Mango", "बैंगन": "Brinjal",
    "गोभी": "Cauliflower", "फूलगोभी": "Cauliflower", "मटर": "Peas",
    "लहसुन": "Garlic", "अदरक": "Ginger", "हल्दी": "Turmeric",
    "मिर्च": "Chillies", "नींबू": "Lemon", "पपीता": "Papaya",
    "अमरूद": "Guava", "अंगूर": "Grapes", "अनार": "Pomegranate",
    "नारियल": "Coconut", "गाजर": "Carrot", "मूली": "Raddish",
    "पालक": "Spinach", "धनिया": "Corriander(Leaf)", "भिंडी": "Ladies Finger",
    "करेला": "Bitter gourd", "लौकी": "Bottle gourd", "कद्दू": "Pumpkin",
    "खीरा": "Cucumber", "तरबूज": "Water Melon",
}

# City name mapping: Devanagari/Hindi -> English (for weather API)
CITY_MAP = {
    "दिल्ली": "Delhi", "मुंबई": "Mumbai", "कोलकाता": "Kolkata", "चेन्नई": "Chennai",
    "बेंगलुरु": "Bengaluru", "बैंगलोर": "Bangalore", "हैदराबाद": "Hyderabad",
    "पुणे": "Pune", "अहमदाबाद": "Ahmedabad", "जयपुर": "Jaipur", "लखनऊ": "Lucknow",
    "कानपुर": "Kanpur", "नागपुर": "Nagpur", "इंदौर": "Indore", "भोपाल": "Bhopal",
    "पटना": "Patna", "वाराणसी": "Varanasi", "आगरा": "Agra", "नासिक": "Nashik",
    "नाशिक": "Nashik", "सूरत": "Surat", "राजकोट": "Rajkot", "वडोदरा": "Vadodara",
    "चंडीगढ़": "Chandigarh", "लुधियाना": "Ludhiana", "अमृतसर": "Amritsar",
    "रांची": "Ranchi", "जमशेदपुर": "Jamshedpur", "भुवनेश्वर": "Bhubaneswar",
    "विशाखापट्टनम": "Visakhapatnam", "कोच्चि": "Kochi", "तिरुवनंतपुरम": "Thiruvananthapuram",
    "गुवाहाटी": "Guwahati", "देहरादून": "Dehradun", "शिमला": "Shimla",
    "श्रीनगर": "Srinagar", "जोधपुर": "Jodhpur", "उदयपुर": "Udaipur",
    "कोटा": "Kota", "अजमेर": "Ajmer", "गोरखपुर": "Gorakhpur",
    "मेरठ": "Meerut", "प्रयागराज": "Prayagraj", "इलाहाबाद": "Prayagraj",
    "मथुरा": "Mathura", "अलीगढ़": "Aligarh", "बरेली": "Bareilly",
    "मुरादाबाद": "Moradabad", "सहारनपुर": "Saharanpur", "रायपुर": "Raipur",
    "गुरुग्राम": "Gurugram", "गुड़गांव": "Gurugram", "नोएडा": "Noida",
    "फरीदाबाद": "Faridabad", "गाजियाबाद": "Ghaziabad",
}

def _detect_intent(question: str):
    q = question.lower()
    # Check weather (works for both Roman and Devanagari)
    if any(w in q or w in question for w in WEATHER_KEYWORDS):
        loc = _extract_location(question)
        if loc:
            return {"intent": "weather", "location": loc}
    # Check mandi/price
    if any(w in q or w in question for w in MANDI_KEYWORDS):
        crop = _extract_crop(question)
        loc = _extract_location(question)
        if crop and loc:
            return {"intent": "mandi", "crop": crop, "location": loc}
        elif crop:
            return {"intent": "mandi", "crop": crop, "location": ""}
    # Check scheme
    if any(w in q or w in question for w in SCHEME_KEYWORDS):
        return {"intent": "scheme"}
    return {"intent": "general"}

def _extract_location(text: str):
    # 1. Check for Devanagari city names first
    for hindi_name, eng_name in CITY_MAP.items():
        if hindi_name in text:
            return eng_name
    # 2. Try Roman script patterns
    patterns = [
        r'(?:in|at|of|mein|ka|ki|ke|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            loc = m.group(1).strip()
            skip = {"Kya", "Aaj", "Kal", "Mujhe", "Bhai", "Batao", "Please", "Sir", "Madam", "Mausam", "Weather", "Price", "Rate", "Daam", "How", "What", "Tell", "Kaisa", "Kaise"}
            if loc not in skip:
                return loc
    return None

def _extract_crop(text: str):
    # Check both original text (for Devanagari) and lowercase (for Roman)
    q = text.lower()
    for keyword, api_name in CROP_KEYWORDS_MAP.items():
        if keyword in text or keyword in q:
            return api_name
    return None

async def get_ai_reply(question: str, history: list = None):

    try:
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

        # --- Keyword-based live data injection (NO extra API call) ---
        intent_data = _detect_intent(question)
            
        context = ""
        if intent_data.get("intent") == "weather" and intent_data.get("location"):
            context = "\n[WEATHER: " + await get_weather(intent_data["location"]) + "]"
        elif intent_data.get("intent") == "mandi" and intent_data.get("crop"):
            loc = intent_data.get("location", "")
            if loc:
                context = "\n[MANDI: " + await get_mandi_price(intent_data["crop"], loc) + "]"
        elif intent_data.get("intent") == "scheme":
            context = "\n[SCHEME: " + await get_govt_scheme(question) + "]"

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=question + context)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=150,
        )

        # Retry up to 2 times for rate-limit errors (free API key)
        last_err = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=config
                )
                return response.text.strip()
            except Exception as api_err:
                last_err = api_err
                print(f"Gemini API attempt {attempt+1} failed: {repr(api_err)}")
                if attempt < 2:
                    import asyncio
                    await asyncio.sleep(2)

        print("Gemini Error (all retries failed):", repr(last_err))
        return "Maaf kijiye, thodi der mein dobara try karein."

    except Exception as e:
        print("Gemini Error (outer):", repr(e))
        return "Maaf kijiye, thodi der mein dobara try karein."


async def generate_call_summary_and_lead(history: list):
    if not history:
        return {
            "customer_name": "Unknown",
            "intent": "None",
            "outcome": "No conversation",
            "sentiment": "Neutral",
            "summary": "No speech recorded",
            "lead": {"name": "Unknown", "phone": "Unknown", "city": "Unknown", "interest": "Unknown"}
        }

    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])

    prompt = f"""
    Analyze the following phone call conversation history and extract the following structured details:
    1. Customer Name (if mentioned, else "Unknown")
    2. Primary Intent of the call (e.g. general query, weather query, scheme query)
    3. Outcome of the call (e.g., Question answered, Callback requested, Drop-off)
    4. Overall Sentiment of the caller (Positive, Neutral, Negative)
    5. Call Summary (a 1-sentence recap of what was discussed)
    6. Lead Information (Extract details if caller shows interest in any product/service/scheme, including Name, City, Interest, and Phone)

    Conversation History:
    {history_text}

    Return the output strictly as a JSON object with the following keys:
    {{
      "customer_name": "...",
      "intent": "...",
      "outcome": "...",
      "sentiment": "...",
      "summary": "...",
      "lead": {{
        "name": "...",
        "phone": "...",
        "city": "...",
        "interest": "..."
      }}
    }}
    Do not include markdown wrappers (like ```json). Just return the raw JSON string.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text_resp = response.text.strip()
        # Clean potential markdown block wrappers if model doesn't obey rules
        if text_resp.startswith("```"):
            lines = text_resp.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text_resp = "\n".join(lines).strip()
            
        return json.loads(text_resp)
    except Exception as e:
        print("Summary extraction error:", e)
        return {
            "customer_name": "Unknown",
            "intent": "Unknown",
            "outcome": "Error generating summary",
            "sentiment": "Neutral",
            "summary": "Error generating summary",
            "lead": {"name": "Unknown", "phone": "Unknown", "city": "Unknown", "interest": "Unknown"}
        }