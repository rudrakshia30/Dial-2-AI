from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.voice import router as voice_router
from app.utils.db import init_db
from app.routes.stream import router as stream_router
from fastapi.staticfiles import StaticFiles


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


@app.get("/ping")
async def ping():
    return {"status": "ok"}
app.mount(
    "/audio",
    StaticFiles(directory="."),
    name="audio"
)