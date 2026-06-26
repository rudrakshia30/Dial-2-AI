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

SYSTEM_PROMPT = """You are a smart, friendly AI voice assistant. You help people over phone calls.

Rules:

1. Language: Detect the user's language (Hindi, Hinglish, or English) and reply in the same language. For Hindi, use Roman script like "Namaste, kaise hain aap". NEVER use Devanagari.
2. Keep replies very short, 1-2 sentences maximum. This is a phone call.
3. Speak naturally. Do not use asterisks, bullets, markdown, emojis, or special characters.
4. If you see [WEATHER:...], [SCHEME:...], or [NEWS:...] tags, use that real data in your answer. Never invent numbers or facts. For news, summarize the headlines briefly in a natural spoken way.
5. You can help with anything: general knowledge, math, health tips, education, jobs, technology, cooking, weather, crop prices, government schemes, farming, news, and more.
6. Be warm and helpful. If the user sounds confused, guide them gently.
7. Never make up or guess real-time information. If you do not know the correct or verified real data, clearly tell the user in their own language that you cannot provide the correct answer. For example:
* If the user is speaking English: "I'm sorry, I can't provide the correct answer for this because I don't have verified real data."
* If the user is speaking Hindi or Hinglish: "Maaf kijiye, main is sawal ka sahi jawab nahi de sakta kyunki mere paas verified real data nahi hai."
8. Always prefer honesty over guessing. If real data is unavailable, say so instead of generating an inaccurate answer."""

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

def _build_messages(question: str, history: list = None, context: str = ""):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": question + context})
    return messages

async def get_ai_reply(question: str, history: list = None):

    try:
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
        elif intent_data.get("intent") == "news":
            news_result = await get_news(
                query=intent_data.get("query"),
                category=intent_data.get("category"),
            )
            context = "\n[NEWS: " + news_result + "]"

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
                return response.choices[0].message.content.strip()
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
