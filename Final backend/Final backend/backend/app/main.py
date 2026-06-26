from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes.voice import router as voice_router
from app.utils.db import init_db
from app.routes.stream import router as stream_router
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="AI Without Internet")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)
app.include_router(stream_router)


from app.services.llm import get_ai_reply

@app.get("/test-ai")
async def test_ai():
    return await get_ai_reply(
        "delhi mein mausam kaisa hai"
    )

@app.on_event("startup")
async def startup():
    init_db()
    try:
        from app.services.audio_convert import _resolve_ffmpeg
        print(f"Audio converter ready: {_resolve_ffmpeg()}")
    except Exception as e:
        print(f"WARNING: audio conversion unavailable — {e}")

    if not (os.getenv("GROQ_API_KEY") or "").strip():
        print("WARNING: GROQ_API_KEY is not set in .env — LLM and STT will not work.")


@app.get("/ping")
async def ping():
    return {"status": "ok"}
app.mount(
    "/audio",
    StaticFiles(directory="."),
    name="audio"
)