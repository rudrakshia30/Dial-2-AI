# AI Without Internet

AI Without Internet is an AI-powered voice assistant accessible to everyone via a simple phone call.

Users call a designated number and directly speak their questions. The system uses AI to understand and answer questions in Hindi/Hinglish/English about:

- Crop prices (mandi rates)
- Weather updates
- Government schemes
- General knowledge
- Health, education, and more

No smartphone or internet needed — just a basic phone and a phone call.

---

# Architecture

```
                    +------------------+
                    |   User Calls     |
                    |  Exotel Number   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |     Exotel       |
                    | (Answers Call)   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | FastAPI Backend   |
                    | /voice/start     |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
       +------------+              +---------------+
       | Gemini STT |              | Gemini LLM    |
       | (Audio →   |              | (Understand   |
       |  Text)     |              |  Intent)      |
       +------------+              +---------------+
              |                             |
              +-------------+---------------+
                            |
                            v
                   +------------------+
                   | Exotel <say>     |
                   | (Speaks Reply)   |
                   +------------------+
                            |
                            v
                   +------------------+
                   | Follow-up Loop   |
                   | (Ask more Qs)    |
                   +------------------+
```

---

# Call Flow

1. User dials **09513886363**
2. Exotel answers → Passthru applet calls `/voice/start`
3. AI greets user → records question after beep
4. Recording sent to `/voice/question`
5. Gemini transcribes audio → understands intent → fetches data
6. Exotel speaks the reply using `<say>` tag
7. Asks "Kya aur koi sawaal hai?" → records again → loops
8. User hangs up when done

---

# Folder Structure

```
backend/         → FastAPI server (Python)
frontend/        → Next.js dashboard
README.md        → This file
```

---

# Environment Variables

| Variable | Description |
|-----------|------------|
| GEMINI_API_KEY | Google Gemini API Key |
| EXOTEL_API_KEY | Exotel API Key |
| EXOTEL_API_TOKEN | Exotel API Token |
| EXOTEL_SID | Exotel Account SID |
| EXOTEL_NUMBER | Your Exotel Virtual Number |
| BASE_URL | Public backend URL (ngrok/Railway) |
| DATA_GOV_API_KEY | Data.gov.in API Key (optional) |
| WEATHER_API_KEY | OpenWeatherMap Key (optional) |

---

# Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

Copy environment file:

```bash
cp .env.example .env
```

Fill all environment variables.

Run:

```bash
uvicorn app.main:app --reload
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend: `http://localhost:3000`

Backend: `http://localhost:8000`

---

# Exotel Configuration

## Flow Setup

1. Go to Exotel Dashboard → App Bazaar
2. Open your flow (or create new one)
3. Set flow as:

```
Incoming Call → Passthru Applet
  URL: https://YOUR_BASE_URL/voice/start
  Method: POST
```

4. Assign this flow to your Exotel number (09513886363)

## Endpoints Used by Exotel

| Endpoint | Purpose |
|----------|---------|
| `/voice/start` | Greets caller, starts recording |
| `/voice/question` | Processes recording, returns AI reply + follow-up |

---

# Running with ngrok

```bash
ngrok http 8000
```

Use the ngrok URL as `BASE_URL` in `.env`.

---

# Railway Deployment

1. Create Railway Project
2. Set environment variables
3. Deploy backend repository

Railway builds using `Dockerfile` and `railway.toml`.

Health Check: `/ping`

---

# Monitoring Dashboard

Dashboard includes:

- Total Calls Today
- Successful Calls
- Failed Calls
- Calls Per Hour chart
- Recent Call Activity

---

# Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| AI Model | Gemini 2.5 Flash |
| STT | Gemini Audio Transcription |
| TTS | Exotel built-in `<say>` |
| Telephony | Exotel (KooKoo XML) |
| Frontend | Next.js + TailwindCSS |
| Database | SQLite |
| Deployment | Railway + Vercel |

---

# Security Notes

- Phone numbers are masked before storage
- API keys stored only in environment variables
- SQLite can be replaced by PostgreSQL in production

---

# Team

| Member | Responsibility |
|----------|----------------|
| Prabhav | Backend |
| Sagar | AI / ML |
| Rudrakshi | Data & APIs |
| Niyati | Frontend |

---

# License

MIT License