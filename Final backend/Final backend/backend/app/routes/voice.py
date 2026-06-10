from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.services.stt import transcribe_audio
from app.services.llm import get_ai_reply
from app.services.data_fetch import get_mandi_price, get_weather, get_govt_scheme
from app.utils.db import insert_log
from dotenv import load_dotenv
from html import escape
import os

load_dotenv()

router = APIRouter()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.api_route("/voice/incoming", methods=["GET", "POST"])
@router.api_route("/voice/start", methods=["GET", "POST"])
async def start(request: Request):
    if request.method == "POST":
        form = await request.form()
        params = {**dict(request.query_params), **dict(form)}
    else:
        params = dict(request.query_params)

    print("[/voice/start] params:", dict(params))
    print("[/voice/start] Direct call - greeting + record")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Namaste! Main aapka AI assistant hoon. Aap apna sawaal boliye. Beep ke baad bolein aur hash key dabakar khatam karein.</Say>
    <Record action="{BASE_URL}/voice/question" method="POST" maxLength="60" finishOnKey="#" playBeep="true" timeout="10"/>
</Response>"""

    return Response(content=xml, media_type="application/xml")


@router.api_route("/voice/question", methods=["GET", "POST"])
async def question(request: Request):
    if request.method == "POST":
        form = await request.form()
        params = {**dict(request.query_params), **dict(form)}
    else:
        params = dict(request.query_params)

    print("[/voice/question] params:", dict(params))

    audio_url = (
        params.get("RecordingUrl")
        or params.get("recording_url")
        or params.get("recordingurl")
        or ""
    )
    caller_number = params.get("CallFrom", params.get("From", "unknown"))
    transcript = ""
    intent_data = {}
    reply = "Kripya dobara boliye."

    print(f"audio_url={audio_url} caller={caller_number}")

    if audio_url:
        transcript = await transcribe_audio(audio_url)
        print("Transcript:", transcript)
        print("TRANSCRIPT RECEIVED =", transcript)
    else:
        print("WARNING: No recording URL found in params:", params)

    if transcript:
        reply = await get_ai_reply(transcript)

        intent_data = {
            "intent": "general",
            "crop": "",
            "location": ""
        }
        exit_words = [
    "nahi",
    "nahin",
    "bye",
    "thank you",
    "band karo"
]

        if transcript.lower().strip() in exit_words:

            xml = """
        <Response>
            <Say>Dhanyavaad. Phir milenge.</Say>
            <Hangup/>
        </Response>
        """

            return Response(
                content=xml,
                media_type="application/xml"
            )

    print("AI REPLY =", reply)

    insert_log(
        phone_number=caller_number,
        transcript=transcript,
        intent=intent_data.get("intent", "unknown"),
        crop=intent_data.get("crop", ""),
        location=intent_data.get("location", ""),
        response=reply,
        status="success" if transcript else "failed",
        duration=0,
    )

    safe_reply = escape(reply, quote=False)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{safe_reply}. Kya aapka koi aur sawaal hai?</Say>
    <Record action="{BASE_URL}/voice/question" method="POST" maxLength="60" finishOnKey="#" playBeep="true" timeout="10"/>
</Response>"""

    print("Returning KooKoo XML:\n", xml)
    return Response(content=xml, media_type="application/xml")


@router.get("/api/stats")
async def api_stats():
    from app.utils.db import get_stats
    return get_stats()


@router.get("/api/logs")
async def api_logs():
    from app.utils.db import get_logs
    rows = get_logs()
    return [
        {
            "id": r[0],
            "phone_number": r[1],
            "timestamp": r[2],
            "transcript": r[3],
            "intent": r[4],
            "crop": r[5],
            "location": r[6],
            "response": r[7],
            "status": r[8],
            "duration": r[9],
            "summary_text": r[10] if len(r) > 10 else "",
            "sentiment": r[11] if len(r) > 11 else "",
            "customer_name": r[12] if len(r) > 12 else "",
            "outcome": r[13] if len(r) > 13 else "",
            "lead_json": r[14] if len(r) > 14 else "{}",
        }
        for r in rows
    ]
