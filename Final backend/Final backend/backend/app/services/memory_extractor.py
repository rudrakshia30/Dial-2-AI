"""
memory_extractor.py
-------------------
After every call, send the conversation transcript to the LLM and
extract only persistent, long-term facts about the caller.

Transient information ("I am hungry", "call me back in 5 minutes") is
deliberately ignored — only stable profile data is returned.
"""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------------

_EXTRACTION_PROMPT = """\
You are an expert at extracting persistent personal information from phone call transcripts.

Read the following conversation and extract ONLY stable, long-term facts about the CALLER (the user, not the AI assistant).

Rules:
- IGNORE transient statements like "I am hungry", "call me back", "I need water", etc.
- KEEP persistent facts: name, age, city, college, profession, language preference, hobbies, projects, family, long-term goals.
- If a fact is not mentioned in THIS conversation, leave the field empty ("" or []).
- For interests and projects, return a simple list of short strings.
- IMPORTANT: If the user CORRECTS any information (e.g. "No, my name is X", "Actually I live in Y", "That's wrong, I am Z"), ALWAYS use the corrected value. The user's latest statement is always the truth.
- If the AI called the user by a wrong name and the user provided their real name, use the user's stated name.
- Return ONLY valid JSON. No markdown, no explanation.
{existing_memory_block}
Conversation Transcript:
{transcript}

Return a JSON object with EXACTLY these keys:
{{
  "name": "",
  "age": "",
  "city": "",
  "college": "",
  "profession": "",
  "preferred_language": "",
  "interests": [],
  "projects": [],
  "preferences": [],
  "summary": ""
}}
"""

_EMPTY_MEMORY = {
    "name": "",
    "age": "",
    "city": "",
    "college": "",
    "profession": "",
    "preferred_language": "",
    "interests": [],
    "projects": [],
    "preferences": [],
    "summary": "",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def extract_memory_from_transcript(
    history: list,
    existing_memory: dict = None,
) -> Optional[dict]:
    """
    Extract persistent caller facts from the conversation history.

    Parameters
    ----------
    history : list of {"role": "user"|"assistant", "content": str}
    existing_memory : dict, optional
        The caller's current profile from Neo4j. Passed to the LLM so
        it can detect corrections (e.g. "No, my name is X not Y").

    Returns
    -------
    dict matching _EMPTY_MEMORY schema, or None on hard failure.
    """
    if not history:
        return None

    # Only extract if there's at least one meaningful user message
    user_messages = [m["content"] for m in history if m.get("role") == "user" and m.get("content", "").strip()]
    if not user_messages:
        return None

    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in history
        if m.get("content", "").strip()
    )

    # Build existing memory block so the LLM can detect corrections
    existing_memory_block = ""
    if existing_memory:
        parts = ["\nExisting caller profile (from previous calls):"]
        for key in ("name", "age", "city", "college", "profession", "preferred_language"):
            val = existing_memory.get(key, "")
            if val:
                parts.append(f"  {key}: {val}")
        if existing_memory.get("interests"):
            parts.append(f"  interests: {', '.join(existing_memory['interests'])}")
        if existing_memory.get("projects"):
            parts.append(f"  projects: {', '.join(existing_memory['projects'])}")
        parts.append(
            "If the user corrects any of the above information in this conversation, "
            "use the corrected value in your output. The user's words always take priority."
        )
        existing_memory_block = "\n".join(parts) + "\n"

    prompt = _EXTRACTION_PROMPT.format(
        transcript=transcript,
        existing_memory_block=existing_memory_block,
    )

    try:
        # Re-use the same Groq client as the main LLM service
        from app.services.llm import _get_client, MODEL

        client = _get_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,  # Low temperature for deterministic extraction
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if the model adds them anyway
        if raw.startswith("```"):
            lines = raw.splitlines()
            lines = [l for l in lines if not l.startswith("```")]
            raw = "\n".join(lines).strip()

        memory = json.loads(raw)

        # Ensure all expected keys exist (fill missing ones with defaults)
        for key, default in _EMPTY_MEMORY.items():
            if key not in memory:
                memory[key] = default

        # Normalise list fields
        for list_key in ("interests", "projects", "preferences"):
            if not isinstance(memory.get(list_key), list):
                memory[list_key] = []
            memory[list_key] = [str(x).strip() for x in memory[list_key] if str(x).strip()]

        logger.info("Memory extracted successfully from transcript.")
        return memory

    except json.JSONDecodeError as exc:
        logger.error("Memory extraction JSON parse error: %s — raw: %s", exc, raw[:200] if 'raw' in dir() else "N/A")
        return None
    except Exception as exc:
        logger.error("Memory extraction failed: %s", exc)
        return None
