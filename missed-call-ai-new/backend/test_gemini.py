import asyncio
from app.services.llm import get_ai_reply

reply = asyncio.run(
    get_ai_reply("दिल्ली का मौसम कैसा है")
)

print(reply)