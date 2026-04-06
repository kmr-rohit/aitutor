# AI Learn - Voice Learning Platform MVP

Interview-prep-first, voice-to-voice AI learning platform with Hinglish teaching style.

## Stack

- Frontend: Next.js PWA (`frontend`)
- Backend: FastAPI (`backend`)
- Provider architecture: STT/TTS/LLM adapters (mock + Sarvam hooks)

## Quickstart

```bash
make backend
# in another terminal
make frontend
```

App: `http://localhost:3000`  
API: `http://localhost:8000`

## MVP Features Implemented

- Session creation for interview practice modes
- Real-time websocket conversation loop
- Session ending + report generation (summary, gaps, next 20-min plan)
- Nudge scheduling + streak tracking APIs
- Hinglish-style tutor responses (mock provider)
- PWA manifest and mobile-first UI shell

## Next Priority Integrations

- Replace/augment mock providers with real API keys in `.env`
- Add persistent Postgres + Redis + Celery jobs
- Wire WhatsApp delivery provider for scheduled nudges
- Add proper auth and encrypted data storage
