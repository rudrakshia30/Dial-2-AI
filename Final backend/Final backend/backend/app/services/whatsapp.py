import os
import asyncio
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

async def send_whatsapp_transcript(phone: str, conversation_history: list, summary_text: str = None) -> bool:
    """
    Formulate call summary and full transcript, and send it to the user's WhatsApp via Twilio.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    if not account_sid or not auth_token or not from_number:
        print("[WhatsApp] ERROR: Twilio credentials missing in environment.")
        return False

    if not phone or phone == "unknown" or phone == "streaming_caller":
        print("[WhatsApp] ERROR: Invalid phone number.")
        return False

    # Standardize recipient phone format (ensure it starts with whatsapp:)
    to_whatsapp = phone
    if not to_whatsapp.startswith("whatsapp:"):
        digits = "".join(filter(str.isdigit, to_whatsapp))
        if not to_whatsapp.startswith("+"):
            if len(digits) == 10:
                to_whatsapp = f"+91{digits}"
            elif len(digits) == 12 and digits.startswith("91"):
                to_whatsapp = f"+{digits}"
            else:
                to_whatsapp = f"+{digits}"
        to_whatsapp = f"whatsapp:{to_whatsapp}"

    # Standardize sender phone format
    from_whatsapp = from_number
    if not from_whatsapp.startswith("whatsapp:"):
        if not from_whatsapp.startswith("+"):
            from_whatsapp = f"+{from_whatsapp}"
        from_whatsapp = f"whatsapp:{from_whatsapp}"

    # Build the message content
    lines = ["📞 *Dial2AI Call Report* 📞\n"]
    
    if summary_text and summary_text != "No summary generated.":
        lines.append(f"📝 *Summary:*\n{summary_text}\n")
        
    if conversation_history:
        lines.append("💬 *Transcript:*")
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                lines.append(f"👤 *You:* {content}")
            elif role == "assistant":
                lines.append(f"🤖 *AI:* {content}")
            else:
                lines.append(f"❓ *{role.capitalize()}:* {content}")
                
    message_body = "\n".join(lines)
    
    # Twilio message size limit is 4096 characters for WhatsApp.
    if len(message_body) > 4000:
        message_body = message_body[:3997] + "..."

    print(f"\n[WhatsApp] Sending message to: {to_whatsapp}")
    print(f"[WhatsApp] Sending from: {from_whatsapp}")
    print(f"[WhatsApp] Body size: {len(message_body)} characters")
    
    try:
        client = Client(account_sid, auth_token)
        
        def _send():
            return client.messages.create(
                body=message_body,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            
        message = await asyncio.to_thread(_send)
        print(f"[WhatsApp] SUCCESS! Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[WhatsApp] ERROR sending message: {e}")
        return False
