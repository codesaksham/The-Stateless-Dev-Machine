import json
import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
    Response,
    Form,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
import crud
import auth
import database
from database import engine, get_db

# --- Template Caching ---

TEMPLATE_DIR = Path(__file__).parent
TEMPLATES: Dict[str, str] = {}


def load_templates():
    """Caches HTML templates to avoid repetitive disk I/O."""
    for name in ["login", "chat", "admin"]:
        path = TEMPLATE_DIR / f"{name}.html"
        if path.exists():
            TEMPLATES[name] = path.read_text(encoding="utf-8")
        else:
            TEMPLATES[name] = f"Template {name}.html not found"


# --- Connection Manager ---


class ConnectionManager:
    """Manages active WebSocket connections thread-safely."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def broadcast(self, message: dict, exclude: str = None):
        dead_connections = []
        for username, connection in self.active_connections.items():
            if username == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(username)

        for username in dead_connections:
            self.disconnect(username)

    async def send_to(self, username: str, message: dict):
        if connection := self.active_connections.get(username):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(username)

    def get_online_users(self) -> List[str]:
        return list(self.active_connections.keys())


manager = ConnectionManager()

# --- Lifespan & DB Init ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    load_templates()

    # Database initialization with retry logic
    retry_count = 10
    for i in range(retry_count):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.create_all)
            break
        except Exception as e:
            if i == retry_count - 1:
                raise e
            print(f"Database not ready, retrying in 2s... ({i+1}/{retry_count})")
            await asyncio.sleep(2)

    # Ensure default admin exists
    async with database.SessionLocal() as db:
        if not await crud.get_user_by_username(db, "admin"):
            await crud.create_user(
                db,
                schemas.UserCreate(username="admin", password="nimda", is_admin=True),
            )

    yield
    # Cleanup logic (if any) here


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

# --- Auth Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    payload = auth.decode_access_token(token)
    if not payload or not (username := payload.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


async def get_current_admin(user: models.User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user


# --- Routes: Pages ---


@app.get("/")
async def redirect_to_login():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return TEMPLATES.get("login", "Login page missing")


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return TEMPLATES.get("chat", "Chat page missing")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return TEMPLATES.get("admin", "Admin page missing")


# --- Routes: API ---


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users", response_model=List[schemas.UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db), _: models.User = Depends(get_current_admin)
):
    return await crud.get_users(db)


@app.post("/api/users", response_model=schemas.UserOut)
async def add_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if await crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    return await crud.create_user(db, user)


@app.delete("/api/users/{username}")
async def remove_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete super admin"
        )
    if not await crud.delete_user(db, username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"detail": "User deleted"}


# --- WebSocket ---


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = auth.decode_access_token(token)
    username = payload.get("sub") if payload else None

    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if username in manager.active_connections:
        await websocket.accept()
        await websocket.send_json(
            {"type": "error", "message": "Session already active in another tab"}
        )
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(username, websocket)

    users = manager.get_online_users()
    timestamp = datetime.now().strftime("%H:%M:%S")

    await manager.broadcast(
        {
            "type": "system",
            "message": f"{username} joined the chat",
            "users": users,
            "timestamp": timestamp,
        }
    )

    async with database.SessionLocal() as db:
        user = await crud.get_user_by_username(db, username)
        is_admin = user.is_admin if user else False

    await manager.send_to(
        username,
        {
            "type": "welcome",
            "message": f"Welcome, {username}!",
            "users": users,
            "is_admin": is_admin,
            "timestamp": timestamp,
        },
    )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_text = json.loads(data).get("message", "").strip()
            except (json.JSONDecodeError, TypeError):
                message_text = data.strip()

            if not message_text:
                continue

            await manager.broadcast(
                {
                    "type": "message",
                    "from": username,
                    "message": message_text,
                    "users": manager.get_online_users(),
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                },
                exclude=username,
            )

    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast(
            {
                "type": "system",
                "message": f"{username} left the chat",
                "users": manager.get_online_users(),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )


# --- Local Execution ---

if __name__ == "__main__":
    import uvicorn

    # Check for SSL certificates in certs/ directory
    cert_path = Path("certs/cert.pem")
    key_path = Path("certs/key.pem")

    ssl_config = {}
    if cert_path.exists() and key_path.exists():
        print(f"🔒 Starting secure server on https://0.0.0.0:8999")
        ssl_config = {"ssl_certfile": str(cert_path), "ssl_keyfile": str(key_path)}
    else:
        print(
            f"🔓 Starting server on http://0.0.0.0:8999 (Certs not found in ./certs/)"
        )

    uvicorn.run("main:app", host="0.0.0.0", port=8999, reload=True, **ssl_config)
