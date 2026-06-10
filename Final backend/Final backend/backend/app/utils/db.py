import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_NAME = os.getenv(
    "CALLS_DB_PATH",
    str(Path(__file__).resolve().parents[2] / "calls.db"),
)


def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS call_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT,
        timestamp TEXT,
        transcript TEXT,
        intent TEXT,
        crop TEXT,
        location TEXT,
        response TEXT,
        status TEXT,
        duration_seconds INTEGER
    )
    """)

    # Add new columns if they don't exist
    cols = [
        ("summary_text", "TEXT"),
        ("sentiment", "TEXT"),
        ("customer_name", "TEXT"),
        ("outcome", "TEXT"),
        ("lead_json", "TEXT")
    ]
    for col_name, col_type in cols:
        try:
            conn.execute(f"ALTER TABLE call_logs ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            # Column already exists
            pass

    conn.commit()
    conn.close()


def mask_phone(phone):
    if len(phone) < 4:
        return phone
    return "*" * (len(phone)-4) + phone[-4:]


def insert_log(
        phone_number,
        transcript,
        intent,
        crop,
        location,
        response,
        status,
        duration
):
    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT INTO call_logs
        (
            phone_number,
            timestamp,
            transcript,
            intent,
            crop,
            location,
            response,
            status,
            duration_seconds
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            mask_phone(phone_number),
            datetime.utcnow().isoformat(),
            transcript,
            intent,
            crop,
            location,
            response,
            status,
            duration
        )
    )

    conn.commit()
    conn.close()


def insert_complete_call_log(
    phone_number,
    transcript,
    intent,
    crop,
    location,
    response,
    status,
    duration_seconds,
    summary_text=None,
    sentiment=None,
    customer_name=None,
    outcome=None,
    lead_json=None
):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        """
        INSERT INTO call_logs
        (
            phone_number,
            timestamp,
            transcript,
            intent,
            crop,
            location,
            response,
            status,
            duration_seconds,
            summary_text,
            sentiment,
            customer_name,
            outcome,
            lead_json
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            mask_phone(phone_number),
            datetime.utcnow().isoformat(),
            transcript,
            intent,
            crop,
            location,
            response,
            status,
            duration_seconds,
            summary_text,
            sentiment,
            customer_name,
            outcome,
            lead_json
        )
    )
    conn.commit()
    conn.close()


def get_logs(limit=50):
    conn = sqlite3.connect(DB_NAME)

    rows = conn.execute(
        """
        SELECT *
        FROM call_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    return rows


import json

def get_stats():
    conn = sqlite3.connect(DB_NAME)

    today = datetime.utcnow().date().isoformat()

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM call_logs
        WHERE timestamp LIKE ?
        """,
        (f"{today}%",)
    ).fetchone()[0]

    success = conn.execute(
        """
        SELECT COUNT(*)
        FROM call_logs
        WHERE status='success'
        AND timestamp LIKE ?
        """,
        (f"{today}%",)
    ).fetchone()[0]

    failed = conn.execute(
        """
        SELECT COUNT(*)
        FROM call_logs
        WHERE status='failed'
        AND timestamp LIKE ?
        """,
        (f"{today}%",)
    ).fetchone()[0]

    hourly_rows = conn.execute(
        """
        SELECT substr(timestamp, 12, 2) AS hour, COUNT(*) AS count
        FROM call_logs
        WHERE timestamp LIKE ?
        GROUP BY hour
        ORDER BY hour
        """,
        (f"{today}%",)
    ).fetchall()

    # Average Call Duration
    avg_duration_row = conn.execute(
        """
        SELECT AVG(duration_seconds)
        FROM call_logs
        WHERE duration_seconds > 0
        """
    ).fetchone()
    avg_duration = round(avg_duration_row[0], 1) if avg_duration_row and avg_duration_row[0] is not None else 0.0

    # Sentiment distribution
    sentiment_rows = conn.execute(
        """
        SELECT sentiment, COUNT(*)
        FROM call_logs
        WHERE sentiment IS NOT NULL AND sentiment != ''
        GROUP BY sentiment
        """
    ).fetchall()
    sentiment_dist = {row[0]: row[1] for row in sentiment_rows}

    # Leads Count
    lead_rows = conn.execute(
        """
        SELECT lead_json
        FROM call_logs
        WHERE lead_json IS NOT NULL AND lead_json != ''
        """
    ).fetchall()
    leads_count = 0
    for row in lead_rows:
        try:
            lead_data = json.loads(row[0])
            # Count as lead if name or interest is extracted (not "Unknown" or empty)
            name = lead_data.get("name", "Unknown")
            interest = lead_data.get("interest", "Unknown")
            if (name and name != "Unknown") or (interest and interest != "Unknown"):
                leads_count += 1
        except Exception:
            pass

    # Top Intents
    intent_rows = conn.execute(
        """
        SELECT intent, COUNT(*) as cnt
        FROM call_logs
        WHERE intent IS NOT NULL AND intent != ''
        GROUP BY intent
        ORDER BY cnt DESC
        LIMIT 5
        """
    ).fetchall()
    top_intents = [{"intent": row[0], "count": row[1]} for row in intent_rows]

    conn.close()

    return {
        "total_today": total,
        "success_today": success,
        "failed_today": failed,
        "calls_per_hour": [
            {"hour": f"{hour}:00", "count": count}
            for hour, count in hourly_rows
        ],
        "avg_duration": avg_duration,
        "sentiment_dist": sentiment_dist,
        "leads_count": leads_count,
        "top_intents": top_intents
    }
