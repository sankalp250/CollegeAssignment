# 🎮 Nexus Games Platform

A high-performance, visually stunning mini-game platform featuring a collection of four interactive challenges. Built with a modern tech stack and a premium neon aesthetic.

## 🚀 Live Deployments

| Component | Status | URL |
| :--- | :--- | :--- |
| **Frontend** | 🟢 Live (Vercel) | [https://college-assignment-chi.vercel.app/](https://college-assignment-chi.vercel.app/) |
| **Backend** | 🟢 Live (Render) | [https://collegeassignment-11l3.onrender.com](https://collegeassignment-11l3.onrender.com) |

---

## ✨ Features

### 🕹️ Mini-Game Collection
- **Escape the Lava**: A strategic grid-based survival game. Navigate your way to safety while avoiding rising fire hazards.
- **Find the Color**: Test your speed and color recognition by hitting the target color as fast as possible.
- **Red Light Green Light**: A high-stakes trial of patience and reaction. Move only when the light is green, or face immediate elimination.
- **Sharp Shooter**: A fast-paced accuracy challenge. Hit 15 targets as they spawn at increasing speeds to win.

### 🛡️ Core Systems
- **Persistent Progress**: Secure user accounts with SQLite-backed session persistence.
- **Dynamic Difficulty**: Real-time speed scaling in Shooter and randomized patterns in RLGL.
- **Premium UI**: 3D parallax carousel, neon glassmorphism design, and smooth micro-animations.

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Custom Design System), Javascript (ES6+)
- **Backend**: FastAPI (Python), JWT Authentication, SQLite (Permanent Data Store)
- **Deployment**: Vercel (Frontend), Render (Backend)

---

## ⚙️ Local Setup

### Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python main.py
   ```
   *The server will automatically initialize the `nexus.db` SQLite database.*

### Frontend
1. Open `index.html` in any modern browser.
2. Ensure the `API_BASE` variable in `index.html` points to your local or deployed backend.

---

## 📝 License
Created for College Assignment. All rights reserved.
