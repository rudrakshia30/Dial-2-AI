<img width="4320" height="1440" alt="HackHazards 2026 Banner" src="https://github.com/user-attachments/assets/c698b2cd-da84-4cb0-9276-125c6a7244aa" />

# 🚀 Dial2AI

> **Making Generative AI Accessible Through a Phone Call.**
>
> **No Internet. No Smartphone. No App. Just a Phone Call. 📞🤖**

---

# 📌 Problem & Domain

Generative AI is transforming every industry, but millions of people still cannot access it because they lack smartphones, stable internet connectivity, or the digital literacy required to use modern applications.

Farmers, senior citizens, daily wage workers, students, and people living in rural areas often rely only on a basic mobile phone. Traditional IVR systems are limited to predefined menu options and cannot understand natural language conversations.

**Dial2AI bridges this digital divide by enabling anyone to interact with an AI assistant through a simple phone call.**

A user simply dials a phone number, asks a question naturally, and receives an intelligent spoken response in **English, Hindi, or Hinglish**—without installing an app or using the internet.

---

## 📌 Themes Selected

- [x] Human Experience & Productivity
- [ ] Climate & Sustainability Systems
- [ ] HealthTech & Bio Platforms
- [x] Learning & Knowledge Systems
- [ ] Work, Finance & Digital Economy
- [x] Infrastructure, Mobility & Smart Systems
- [ ] Trust, Identity & Security
- [ ] Media, Social & Interactive Platforms
- [x] Public Systems, Governance and Civic Tech
- [x] Developer Tools & Software Infrastructure

---

# 🎯 Objective

Dial2AI aims to democratize access to Generative AI by making it available through the world's most familiar interface—a phone call.

### Target Users

- 👨‍🌾 Farmers
- 👵 Senior Citizens
- 👨‍🏭 Daily Wage Workers
- 👨‍🎓 Students
- 🌾 Rural Communities
- 📱 People without Smartphones or Internet

### Pain Points

- No smartphone
- Poor internet connectivity
- Low digital literacy
- Traditional IVR systems are rigid and menu-driven
- AI remains inaccessible to a large population

### Our Solution

Dial2AI converts a regular phone call into a natural conversation with an AI assistant capable of:

- Answering open-ended questions
- Providing live weather/news information
- Understanding follow-up questions
- Speaking multiple languages
- Personalizing future conversations

---

# 🧠 Team & Approach

## Team Name

`Git Push Pray`

## Team Members

- **Prabhav Agrawal** 
- **Rudrakshi Agarwal**

---

## Our Approach

Instead of creating another AI application, we focused on eliminating the biggest barrier—**the need for a smartphone.**

We designed Dial2AI around something nearly everyone already understands:

📞 **A Phone Call**

Major engineering challenges included:

- Real-time bidirectional audio streaming
- Maintaining low latency
- Noise suppression
- Smart silence detection
- Barge-in interruption
- Hinglish understanding
- Conversational memory

Using asynchronous WebSockets, AI inference, and graph-based memory, we created a natural voice-first AI experience.

---

# 🛠️ Tech Stack

## Core Technologies Used

### Frontend

- Next.js
- React
- TailwindCSS
- Recharts
- Lucide Icons

Frontend Deployment

➡️ **https://dial2-ai.vercel.app/**

---

### Backend

- Python
- FastAPI
- Uvicorn
- WebSockets
- HTTPX
- Pydantic
- FFmpeg

Backend Deployment

☁️ **Render**

---

### Database

- SQLite
- **Neo4j AuraDB**

---

### AI

- Grok STT
- Grok 4.1 Fast
- Google Text-to-Speech
- gTTS

---

### Telephony

- Exotel
- Passthru Applets

---

### Dashboard

- **Base44**

---

### Hosting

- Vercel (Frontend)
- Render (Backend)

---

## Additional Technologies Used

- [x] AI / ML
- [ ] Web3 / Blockchain
- [ ] Cyber Security
- [x] Cloud

---

# 🏆 Sponsored Track

## ✅ Neo4j Track

We use **Neo4j AuraDB** as our graph database to maintain conversational memory.

AuraDB stores relationships between:

- Callers
- Previous conversations
- Interests
- Topics
- Locations

This enables personalized responses for returning users.

---

## ✅ Base44 Track

We built our operational dashboard using **Base44**.

It provides:

- Call analytics
- Conversation history
- Intent detection
- Sentiment analysis
- Dashboard management
- Backend configuration

This accelerated dashboard development, allowing us to focus on building the real-time AI pipeline.

---

## ✅ Render

Our FastAPI backend is deployed on **Render**, providing reliable cloud hosting for our real-time AI voice pipeline.

---

# ✨ Key Features

- ✅ AI conversations through a simple phone call
- ✅ Works without smartphone or internet
- ✅ English, Hindi & Hinglish support
- ✅ Conversational memory using Neo4j AuraDB
- ✅ Live weather, news and public information
- ✅ Real-time speech-to-text
- ✅ AI-generated spoken responses
- ✅ Barge-in interruption support
- ✅ Smart silence detection
- ✅ Noise gate for telecom static
- ✅ Hold music during AI processing
- ✅ Dashboard with analytics and transcripts
- ✅ Real-time WebSocket streaming

---

# 📽️ Demo & Deliverables

### 🎥 Demo Video

Coming Soon

---

### 🌐 Frontend Deployment

https://dial2-ai.vercel.app/

---

### ⚙️ Backend

Hosted on **Render**

---

### 📑 Pitch Deck

Coming Soon

---

# ✅ Tasks & Bonus Checklist

- [x] All team members completed the mandatory social task
- [x] Bonus Task 1 – Badge sharing
- [x] Bonus Task 2 – Blog/Article

---

# 🧪 How to Run the Project

## Requirements

- Python 3.11+
- Node.js 20+
- FFmpeg
- Exotel Account
- Grok API Key
- Weather API
- News API
- Neo4j AuraDB Instance

---

## Environment Variables

```env
GROK_API_KEY=
EXOTEL_API_KEY=
EXOTEL_API_TOKEN=
EXOTEL_SID=
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
WEATHER_API_KEY=
NEWS_API_KEY=
```

---

## Local Setup

### Clone Repository

```bash
git clone https://github.com/yourusername/Dial2AI.git

cd Dial2AI
```

### Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🧬 Future Scope

- 🌍 Support for more Indian regional languages
- 📞 Missed-call callback system
- 📍 Location-aware weather updates
- 🌾 Agmarknet & Mandi price integration
- 🚆 Railway APIs
- 🏥 Healthcare integrations
- 🏛 Government scheme recommendations
- 💬 Two-way SMS conversations
- 🧠 Smarter personalization using Neo4j graphs
- 📈 Advanced analytics dashboard

---

# 📎 Resources / Credits

### APIs

- Exotel
- Grok API
- Google Text-to-Speech
- Weather APIs
- News APIs

### Technologies

- FastAPI
- Next.js
- Neo4j AuraDB
- Base44
- Render
- SQLite
- React
- TailwindCSS
- Recharts

---

# 🏁 Final Words

Dial2AI was built with a simple belief:

> **Artificial Intelligence should not be limited to people with smartphones.**

If someone can make a phone call, they should be able to access AI.

By combining **real-time telephony**, **Generative AI**, **Neo4j AuraDB**, **Base44**, and **Render**, we transformed an ordinary phone call into an intelligent conversation.

📞 **No Internet.**

📱 **No Smartphone.**

🤖 **Just Dial. Just Ask.**

---

## ❤️ Built with passion at HackHazards'26

**Team Git Push Pray**
