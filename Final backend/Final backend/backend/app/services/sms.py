# import os
# import httpx
# from dotenv import load_dotenv

# load_dotenv()

# EXOTEL_SID = os.getenv("EXOTEL_SID")
# EXOTEL_API_KEY = os.getenv("EXOTEL_API_KEY")
# EXOTEL_API_TOKEN = os.getenv("EXOTEL_API_TOKEN")
# EXOTEL_NUMBER = os.getenv("EXOTEL_NUMBER")


# async def send_sms(to_phone: str, message: str):
#     """Send SMS to a phone number via Exotel SMS API."""
#     print(f"\n{'='*40}")
#     print(f"[SMS] Sending to: {to_phone}")
#     print(f"[SMS] Body length: {len(message)} chars")
#     print(f"[SMS] Body: {message[:200]}...")
#     print(f"{'='*40}\n")

#     if not EXOTEL_SID or not EXOTEL_API_KEY or not EXOTEL_API_TOKEN:
#         print("[SMS] ERROR: Credentials missing!")
#         print(f"  EXOTEL_SID: {'SET' if EXOTEL_SID else 'MISSING'}")
#         print(f"  EXOTEL_API_KEY: {'SET' if EXOTEL_API_KEY else 'MISSING'}")
#         print(f"  EXOTEL_API_TOKEN: {'SET' if EXOTEL_API_TOKEN else 'MISSING'}")
#         return False

#     if not to_phone or to_phone == "unknown":
#         print("[SMS] ERROR: No valid phone number to send to.")
#         return False

#     # Try multiple Exotel API URL formats (including India region subdomain api.in.exotel.com)
#     urls = [
#         f"https://{EXOTEL_API_KEY}:{EXOTEL_API_TOKEN}@api.in.exotel.com/v1/Accounts/{EXOTEL_SID}/Sms/send.json",
#         f"https://{EXOTEL_API_KEY}:{EXOTEL_API_TOKEN}@api.exotel.com/v1/Accounts/{EXOTEL_SID}/Sms/send.json",
#         f"https://api.in.exotel.com/v1/Accounts/{EXOTEL_SID}/Sms/send.json",
#         f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Sms/send.json",
#     ]

#     for url in urls:
#         try:
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 # Use basic auth
#                 auth = (EXOTEL_API_KEY, EXOTEL_API_TOKEN)
#                 data = {
#                     "From": EXOTEL_NUMBER,
#                     "To": to_phone,
#                     "Body": message[:160],  # SMS limit
#                 }
                
#                 print(f"[SMS] Trying: POST {url.split('@')[-1] if '@' in url else url}")
#                 print(f"[SMS] Data: From={EXOTEL_NUMBER}, To={to_phone}")

#                 # First URL has auth embedded, second needs explicit auth
#                 if "@" in url:
#                     response = await client.post(url, data=data)
#                 else:
#                     response = await client.post(url, data=data, auth=auth)

#                 print(f"[SMS] Response status: {response.status_code}")
#                 print(f"[SMS] Response body: {response.text[:500]}")

#                 if response.status_code in (200, 201, 202):
#                     print("[SMS] SUCCESS! SMS sent via Exotel.")
#                     return True
#                 else:
#                     print(f"[SMS] Failed with this URL, trying next...")
#                     continue

#         except Exception as e:
#             print(f"[SMS] Error with this URL: {e}")
#             continue

#     print("[SMS] All API attempts failed. SMS was NOT sent.")
#     return False


# def format_sms_history(history: list) -> str:
#     """Format conversation history into a short SMS-friendly string."""
#     if not history:
#         return "Dhanyavaad! AI Without Internet se baat karne ke liye."

#     lines = ["AI Without Internet - Call Summary:"]
#     for msg in history:
#         role = "You" if msg["role"] == "user" else "AI"
#         lines.append(f"{role}: {msg['content']}")

#     body = "\n".join(lines)
#     # SMS max length ~160 chars for single SMS, 
#     # but we truncate to fit within reasonable limits
#     if len(body) > 150:
#         body = body[:147] + "..."
#     return body
import os
import httpx


async def send_sms(phone, message):
    """Send SMS via Exotel SMS API (async)."""
    if not phone or phone == "unknown":
        print("[SMS] No valid phone number. Skipping.")
        return False

    sid = os.getenv("EXOTEL_SID")
    api_key = os.getenv("EXOTEL_API_KEY")
    api_token = os.getenv("EXOTEL_API_TOKEN")
    from_number = os.getenv("EXOTEL_NUMBER") or os.getenv("EXOTEL_SMS_NUMBER")

    if not sid or not api_key or not api_token:
        print("[SMS] ERROR: Exotel credentials missing!")
        return False

    url = f"https://api.exotel.com/v1/Accounts/{sid}/Sms/send"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                data={
                    "From": from_number,
                    "To": phone,
                    "Body": message[:160]
                },
                auth=(api_key, api_token)
            )
            print(f"[SMS] Response: {response.status_code} — {response.text[:200]}")
            return response.status_code in (200, 201, 202)
    except Exception as e:
        print(f"[SMS] Error: {e}")
        return False