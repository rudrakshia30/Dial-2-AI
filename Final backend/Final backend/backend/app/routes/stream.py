from fastapi import APIRouter, WebSocket
import json
import base64
import time
import asyncio
import struct
import os

from app.services.audio_utils import raw_to_wav, contains_speech
from app.services.stt import transcribe_wav
from app.services.llm import get_ai_reply, generate_call_summary_and_lead
from app.services.tts import text_to_speech
from app.services.audio_convert import mp3_to_pcm
from app.services.correct_hindi_transcript import correct_hindi_transcript
from app.services.repeat_intent import (
    detect_language,
    get_no_repeat_answer_message,
    is_probably_repeat_request,
    is_repeat_request,
    should_cache_as_successful_answer,
)
from app.services.transcript_fix import get_repeat_user_log_text
from app.utils.db import insert_complete_call_log
from app.services.sms import send_sms

router = APIRouter()

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIO_WORK_DIR = os.path.join(_BACKEND_DIR, "audio_work")
os.makedirs(AUDIO_WORK_DIR, exist_ok=True)

# --- Hold music (interval) support ---
# Resolve interval.mp3 path relative to project root (two levels up from this file)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
INTERVAL_MP3 = os.path.join(_PROJECT_ROOT, "interval.mp3")
# Cache of converted PCM files keyed by sample_rate
_interval_pcm_cache: dict[int, str] = {}


def _get_interval_pcm(sample_rate: int = 8000) -> str:
    """Return the path to interval.pcm for the given sample rate, converting once."""
    if sample_rate in _interval_pcm_cache:
        return _interval_pcm_cache[sample_rate]
    pcm_path = os.path.join(os.path.dirname(INTERVAL_MP3), f"interval_{sample_rate}.pcm")
    if not os.path.exists(pcm_path):
        print(f"Converting interval.mp3 -> {pcm_path} at {sample_rate} Hz ...")
        mp3_to_pcm(INTERVAL_MP3, pcm_path, sample_rate=sample_rate)
    _interval_pcm_cache[sample_rate] = pcm_path
    return pcm_path


async def send_hold_music_loop(websocket, stream_sid, sample_rate=8000):
    """Stream interval PCM audio in a loop until this task is cancelled.

    The audio is sent in small chunks with pacing so Exotel can play it
    in real-time.  When the caller's AI reply is ready the parent code
    cancels this task which stops the music immediately.
    """
    try:
        pcm_path = _get_interval_pcm(sample_rate)
    except Exception as e:
        print(f"Hold music unavailable: {e}")
        return

    chunk_duration = 0.1  # 100 ms
    chunk_samples = int(sample_rate * chunk_duration)
    chunk_bytes = chunk_samples * 2  # 16-bit PCM = 2 bytes/sample

    try:
        # Read entire file into memory once (avoids repeated I/O)
        with open(pcm_path, "rb") as f:
            pcm_data = f.read()

        print("🎵 Hold music started")
        while True:  # loop until cancelled
            offset = 0
            while offset < len(pcm_data):
                chunk = pcm_data[offset:offset + chunk_bytes]
                offset += chunk_bytes
                payload = base64.b64encode(chunk).decode()
                try:
                    await websocket.send_json({
                        "event": "media",
                        "stream_sid": stream_sid,
                        "media": {"payload": payload}
                    })
                except Exception:
                    return  # WebSocket closed
                await asyncio.sleep(chunk_duration * 0.8)  # pace close to real-time
            # Small pause before looping the track again
            await asyncio.sleep(0.02)
    except asyncio.CancelledError:
        # Send a clear event so Exotel flushes any buffered hold music
        try:
            await websocket.send_json({"event": "clear", "stream_sid": stream_sid})
        except Exception:
            pass
        print("🎵 Hold music stopped")
        raise  # re-raise so the task registers as cancelled


async def send_pcm_audio(
    websocket,
    pcm_path,
    stream_sid,
    sample_rate=8000
):
    chunk_duration = 0.1  # 100ms chunks
    chunk_samples = int(sample_rate * chunk_duration)
    chunk_bytes = chunk_samples * 2  # 16-bit is 2 bytes per sample
    total_sent = 0

    with open(pcm_path, "rb") as f:
        while True:
            chunk = f.read(chunk_bytes)
            if not chunk:
                break
            total_sent += len(chunk)

            payload = base64.b64encode(chunk).decode()

            try:
                await websocket.send_json(
                    {
                        "event": "media",
                        "stream_sid": stream_sid,
                        "media": {
                            "payload": payload
                        }
                    }
                )
            except Exception as e:
                print("SEND ERROR:", repr(e))
                break

            await asyncio.sleep(0.01)
    print(f"Total PCM bytes sent: {total_sent}")


async def send_pcm_bytes(
    websocket,
    pcm_data: bytes,
    stream_sid,
    sample_rate=8000,
):
    chunk_duration = 0.1
    chunk_samples = int(sample_rate * chunk_duration)
    chunk_bytes = chunk_samples * 2
    total_sent = 0
    offset = 0

    while offset < len(pcm_data):
        chunk = pcm_data[offset:offset + chunk_bytes]
        offset += chunk_bytes
        total_sent += len(chunk)
        payload = base64.b64encode(chunk).decode()

        try:
            await websocket.send_json(
                {
                    "event": "media",
                    "stream_sid": stream_sid,
                    "media": {"payload": payload},
                }
            )
        except Exception as e:
            print("SEND ERROR:", repr(e))
            break

        await asyncio.sleep(0.01)
    print(f"Total PCM bytes sent from cache: {total_sent}")


async def play_audio_and_wait(websocket, pcm_path, stream_sid, sample_rate=8000):
    """Send PCM audio and wait for it to finish playing on Exotel's end."""
    try:
        import os
        audio_size = os.path.getsize(pcm_path)
        bytes_per_sec = sample_rate * 2.0
        audio_duration = audio_size / bytes_per_sec
        print(f"Audio file: {audio_size} bytes, duration: {audio_duration:.2f}s (at {sample_rate} Hz)")

        await send_pcm_audio(websocket, pcm_path, stream_sid, sample_rate=sample_rate)

        # Wait for Exotel to actually finish playing the audio on the phone
        wait_time = audio_duration + 1.5
        print(f"Waiting {wait_time:.1f}s for Exotel to finish playing...")
        await asyncio.sleep(wait_time)
        print("Playback complete. Ready for next question.")

    except asyncio.CancelledError:
        print("Playback cancelled due to barge-in.")
        try:
            await websocket.send_json({
                "event": "clear",
                "stream_sid": stream_sid
            })
        except Exception as e:
            print("Failed to send clear event:", e)
        raise
    except Exception as e:
        print("Playback error:", e)


async def play_audio_bytes_and_wait(
    websocket,
    pcm_data: bytes,
    stream_sid,
    sample_rate=8000,
):
    """Send in-memory PCM and wait for Exotel playback to finish."""
    try:
        audio_size = len(pcm_data)
        bytes_per_sec = sample_rate * 2.0
        audio_duration = audio_size / bytes_per_sec
        print(
            f"Cached audio: {audio_size} bytes, duration: {audio_duration:.2f}s "
            f"(at {sample_rate} Hz)"
        )

        await send_pcm_bytes(websocket, pcm_data, stream_sid, sample_rate=sample_rate)

        wait_time = audio_duration + 1.5
        print(f"Waiting {wait_time:.1f}s for Exotel to finish playing cached audio...")
        await asyncio.sleep(wait_time)
        print("Cached playback complete. Ready for next question.")

    except asyncio.CancelledError:
        print("Cached playback cancelled due to barge-in.")
        try:
            await websocket.send_json({"event": "clear", "stream_sid": stream_sid})
        except Exception as e:
            print("Failed to send clear event:", e)
        raise
    except Exception as e:
        print("Cached playback error:", e)


def get_avg_amplitude(chunk: bytes) -> float:
    if not chunk:
        return 0.0
    count = len(chunk) // 2
    if count == 0:
        return 0.0
    try:
        shorts = struct.unpack(f"<{count}h", chunk[:count * 2])
        return sum(abs(s) for s in shorts) / count
    except Exception as e:
        print("Amplitude calculation error:", e)
        return 0.0


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    # Log all query params to help debug Exotel phone parameter keys
    query_params = dict(websocket.query_params)
    print("==========")
    print("EXOTEL WS CONNECTION ACCEPTED")
    print("WebSocket Query Params:", query_params)
    print("==========")

    # Negotiate sample rate (default to 8000 Hz for Exotel streams)
    sample_rate_str = query_params.get("sample-rate") or query_params.get("sample_rate") or query_params.get("sampleRate")
    sample_rate = int(sample_rate_str) if (sample_rate_str and sample_rate_str.isdigit()) else 8000
    bytes_per_sec = sample_rate * 2.0
    print(f"Negotiated sample rate: {sample_rate} Hz ({bytes_per_sec} bytes/sec)")

    # Retrieve caller phone number from query params
    caller_number = (
        query_params.get("From") or 
        query_params.get("from") or 
        query_params.get("CallFrom") or 
        query_params.get("phone_number") or
        query_params.get("caller_id") or
        query_params.get("caller")
    )

    audio_buffer = bytearray()
    stream_sid = None
    conversation_history = []
    caller_number = None
    
    # State tracking for silence detection
    has_spoken = False
    silence_seconds = 0.0
    initial_silence_seconds = 0.0
    conversation_history = []  # Session memory
    
    playback_task = None
    playback_start_time = None
    hold_music_task = None  # Track hold music task separately
    call_start_time = time.time()
    last_successful_answer = None  # Per-session cache: text, language, pcm_bytes
    greeting_started = False
    greeting_finished = False

    async def play_welcome_greeting():
        nonlocal greeting_finished, playback_start_time
        try:
            welcome_text = "Namaste! Main aapka AI assistant hoon. Aap apna sawaal boliye."
            welcome_mp3 = os.path.join(AUDIO_WORK_DIR, "welcome.mp3")
            welcome_pcm = os.path.join(AUDIO_WORK_DIR, "welcome.pcm")
            mp3_file = await asyncio.to_thread(
                text_to_speech, welcome_text, welcome_mp3
            )
            pcm_file = await asyncio.to_thread(
                mp3_to_pcm, mp3_file, welcome_pcm, sample_rate=sample_rate
            )
            playback_start_time = time.time()
            await play_audio_and_wait(
                websocket, pcm_file, stream_sid, sample_rate=sample_rate
            )
            print("🎙️ Welcome greeting completed!")
        except Exception as e:
            print(f"Welcome greeting error: {e}")
        finally:
            greeting_finished = True

    def ensure_welcome_started():
        nonlocal greeting_started, greeting_finished
        if greeting_started or not stream_sid:
            return
        greeting_started = True
        greeting_finished = False
        asyncio.create_task(play_welcome_greeting())
        print("🎙️ Welcome greeting started!")

    try:

        while True:

            msg = await websocket.receive()

            if "text" not in msg:
                continue

            data = json.loads(msg["text"])

            event = data.get("event")
            if event == "start":
                start_meta = data.get("start", {})
                caller_number = start_meta.get("from") or start_meta.get("From")
                print("CALLER:", caller_number)
                stream_sid = data.get("stream_sid") or data.get("streamSid")
                print("MEDIA FORMAT:")
                print(start_meta.get("media_format", {}))
                print("STREAM SID:", stream_sid)
                print("Start Event Metadata:", start_meta)
                
                # Dynamically extract and update sample rate from start event metadata
                media_format = start_meta.get("media_format") or start_meta.get("mediaFormat") or {}
                evt_sample_rate_str = media_format.get("sample_rate") or media_format.get("sampleRate")
                if evt_sample_rate_str and str(evt_sample_rate_str).isdigit():
                    sample_rate = int(evt_sample_rate_str)
                    bytes_per_sec = sample_rate * 2.0
                    print(f"Dynamically updated sample rate from start event: {sample_rate} Hz ({bytes_per_sec} bytes/sec)")
                
                ensure_welcome_started()

                if not caller_number:
                    caller_number = (
                        start_meta.get("from") or 
                        start_meta.get("From") or
                        start_meta.get("customParameters", {}).get("From") or
                        start_meta.get("customParameters", {}).get("from")
                    )

            elif event == "media":
                if stream_sid is None:
                    stream_sid = data.get("stream_sid") or data.get("streamSid")
                ensure_welcome_started()
                if not greeting_finished:
                    continue
                if not caller_number:
                    start_meta = data.get("start", {})
                    caller_number = (
                        start_meta.get("from") or 
                        start_meta.get("From") or
                        start_meta.get("customParameters", {}).get("From") or
                        start_meta.get("customParameters", {}).get("from")
                    )

                payload = data["media"]["payload"]
                audio_chunk = base64.b64decode(payload)

                # Check if AI is currently speaking
                is_playing = (playback_task is not None and not playback_task.done())
                avg_amp = get_avg_amplitude(audio_chunk)

                SILENCE_THRESHOLD = 600.0
                BARGE_IN_THRESHOLD = 1800.0

                if is_playing:
                    time_since_playback = time.time() - playback_start_time if playback_start_time else 0.0
                    if time_since_playback > 1.2 and avg_amp > BARGE_IN_THRESHOLD:
                        print(f"BARGE-IN DETECTED! (Amp: {avg_amp:.1f} > {BARGE_IN_THRESHOLD}, Time: {time_since_playback:.2f}s) Cancelling AI playback...")
                        playback_task.cancel()
                        playback_task = None
                        
                        # Reset states to capture user speech
                        audio_buffer.clear()
                        audio_buffer.extend(audio_chunk)
                        has_spoken = True
                        silence_seconds = 0.0
                        initial_silence_seconds = 0.0
                        continue
                    else:
                        # User is quiet or we are in the initial echo-guard window, ignore this inbound chunk
                        continue

                audio_buffer.extend(audio_chunk)
                chunk_duration = len(audio_chunk) / bytes_per_sec

                # Use our custom noise gate to filter Exotel static
                is_real_speech = contains_speech(audio_chunk, threshold=800)
                
                if avg_amp > SILENCE_THRESHOLD and is_real_speech:
                    if not has_spoken:
                        print("Speech detected! Recording...")
                        has_spoken = True
                    silence_seconds = 0.0
                else:
                    if has_spoken:
                        silence_seconds += chunk_duration
                    else:
                        initial_silence_seconds += chunk_duration

                total_duration = len(audio_buffer) / bytes_per_sec
                should_process = False
                reason = ""

                if has_spoken and silence_seconds >= 2.0:
                    should_process = True
                    reason = "2 seconds silence detected"
                elif not has_spoken and initial_silence_seconds >= 7.0:
                    should_process = True
                    reason = "7 seconds initial silence timeout"
                elif total_duration >= 30.0:
                    should_process = True
                    reason = "30 seconds max recording limit reached"

                if should_process:
                    print(f"\nProcessing audio: {reason} (total={total_duration:.2f}s)")

                    try:
                        # --- Start hold music while AI processes ---
                        if hold_music_task and not hold_music_task.done():
                            hold_music_task.cancel()
                        if stream_sid:
                            hold_music_task = asyncio.create_task(
                                send_hold_music_loop(
                                    websocket, stream_sid, sample_rate=sample_rate
                                )
                            )

                        # --- Run blocking I/O in threads so hold music keeps playing ---
                        def _save_raw():
                            raw_path = os.path.join(AUDIO_WORK_DIR, "call_audio.raw")
                            with open(raw_path, "wb") as f:
                                f.write(bytes(audio_buffer))
                            return raw_path
                        raw_path = await asyncio.to_thread(_save_raw)

                        wav_path = await asyncio.to_thread(
                            raw_to_wav,
                            raw_path,
                            os.path.join(AUDIO_WORK_DIR, "call_audio.wav"),
                            sample_rate
                        )

                        raw_text = await asyncio.to_thread(transcribe_wav, wav_path)
                        print(f"\nraw_transcript: {raw_text}")

                        correction = await correct_hindi_transcript(
                            raw_text, conversation_history
                        )
                        text = correction.corrected_transcript
                        print(f"corrected_transcript: {text}")
                        print(
                            f"detected_language: {correction.detected_language} "
                            f"(llm_correction={'yes' if correction.used_llm else 'no'})"
                        )

                        repeat_detected = is_probably_repeat_request(
                            raw_text,
                            audio_duration_sec=total_duration,
                            has_cached_answer=last_successful_answer is not None,
                        )
                        if not repeat_detected:
                            repeat_detected = is_probably_repeat_request(
                                text,
                                audio_duration_sec=total_duration,
                                has_cached_answer=last_successful_answer is not None,
                            )
                        if repeat_detected:
                            print(f"Repeat intent matched for STT text: '{text}'")
                        replay_cached_pcm = False
                        cached_pcm_bytes = None
                        pcm_file = None

                        if repeat_detected:
                            if last_successful_answer:
                                print(
                                    "Repeat intent detected — replaying cached response without LLM call."
                                )
                                reply = last_successful_answer["text"]
                                cached_pcm_bytes = last_successful_answer.get("pcm_bytes")
                                replay_cached_pcm = bool(cached_pcm_bytes)
                                user_log = get_repeat_user_log_text(raw_text)

                                conversation_history.append({"role": "user", "content": user_log})
                                conversation_history.append(
                                    {"role": "assistant", "content": reply}
                                )
                                if len(conversation_history) > 20:
                                    conversation_history = conversation_history[-20:]
                            else:
                                user_lang = detect_language(text)
                                reply = get_no_repeat_answer_message(user_lang)
                                print(
                                    "Repeat intent detected — no cached answer available for this session."
                                )
                                user_log = get_repeat_user_log_text(raw_text)

                                conversation_history.append({"role": "user", "content": user_log})
                                conversation_history.append(
                                    {"role": "assistant", "content": reply}
                                )
                                if len(conversation_history) > 20:
                                    conversation_history = conversation_history[-20:]
                        elif not text.strip():
                            reply = "Maaf kijiye, mujhe aapki aawaz nahi aayi. Kripya apna sawaal bolein."
                        elif correction.needs_clarification and correction.clarification_question:
                            reply = correction.clarification_question
                        else:
                            reply = await get_ai_reply(
                                text,
                                conversation_history,
                                response_language=correction.detected_language,
                            )

                            conversation_history.append(
                                {
                                    "role": "user",
                                    "content": text
                                }
                            )

                            conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": reply
                                }
                            )

                            if len(conversation_history) > 20:
                                conversation_history = conversation_history[-20:]

                        print(f"\nAI REPLY: {reply}")

                        if replay_cached_pcm:
                            print("Using cached PCM audio — skipping TTS API call.")
                        else:
                            if repeat_detected and last_successful_answer:
                                print(
                                    "Cached PCM unavailable — falling back to TTS with stored answer text."
                                )
                            mp3_file = await asyncio.to_thread(
                                text_to_speech,
                                reply,
                                os.path.join(AUDIO_WORK_DIR, "reply.mp3")
                            )

                            pcm_file = await asyncio.to_thread(
                                mp3_to_pcm,
                                mp3_file,
                                os.path.join(AUDIO_WORK_DIR, "reply.pcm"),
                                sample_rate
                            )

                            if should_cache_as_successful_answer(text, reply, repeat_detected):
                                def _read_pcm():
                                    with open(pcm_file, "rb") as pcm_f:
                                        return pcm_f.read()

                                pcm_cache_bytes = await asyncio.to_thread(_read_pcm)
                                answer_language = correction.detected_language or detect_language(text or reply)
                                last_successful_answer = {
                                    "text": reply,
                                    "language": answer_language,
                                    "pcm_bytes": pcm_cache_bytes,
                                }
                                print(
                                    f"Cached last successful answer for session "
                                    f"(language={answer_language}, "
                                    f"pcm_bytes={len(pcm_cache_bytes)})."
                                )

                        # --- Stop hold music NOW (AI reply is ready) ---
                        if hold_music_task and not hold_music_task.done():
                            hold_music_task.cancel()
                            try:
                                await hold_music_task
                            except asyncio.CancelledError:
                                pass
                            hold_music_task = None
                        # Brief pause to let Exotel flush the cleared buffer
                        await asyncio.sleep(0.15)

                        # Cancel any existing playback task just in case
                        if playback_task and not playback_task.done():
                            playback_task.cancel()

                        print("Starting background playback...")
                        playback_start_time = time.time()
                        if replay_cached_pcm:
                            playback_task = asyncio.create_task(
                                play_audio_bytes_and_wait(
                                    websocket,
                                    cached_pcm_bytes,
                                    stream_sid,
                                    sample_rate=sample_rate,
                                )
                            )
                        else:
                            playback_task = asyncio.create_task(
                                play_audio_and_wait(
                                    websocket,
                                    pcm_file,
                                    stream_sid,
                                    sample_rate=sample_rate,
                                )
                            )

                        # Reset states for the next turn
                        audio_buffer.clear()
                        has_spoken = False
                        silence_seconds = 0.0
                        initial_silence_seconds = 0.0

                    except Exception as turn_err:
                        print(f"Turn processing error (call continues): {turn_err}")
                        if hold_music_task and not hold_music_task.done():
                            hold_music_task.cancel()
                            try:
                                await hold_music_task
                            except asyncio.CancelledError:
                                pass
                            hold_music_task = None
                        audio_buffer.clear()
                        has_spoken = False
                        silence_seconds = 0.0
                        initial_silence_seconds = 0.0

            elif event == "stop":
                print("CALL ENDED BY USER")
                transcript = "\n".join(
                    [
                        f"{msg['role']}: {msg['content']}"
                        for msg in conversation_history
                    ]
                )

                print("\nTRANSCRIPT:")
                print(transcript)
                # SMS is handled in the 'finally' block with AI summary
                break

    except Exception as e:
        print("WS ERROR:", e)

    finally:
        print("WebSocket connection closing. Processing end of call analytics...")
        last_successful_answer = None
        print("Cleared session repeat-answer cache.")
        # Clean up hold music if still playing
        if hold_music_task and not hold_music_task.done():
            hold_music_task.cancel()
        if playback_task and not playback_task.done():
            playback_task.cancel()
            
        call_end_time = time.time()
        duration = int(call_end_time - call_start_time) if call_start_time else 0
        
        # Combine user messages for transcript
        user_texts = [msg["content"] for msg in conversation_history if msg["role"] == "user"]
        full_transcript = " | ".join(user_texts) if user_texts else ""
        
        last_reply = ""
        ai_replies = [msg["content"] for msg in conversation_history if msg["role"] == "assistant"]
        if ai_replies:
            last_reply = ai_replies[-1]
            
        phone_to_use = caller_number or "unknown"

        # Generate summary and leads
        analytics = None
        if conversation_history:
            print("Extracting summary & lead with AI...")
            analytics = await generate_call_summary_and_lead(conversation_history)
            
        # Fallback to extract phone from AI extracted lead details if not captured from WS headers
        if (not phone_to_use or phone_to_use == "unknown" or phone_to_use == "streaming_caller") and analytics:
            lead_phone = analytics.get("lead", {}).get("phone")
            if lead_phone and lead_phone != "Unknown" and lead_phone != "":
                clean_phone = "".join(filter(str.isdigit, lead_phone))
                if len(clean_phone) >= 10:
                    phone_to_use = clean_phone
                    print(f"Extracted caller phone number from conversation lead: {phone_to_use}")

        # Format number as E.164 (+91) for Indian numbers if it's 10 digits
        if phone_to_use and phone_to_use != "unknown":
            digits = "".join(filter(str.isdigit, phone_to_use))
            if len(digits) == 10:
                phone_to_use = "+91" + digits
            elif len(digits) == 12 and digits.startswith("91"):
                phone_to_use = "+" + digits

        if conversation_history:
            if analytics:
                summary_text = analytics.get("summary", "")
                sentiment = analytics.get("sentiment", "Neutral")
                cust_name = analytics.get("customer_name", "Unknown")
                intent = analytics.get("intent", "general")
                outcome = analytics.get("outcome", "")
                lead_json_str = json.dumps(analytics.get("lead", {}))
            else:
                summary_text = "No summary generated."
                sentiment = "Neutral"
                cust_name = "Unknown"
                intent = "general"
                outcome = ""
                lead_json_str = "{}"
                
            print(f"Saving complete call logs for phone: {phone_to_use}...")
            insert_complete_call_log(
                phone_number=phone_to_use,
                transcript=full_transcript,
                intent=intent,
                crop="",
                location="",
                response=last_reply,
                status="success" if full_transcript else "failed",
                duration_seconds=duration,
                summary_text=summary_text,
                sentiment=sentiment,
                customer_name=cust_name,
                outcome=outcome,
                lead_json=lead_json_str
            )
            
            # SMS follow up
            if phone_to_use and phone_to_use != "unknown" and phone_to_use != "streaming_caller":
                print(f"Sending SMS follow-up to {phone_to_use}...")
                # sms_body = format_sms_history(conversation_history)
                await send_sms(
                    phone_to_use,
                    summary_text
                )
            else:
                print("Caller number unknown. Skipping SMS sending.")