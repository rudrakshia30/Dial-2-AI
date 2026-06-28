import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL ="llama-3.1-8b-instant"


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

import json
import re
from .data_fetch import get_weather, get_mandi_price, get_govt_scheme, get_news
from app.services.india_officials import get_official_fact_context
from app.services.language_filter import user_wants_devanagari
from app.services.repeat_intent import detect_language

SYSTEM_PROMPT = """You are a smart AI voice assistant on a live phone call. The caller already heard a Namaste welcome greeting before asking any question.

Rules:

1. Language: Reply in EXACTLY the same language as the user's latest question.
   - English question -> English answer only.
   - Hindi question -> natural Roman Hindi answer (unless the user explicitly asked for Devanagari).
   - Hinglish question -> Hinglish Roman script only.
   - Do NOT switch language unless the user switches first.
   - Never discuss language rules or script preferences. Just answer the question.
2. Direct answers only: give the fact or solution immediately. Do NOT use filler phrases like "aapke jawab mein", "main aapko batata hoon", "aapke sawal ka jawab hai", "sure", or "of course".
3. Never greet again: do NOT say Namaste, Hello, Hi, or Namaskar in your answers. Greeting happens once at call start only.
4. Keep replies very short, 1-2 sentences maximum. This is a phone call.
5. Speak naturally. Do not use asterisks, bullets, markdown, emojis, or special characters.
6. If you see [WEATHER:...], [SCHEME:...], [NEWS:...], [MANDI:...], or [FACT:...] tags, use that exact verified data in your answer. Never invent numbers, names, or facts.
7. You can help with general knowledge, math, health, education, jobs, technology, cooking, weather, crop prices, government schemes, farming, news, and more.
8. Never make up real-time information. If verified data is unavailable, say so briefly in the user's language.
9. Always prefer honesty over guessing."""

_LANGUAGE_HINTS = {
    "english": "Reply in English only. No Hindi words. No greeting. Direct answer.",
    "hindi": "Reply in natural Roman Hindi only. No Devanagari. No greeting. Direct answer.",
    "hinglish": "Reply in Hinglish Roman script only. No greeting. Direct answer.",
}

_GREETING_PREFIX_RE = re.compile(
    r"^(?:namaste|namaskar|hello|hi|hey|good morning|good evening)[!,.\s]+",
    re.IGNORECASE,
)

_FILLER_PHRASE_RES = [
    re.compile(r"^aapke jawab mein[,\s]*", re.IGNORECASE),
    re.compile(r"^aapke sawal ka jawab hai[,\s]*", re.IGNORECASE),
    re.compile(r"^aapke prashn ka jawab hai[,\s]*", re.IGNORECASE),
    re.compile(r"^main aapko batata hoon[,\s]*", re.IGNORECASE),
    re.compile(r"^main aapko bata deta hoon[,\s]*", re.IGNORECASE),
    re.compile(r"^main aapko bata deti hoon[,\s]*", re.IGNORECASE),
    re.compile(r"^sure[,.\s]+", re.IGNORECASE),
    re.compile(r"^of course[,.\s]+", re.IGNORECASE),
    re.compile(r"^ji[,.\s]+", re.IGNORECASE),
    re.compile(r"^main samajh(?:ta|ti)? hoon[,\s]*", re.IGNORECASE),
    re.compile(r"^it seems you want[,\s]*", re.IGNORECASE),
]

# --- Keyword-based intent detection (saves 1 API call per message) ---
WEATHER_KEYWORDS = [
    "weather", "mausam", "temperature", "barish", "rain", "thand", "garmi", "dhoop", "toofan", "storm", "humidity", "hawa",
    # Devanagari
    "मौसम", "तापमान", "टेंपरेचर", "बारिश", "बरसात", "ठंड", "गर्मी", "धूप", "तूफान", "हवा", "नमी",
]
SCHEME_KEYWORDS = [
    "yojana", "scheme", "pm kisan", "ayushman", "fasal bima", "kcc", "credit card", "pmay", "awas", "mnrega", "nrega", "rojgar", "sinchai", "irrigation", "soil health", "enam",
    # Devanagari
    "योजना", "स्कीम", "किसान", "आयुष्मान", "फसल बीमा", "आवास", "रोजगार", "सिंचाई", "मनरेगा",
]
NEWS_KEYWORDS = [
    "news", "khabar", "headlines", "headline", "samachar", "taza khabar", "latest news", "top news",
    "current news", "aaj ki khabar", "aaj ka news", "india news", "world news",
    # Devanagari
    "खबर", "समाचार", "ताजा खबर", "हेडलाइन", "न्यूज़", "न्यूज",
]
NEWS_CATEGORY_MAP = {
    "sports": "sports", "khel": "sports", "cricket": "sports", "football": "sports",
    "खेल": "sports", "क्रिकेट": "sports",
    "technology": "technology", "tech": "technology", "teknoloji": "technology",
    "तकनीक": "technology", "टेक्नोलॉजी": "technology",
    "business": "business", "vyapar": "business", "market": "business", "bazaar": "business",
    "व्यापार": "business", "बाज़ार": "business", "बिजनेस": "business",
    "entertainment": "entertainment", "manoranjan": "entertainment", "bollywood": "entertainment",
    "मनोरंजन": "entertainment", "बॉलीवुड": "entertainment",
    "science": "science", "vigyan": "science", "विज्ञान": "science",
    "health": "health", "swasthya": "health", "sehat": "health",
    "स्वास्थ्य": "health", "सेहत": "health",
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

MANDI_KEYWORDS = [
    "mandi", "price", "rate", "daam", "bhav", "bhaav", "modal", "quintal",
    # Devanagari
    "मंडी", "दाम", "भाव", "रेट", "कीमत", "प्रति क्विंटल",
]

CROP_MAP = {
    "arhar": "Arhar", "tur": "Arhar", "tuar": "Arhar", "pigeon pea": "Arhar",
    "अरहर": "Arhar", "तुअर": "Arhar", "तूर": "Arhar",
    "urad": "Urad", "black gram": "Urad", "urad dal": "Urad",
    "उड़द": "Urad", "उरद": "Urad",
    "moong": "Moong", "green gram": "Moong", "moong dal": "Moong",
    "मूंग": "Moong", "मूँग": "Moong",
    "potato": "Potato", "aloo": "Potato", "alu": "Potato",
    "आलू": "Potato",
    "onion": "Onion", "pyaz": "Onion", "pyaaz": "Onion",
    "प्याज": "Onion", "प्याज़": "Onion",
    "tomato": "Tomato", "tamatar": "Tomato",
    "टमाटर": "Tomato",
    "wheat": "Wheat", "gehun": "Wheat", "gehoon": "Wheat",
    "गेहूं": "Wheat", "गेहूँ": "Wheat",
    "chana": "Chana", "gram": "Chana", "chickpea": "Chana",
    "चना": "Chana",
    "rice": "Rice", "chawal": "Rice",
    "चावल": "Rice",
    "paddy": "Paddy(Dhan)", "dhan": "Paddy(Dhan)",
    "धान": "Paddy(Dhan)",
}

STATE_MAP = {
    "rajasthan": "Rajasthan", "राजस्थान": "Rajasthan",
    "andhra pradesh": "Andhra Pradesh", "andhra": "Andhra Pradesh", "आंध्र प्रदेश": "Andhra Pradesh", "आंध्र": "Andhra Pradesh",
    "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "तमिलनाडु": "Tamil Nadu",
    "bihar": "Bihar", "बिहार": "Bihar",
    "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh", "उत्तर प्रदेश": "Uttar Pradesh", "यूपी": "Uttar Pradesh",
    "jharkhand": "Jharkhand", "झारखंड": "Jharkhand", "झारखण्ड": "Jharkhand",
    "karnataka": "Karnataka", "कर्नाटक": "Karnataka",
    "gujarat": "Gujarat", "गुजरात": "Gujarat",
    "chhattisgarh": "Chhattisgarh", "chhatisgarh": "Chhattisgarh", "छत्तीसगढ़": "Chhattisgarh", "छत्तीसगढ़": "Chhattisgarh",
    "odisha": "Odisha", "orissa": "Odisha", "ओडिशा": "Odisha", "उड़ीसा": "Odisha",
    "west bengal": "West Bengal", "bengal": "West Bengal", "paschim bengal": "West Bengal", "पश्चिम बंगाल": "West Bengal", "बंगाल": "West Bengal",
    "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh", "मध्य प्रदेश": "Madhya Pradesh", "एमपी": "Madhya Pradesh",
    "maharashtra": "Maharashtra", "mh": "Maharashtra", "महाराष्ट्र": "Maharashtra",
    "telangana": "Telangana", "तेलंगाना": "Telangana",
}

def _extract_state(text: str) -> str | None:
    lowered = text.lower()
    for state_kw, canonical in STATE_MAP.items():
        if state_kw in lowered or state_kw in text:
            return canonical
    return None

def _detect_intent(question: str):
    q = question.lower()
    # Check weather (works for both Roman and Devanagari)
    if any(w in q or w in question for w in WEATHER_KEYWORDS):
        loc = _extract_location(question)
        if loc:
            return {"intent": "weather", "location": loc}
    # Check scheme
    if any(w in q or w in question for w in SCHEME_KEYWORDS):
        return {"intent": "scheme"}
    # Check news
    if any(w in q or w in question for w in NEWS_KEYWORDS):
        # Detect category from the question
        detected_category = None
        for keyword, cat in NEWS_CATEGORY_MAP.items():
            if keyword in q or keyword in question:
                detected_category = cat
                break
        # Try to extract a search query (e.g. "modi news" -> query="modi")
        search_query = None
        if not detected_category:
            # Remove common news keywords to isolate the topic
            topic = q
            for nk in NEWS_KEYWORDS:
                topic = topic.replace(nk, "")
            topic = topic.strip(" ?.,!")
            if len(topic) >= 3:
                search_query = topic
        return {"intent": "news", "category": detected_category, "query": search_query}

    # Check mandi/crop price
    detected_crop = None
    for crop_kw, canonical in CROP_MAP.items():
        if crop_kw in q or crop_kw in question:
            detected_crop = canonical
            break

    is_mandi_query = any(w in q or w in question for w in MANDI_KEYWORDS)
    if is_mandi_query or detected_crop:
        # For mandi queries, try state extraction first (e.g. "Maharashtra mein")
        loc = _extract_state(question)
        # Fall back to location extractor only if state wasn't found
        if not loc:
            loc = _extract_location(question)
            # Discard if the "location" is actually the crop name
            if loc and detected_crop and loc.lower() == detected_crop.lower():
                loc = None
        return {"intent": "mandi", "crop": detected_crop, "location": loc}

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
            skip = {"Kya", "Aaj", "Kal", "Mujhe", "Bhai", "Batao", "Please", "Sir", "Madam",
                    "Mausam", "Weather", "Price", "Rate", "Daam", "How", "What", "Tell",
                    "Kaisa", "Kaise",
                    # Crop names — prevent them being matched as locations
                    "Arhar", "Urad", "Moong", "Potato", "Onion", "Tomato", "Wheat",
                    "Chana", "Rice", "Paddy"}
            if loc not in skip:
                return loc
    return None

def _sanitize_reply(reply: str) -> str:
    """Strip greetings and filler the model sometimes adds despite instructions."""
    text = (reply or "").strip()
    if not text:
        return text

    text = _GREETING_PREFIX_RE.sub("", text).strip()
    for pattern in _FILLER_PHRASE_RES:
        text = pattern.sub("", text).strip()

    # Remove mid-sentence filler like ", aapke jawab mein,"
    text = re.sub(r",?\s*aapke jawab mein,?\s*", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _language_hint_for_question(question: str, response_language: str | None = None) -> str:
    if user_wants_devanagari(question):
        return "Reply in Devanagari Hindi only. No greeting. Direct answer."
    lang = response_language or detect_language(question)
    if re.search(r"[\u0900-\u097F]", question) and lang == "hindi":
        return _LANGUAGE_HINTS["hindi"]
    return _LANGUAGE_HINTS.get(lang, _LANGUAGE_HINTS["hinglish"])


def _direct_official_answer(question: str, response_language: str | None = None) -> str | None:
    """Guaranteed correct short answers for India PM/President — no LLM hallucination."""
    from app.services.india_officials import detect_india_official

    official = detect_india_official(question)
    if not official:
        return None

    lang = response_language or detect_language(question)
    if official == "president":
        if lang == "english":
            return "Droupadi Murmu is the President of India."
        return "Droupadi Murmu Bharat ki rashtrapati hain."
    if official == "pm":
        if lang == "english":
            return "Narendra Modi is the Prime Minister of India."
        return "Narendra Modi Bharat ke pradhan mantri hain."
    return None


def _build_messages(question: str, history: list = None, context: str = ""):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": question + context})
    return messages

async def get_ai_reply(
    question: str,
    history: list = None,
    response_language: str | None = None,
):

    try:
        lang_hint = _language_hint_for_question(question, response_language)

        direct = _direct_official_answer(question, response_language)
        if direct:
            return direct

        # --- Keyword-based live data injection (NO extra API call) ---
        intent_data = _detect_intent(question)

        context = f"\n[{lang_hint}]"
        context += get_official_fact_context(question)
        if intent_data.get("intent") == "weather" and intent_data.get("location"):
            context += "\n[WEATHER: " + await get_weather(intent_data["location"]) + "]"
        elif intent_data.get("intent") == "mandi" and intent_data.get("crop"):
            loc = intent_data.get("location") or ""
            context += "\n[MANDI: " + await get_mandi_price(intent_data["crop"], loc) + "]"
        elif intent_data.get("intent") == "scheme":
            context += "\n[SCHEME: " + await get_govt_scheme(question) + "]"
        elif intent_data.get("intent") == "news":
            news_result = await get_news(
                query=intent_data.get("query"),
                category=intent_data.get("category"),
            )
            context += "\n[NEWS: " + news_result + "]"

        messages = _build_messages(question, history, context)

        # Retry up to 2 times for rate-limit errors
        last_err = None
        for attempt in range(3):
            try:
                response = _get_client().chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    max_tokens=150,
                )
                raw = response.choices[0].message.content.strip()
                return _sanitize_reply(raw)
            except Exception as api_err:
                last_err = api_err
                print(f"Grok API attempt {attempt+1} failed: {repr(api_err)}")
                if attempt < 2:
                    import asyncio
                    await asyncio.sleep(2)

        print("Grok Error (all retries failed):", repr(last_err))
        return "Maaf kijiye, thodi der mein dobara try karein."

    except Exception as e:
        print("Grok Error (outer):", repr(e))
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
        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text_resp = response.choices[0].message.content.strip()
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
