"""
Nexus Games — FastAPI Backend
Includes: SQLite Auth, User Progress, Grid Generation
"""
import sqlite3
from contextlib import closing
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib, secrets, json, os

# ── Try to import JWT; graceful fallback ──────────────────
try:
    from jose import jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️  python-jose not installed. Run: pip install python-jose[cryptography]")

# ── Try bcrypt ────────────────────────────────────────────
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# ─────────────────────────────────────────────────────────
SECRET_KEY  = os.getenv("SECRET_KEY", "nexus_super_secret_dev_key_12345")
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 24
DB_PATH = "nexus.db"

app = FastAPI(title="Nexus Games API", version="3.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_db()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                progress TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# ═══════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class UserMe(BaseModel):
    username: str
    email: str

class ProgressData(BaseModel):
    game: str
    score: int
    level: int = 1
    pattern: int = 1

class GridRequest(BaseModel):
    rows: int = 10
    cols: int = 10
    pattern: int = 1

class GridResponse(BaseModel):
    grid: List[List[str]]
    rows: int
    cols: int
    blue_count: int
    pattern: int

# ═══════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════
def hash_password(password: str) -> str:
    if BCRYPT_AVAILABLE:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            pass
    return hashlib.sha256(plain.encode()).hexdigest() == hashed

def create_token(email: str) -> str:
    if not JWT_AVAILABLE:
        import base64
        payload = json.dumps({"sub": email, "exp": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)).isoformat()})
        return base64.b64encode(payload.encode()).decode()
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[str]:
    if not token: return None
    try:
        if JWT_AVAILABLE:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        else:
            import base64
            payload = json.loads(base64.b64decode(token.encode()).decode())
            exp = datetime.fromisoformat(payload["exp"])
            if datetime.utcnow() > exp: return None
            return payload.get("sub")
    except Exception: return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    with closing(get_db()) as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return dict(user)

# ═══════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════
@app.post("/register", status_code=201)
def register(body: RegisterRequest):
    with closing(get_db()) as conn:
        if conn.execute("SELECT email FROM users WHERE email = ?", (body.email,)).fetchone():
            raise HTTPException(400, "Email already registered")
        
        conn.execute(
            "INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)",
            (body.email, body.username, hash_password(body.password))
        )
        conn.commit()
    return {"message": "Account created", "username": body.username}

@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    with closing(get_db()) as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email,)).fetchone()
        if not user or not verify_password(body.password, user["hashed_password"]):
            raise HTTPException(401, "Invalid email or password")
        
        token = create_token(body.email)
        return TokenResponse(access_token=token, username=user["username"])

@app.get("/me", response_model=UserMe)
def get_me(current = Depends(get_current_user)):
    return UserMe(username=current["username"], email=current["email"])

@app.post("/save-progress")
def save_progress(body: ProgressData, current = Depends(get_current_user)):
    with closing(get_db()) as conn:
        conn.execute(
            "UPDATE users SET progress = ? WHERE email = ?",
            (json.dumps(body.dict()), current["email"])
        )
        conn.commit()
    return {"message": "Progress saved"}

@app.get("/progress")
def get_progress(current = Depends(get_current_user)):
    with closing(get_db()) as conn:
        user = conn.execute("SELECT progress FROM users WHERE email = ?", (current["email"],)).fetchone()
        if not user or not user["progress"]:
            return {"progress": None}
        return {"progress": json.loads(user["progress"])}

# ═══════════════════════════════════════════
# GAME LOGIC
# ═══════════════════════════════════════════
def tile_at(r: int, c: int, rows: int, cols: int, pattern: int) -> str:
    if pattern == 1:
        d = (r + c) % 5
        return "red" if d == 0 else "blue" if d in (2, 4) else "green"
    else:
        cr = abs(r - (rows - 1) / 2)
        cc = abs(c - (cols - 1) / 2)
        return "blue" if (cr < 2 and cc < 2) else ("red" if (r % 3 == 0 and c % 3 == 0) else ("blue" if (r + c) % 2 == 0 else "green"))

@app.post("/generate-grid", response_model=GridResponse)
def generate_grid(body: GridRequest):
    rows, cols = max(body.rows, 5), max(body.cols, 5)
    grid, blue_count = [], 0
    for r in range(rows):
        row = []
        for c in range(cols):
            t = tile_at(r, c, rows, cols, body.pattern)
            if t == "blue": blue_count += 1
            row.append(t)
        grid.append(row)
    return GridResponse(grid=grid, rows=rows, cols=cols, blue_count=blue_count, pattern=body.pattern)

@app.get("/")
def root():
    return {"service": "Nexus Games API v3", "db_engine": "SQLite"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
