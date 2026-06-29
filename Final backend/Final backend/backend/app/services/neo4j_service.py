"""
neo4j_service.py
----------------
Reusable async Neo4j AuraDB service for persistent caller memory.

Graph schema
------------
(Person {phone, name, age, city, college, profession,
         preferred_language, summary, last_called})
  -[:LIKES]->   (Interest    {name})
  -[:WORKS_ON]-> (Project     {name})
  -[:HAD_CALL]-> (Conversation {id, timestamp, summary})

All public helpers are async-safe and wrapped in try/except so a
Neo4j outage never crashes the voice call.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Driver — lazy singleton
# ---------------------------------------------------------------------------

_driver = None


def _get_driver():
    """Return a shared AsyncDriver, or None if env vars are missing."""
    global _driver
    if _driver is not None:
        return _driver

    uri      = os.getenv("NEO4J_URI", "").strip()
    username = os.getenv("NEO4J_USERNAME", "").strip()
    password = os.getenv("NEO4J_PASSWORD", "").strip()

    if not uri or not username or not password:
        logger.warning(
            "Neo4j env vars (NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD) "
            "are not set — persistent memory disabled."
        )
        return None

    try:
        from neo4j import AsyncGraphDatabase  # noqa: import inside function (optional dep)
        # bolt+ssc:// already trusts self-signed certs — no extra params needed
        _driver = AsyncGraphDatabase.driver(
            uri,
            auth=(username, password),
            notifications_min_severity="OFF",  # Silences DBMS schema warning notifications
        )
        logger.info("Neo4j driver initialised: %s", uri)
    except Exception as exc:
        logger.error("Failed to create Neo4j driver: %s", exc)
        _driver = None

    return _driver


async def init_neo4j():
    """
    Call once at application startup.
    Verifies connection and initializes uniqueness constraints and indexes.
    """
    driver = _get_driver()
    if driver is None:
        return

    try:
        await driver.verify_connectivity()
        logger.info("✅ Neo4j AuraDB connected successfully.")
        
        # Pre-create constraints and indexes to optimize performance and prevent schema warnings
        db_name = os.getenv("NEO4J_DATABASE", "neo4j")
        async with driver.session(database=db_name) as session:
            await session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.phone IS UNIQUE")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (i:Interest) ON (i.name)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (pr:Project) ON (pr.name)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (c:Conversation) ON (c.id)")
        logger.info("✅ Neo4j database schema constraints & indexes verified/created.")
    except Exception as exc:
        logger.error("❌ Neo4j initialization check failed: %s", exc)


async def close_neo4j():
    """Call once at application shutdown to release the driver."""
    global _driver
    if _driver is not None:
        try:
            await _driver.close()
            logger.info("Neo4j driver closed.")
        except Exception as exc:
            logger.error("Error closing Neo4j driver: %s", exc)
        finally:
            _driver = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value) -> str:
    """Return a stripped string, or empty string for None/falsy."""
    if value is None:
        return ""
    return str(value).strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_person_by_phone(phone: str) -> Optional[dict]:
    """
    Fetch the full profile of a Person node by phone number.

    Returns a dict with keys:
        phone, name, age, city, college, profession,
        preferred_language, summary, last_called,
        interests (list[str]), projects (list[str]),
        recent_conversations (list[dict])

    Returns None if the person is not found or Neo4j is unavailable.
    """
    driver = _get_driver()
    if driver is None:
        return None

    try:
        async with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            result = await session.run(
                """
                MATCH (p:Person {phone: $phone})
                OPTIONAL MATCH (p)-[:LIKES]->(i:Interest)
                OPTIONAL MATCH (p)-[:WORKS_ON]->(pr:Project)
                OPTIONAL MATCH (p)-[:HAD_CALL]->(c:Conversation)
                RETURN p,
                       collect(DISTINCT i.name) AS interests,
                       collect(DISTINCT pr.name) AS projects,
                       collect(DISTINCT {id: c.id, timestamp: c.timestamp, summary: c.summary})
                           AS conversations
                """,
                phone=phone,
            )
            record = await result.single()
            if record is None:
                return None

            node = record["p"]
            conversations = sorted(
                [cv for cv in record["conversations"] if cv.get("id")],
                key=lambda x: x.get("timestamp", ""),
                reverse=True,
            )[:10]  # keep 10 most recent

            return {
                "phone":              node.get("phone", phone),
                "name":               node.get("name", ""),
                "age":                node.get("age", ""),
                "city":               node.get("city", ""),
                "college":            node.get("college", ""),
                "profession":         node.get("profession", ""),
                "preferred_language": node.get("preferred_language", ""),
                "summary":            node.get("summary", ""),
                "last_called":        node.get("last_called", ""),
                "interests":          [x for x in record["interests"] if x],
                "projects":           [x for x in record["projects"] if x],
                "recent_conversations": conversations,
            }
    except Exception as exc:
        logger.error("get_person_by_phone(%s) error: %s", phone, exc)
        return None


async def create_person(phone: str) -> bool:
    """
    Create a bare Person node with just the phone number.
    Returns True on success, False on failure.
    """
    driver = _get_driver()
    if driver is None:
        return False

    try:
        async with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            await session.run(
                """
                MERGE (p:Person {phone: $phone})
                ON CREATE SET p.last_called = $now
                """,
                phone=phone,
                now=_now_iso(),
            )
        logger.info("Person node ensured for phone: %s", phone)
        return True
    except Exception as exc:
        logger.error("create_person(%s) error: %s", phone, exc)
        return False


async def update_person_memory(phone: str, memory: dict) -> bool:
    """
    Upsert all extracted memory fields onto a Person node.

    memory keys (all optional):
        name, age, city, college, profession,
        preferred_language, summary,
        interests (list), projects (list)

    Interests and Projects are MERGE'd — no duplicates.
    Returns True on success.
    """
    driver = _get_driver()
    if driver is None:
        return False

    if not phone:
        return False

    try:
        async with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            # --- 1. Upsert scalar properties ---
            await session.run(
                """
                MERGE (p:Person {phone: $phone})
                SET p.last_called        = $now,
                    p.name               = CASE WHEN $name <> ''               THEN $name               ELSE coalesce(p.name, '') END,
                    p.age                = CASE WHEN $age <> ''                THEN $age                ELSE coalesce(p.age, '') END,
                    p.city               = CASE WHEN $city <> ''               THEN $city               ELSE coalesce(p.city, '') END,
                    p.college            = CASE WHEN $college <> ''            THEN $college            ELSE coalesce(p.college, '') END,
                    p.profession         = CASE WHEN $profession <> ''         THEN $profession         ELSE coalesce(p.profession, '') END,
                    p.preferred_language = CASE WHEN $preferred_language <> '' THEN $preferred_language ELSE coalesce(p.preferred_language, '') END,
                    p.summary            = CASE WHEN $summary <> ''            THEN $summary            ELSE coalesce(p.summary, '') END
                """,
                phone=phone,
                now=_now_iso(),
                name=_clean(memory.get("name")),
                age=_clean(memory.get("age")),
                city=_clean(memory.get("city")),
                college=_clean(memory.get("college")),
                profession=_clean(memory.get("profession")),
                preferred_language=_clean(memory.get("preferred_language")),
                summary=_clean(memory.get("summary")),
            )

            # --- 2. Merge interests (no duplicates) ---
            interests = [_clean(i) for i in (memory.get("interests") or []) if _clean(i)]
            for interest in interests:
                await session.run(
                    """
                    MATCH (p:Person {phone: $phone})
                    MERGE (i:Interest {name: $interest})
                    MERGE (p)-[:LIKES]->(i)
                    """,
                    phone=phone,
                    interest=interest,
                )

            # --- 3. Merge projects (no duplicates) ---
            projects = [_clean(p) for p in (memory.get("projects") or []) if _clean(p)]
            for project in projects:
                await session.run(
                    """
                    MATCH (p:Person {phone: $phone})
                    MERGE (pr:Project {name: $project})
                    MERGE (p)-[:WORKS_ON]->(pr)
                    """,
                    phone=phone,
                    project=project,
                )

        logger.info("Memory updated for phone: %s", phone)
        return True

    except Exception as exc:
        logger.error("update_person_memory(%s) error: %s", phone, exc)
        return False


async def save_conversation(phone: str, summary: str, timestamp: str = None) -> bool:
    """
    Create a Conversation node and attach it to the Person via HAD_CALL.
    Prunes conversations beyond the 10 most recent.

    Returns True on success.
    """
    driver = _get_driver()
    if driver is None:
        return False

    if not phone or not summary:
        return False

    ts = timestamp or _now_iso()
    conv_id = f"{phone}_{ts}"

    try:
        async with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            # Create conversation
            await session.run(
                """
                MERGE (p:Person {phone: $phone})
                CREATE (c:Conversation {id: $id, timestamp: $ts, summary: $summary})
                CREATE (p)-[:HAD_CALL]->(c)
                """,
                phone=phone,
                id=conv_id,
                ts=ts,
                summary=summary,
            )

            # Prune: keep only 10 most recent conversations
            await session.run(
                """
                MATCH (p:Person {phone: $phone})-[:HAD_CALL]->(c:Conversation)
                WITH c ORDER BY c.timestamp DESC
                SKIP 10
                DETACH DELETE c
                """,
                phone=phone,
            )

        logger.info("Conversation saved for phone: %s", phone)
        return True

    except Exception as exc:
        logger.error("save_conversation(%s) error: %s", phone, exc)
        return False


async def get_relevant_memory(phone: str) -> Optional[dict]:
    """
    High-level helper used by the call route.

    1. Looks up the person in Neo4j.
    2. If they don't exist yet, creates a bare node and returns None
       (the LLM won't get a memory block for first-time callers).
    3. Returns the memory dict for returning callers.
    """
    if not phone or phone in ("unknown", "streaming_caller"):
        return None

    person = await get_person_by_phone(phone)

    if person is None:
        # First-time caller — create the node so it's ready for post-call update
        await create_person(phone)
        return None

    # Only return memory if there's something meaningful to inject
    has_data = any([
        person.get("name"),
        person.get("age"),
        person.get("city"),
        person.get("college"),
        person.get("profession"),
        person.get("interests"),
        person.get("projects"),
        person.get("recent_conversations"),
    ])

    return person if has_data else None
