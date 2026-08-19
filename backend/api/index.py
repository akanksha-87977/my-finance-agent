import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_PATH = "/tmp/financial_ai_vercel.sqlite3"
FRONTEND_ORIGIN = "https://frontend-alpha-six-62.vercel.app"

app = FastAPI(title="Financial AI Platform API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )"""
    )
    connection.commit()
    return connection


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":", 1)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=16384, r=8, p=1)
    return hmac.compare_digest(digest.hex(), digest_hex)


def user_response(row):
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "full_name": row["full_name"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


@app.get("/")
def root():
    return {"message": "Welcome to Financial AI Platform API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Financial AI Platform", "version": "1.0.0"}


@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO users (email, username, password_hash, full_name, created_at) VALUES (?, ?, ?, ?, ?)",
            (payload.email, payload.username, hash_password(payload.password), payload.full_name, datetime.utcnow().isoformat()),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return user_response(row)
    except sqlite3.IntegrityError as error:
        field = "Email" if "email" in str(error).lower() else "Username"
        raise HTTPException(status_code=400, detail=f"{field} already registered")
    finally:
        connection.close()


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    connection = get_connection()
    try:
        row = connection.execute("SELECT * FROM users WHERE username = ?", (payload.username,)).fetchone()
        if not row or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        return {"access_token": f"vercel-session-{row['id']}", "token_type": "bearer"}
    finally:
        connection.close()
