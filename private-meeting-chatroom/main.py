import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        """Accepts a connection and stores it."""
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        """Removes a connection from the repository."""
        if username in self.active_connections:
            del self.active_connections[username]

    async def broadcast(self, message: dict, exclude: str = None):
        """Sends JSON to all connections except the excluded one."""
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
        """Sends JSON to a specific user."""
        if username in self.active_connections:
            try:
                await self.active_connections[username].send_json(message)
            except Exception:
                self.disconnect(username)

    def online_users(self) -> list[str]:
        """Returns a list of currently connected usernames."""
        return list(self.active_connections.keys())

manager = ConnectionManager()

@app.get("/")
async def root():
    """Returns 404 as requested."""
    return Response(status_code=404)

@app.get("/chat")
async def get_chat():
    """Serves the chat HTML file."""
    chat_file = Path(__file__).parent / "chat.html"
    return HTMLResponse(content=chat_file.read_text())

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """Handles WebSocket lifecycle."""
    username = username.strip()
    if not username:
        await websocket.close(code=1008)
        return

    if username in manager.active_connections:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "message": "Username already taken..."
        })
        await websocket.close(code=1008)
        return

    await manager.connect(username, websocket)
    
    users = manager.online_users()
    await manager.broadcast({
        "type": "system",
        "message": f"{username} joined the chat",
        "users": users
    })
    
    await manager.send_to(username, {
        "type": "welcome",
        "message": f"Welcome, {username}!",
        "users": users
    })

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                message_text = payload.get("message", "").strip()
            except json.JSONDecodeError:
                message_text = data.strip()

            if not message_text:
                continue

            users = manager.online_users()
            await manager.broadcast({
                "type": "message",
                "from": username,
                "message": message_text,
                "users": users
            }, exclude=username)
            
    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast({
            "type": "system",
            "message": f"{username} left the chat",
            "users": manager.online_users()
        })
