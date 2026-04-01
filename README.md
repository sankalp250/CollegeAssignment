# 🎮 NEXUS GAMES v2 — Swipe Carousel + Auth System

## What's New in v2
- ✅ Physics-based swipe carousel (velocity detection + spring snap)
- ✅ JWT authentication (Login / Register)
- ✅ Guest mode (no sign-up required)
- ✅ Persistent progress (save + resume game)
- ✅ Auto-login on refresh (token validation)
- ✅ Profile dropdown with logout

---

## 🚀 Quick Start

Open `index.html` directly — works standalone with localStorage auth.

---

## 🐍 Backend Setup (FastAPI + JWT)

```bash
cd backend

python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

pip install fastapi uvicorn pydantic python-jose[cryptography] bcrypt

python main.py
# → http://localhost:8000
# → Docs: http://localhost:8000/docs
```

---

## 📡 API Reference

### Auth
| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/register` | `{username, email, password}` | `201 Created` |
| POST | `/login` | `{email, password}` | `{access_token, username}` |
| GET | `/me` | — (Bearer token) | `{username, email}` |

### Progress
| Method | Endpoint | Auth | Body |
|--------|----------|------|------|
| POST | `/save-progress` | ✅ | `{game, score, level, pattern}` |
| GET | `/progress` | ✅ | — |

### Game
| Method | Endpoint | Body |
|--------|----------|------|
| POST | `/generate-grid` | `{rows, cols, pattern}` |
| POST | `/validate-move` | `{row, col, tile_type, current_score, current_lives}` |
| POST | `/game-status` | `{score, lives, time_remaining, blue_collected, blue_total}` |

---

## 🧠 Swipe Engine — How It Works

```
pointerdown → record startX, startTime
pointermove → translate track by delta (elastic at edges)
pointerup   → compute velocity = dx / elapsed (px/ms)

if |velocity| > 0.35 OR |distance| > 28% of cardWidth:
    advance/retreat to next card
else:
    spring back to current card

snap uses cubic-bezier(0.25, 0.46, 0.45, 0.94) spring
```

Works on both **touch (mobile)** and **mouse drag (desktop)** via unified Pointer Events API.

---

## 🔐 Auth Flow

```
App Boot
  ├─ localStorage has valid token? → auto-login → Game Selection
  └─ No token → Auth Screen

Login
  ├─ Try real API (2s timeout)
  └─ Fall back to localStorage mock DB

Register
  ├─ Validate (email unique, password ≥ 6 chars)
  ├─ Try real API
  └─ Always write to localStorage mock DB

Token format: JWT (HS256) or base64-JSON fallback if jose not installed
Token stored in: localStorage['nexus_token']
```

---

## 🌐 Deployment

### Frontend → Vercel
```bash
# No build needed — upload index.html directly
# Or wrap in Vite React and: npm run build && vercel --prod
```

### Backend → Render
1. Push `backend/` to GitHub
2. New Web Service: Python 3.11
3. Build: `pip install fastapi uvicorn pydantic python-jose[cryptography] bcrypt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set env var: `SECRET_KEY=your-secret-here`

> ⚠️ Current backend uses in-memory DB. For production, swap `DB: dict` with PostgreSQL using `databases` + `asyncpg`.

---

## 📁 Structure
```
nexus-games-v2/
├── index.html          ← Complete frontend (auth + carousel + game)
├── README.md
└── backend/
    └── main.py         ← FastAPI: JWT auth + progress + game APIs
```
