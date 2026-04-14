from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
from typing import Dict

from db import get_db, get_scan

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, scan_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[scan_id] = websocket
    
    def disconnect(self, scan_id: int):
        if scan_id in self.active_connections:
            del self.active_connections[scan_id]
    
    async def send_message(self, scan_id: int, message: dict):
        if scan_id in self.active_connections:
            try:
                await self.active_connections[scan_id].send_json(message)
            except:
                pass

manager = ConnectionManager()

@websocket.websocket("/ws/scan/{scan_id}")
async def websocket_endpoint(scan_id: int, websocket: WebSocket):
    await manager.connect(scan_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(scan_id)

@router.get("/tools/available")
async def get_available_tools():
    from tools import get_available_tools
    return get_available_tools()

async def broadcast_tool_start(scan_id: int, tool: str):
    await manager.send_message(scan_id, {
        "type": "tool_start",
        "tool": tool,
        "message": f"Running {tool}..."
    })

async def broadcast_tool_output(scan_id: int, tool: str, line: str):
    await manager.send_message(scan_id, {
        "type": "tool_output",
        "tool": tool,
        "line": line
    })

async def broadcast_tool_done(scan_id: int, tool: str, duration: float):
    await manager.send_message(scan_id, {
        "type": "tool_done",
        "tool": tool,
        "duration": duration
    })

async def broadcast_llm_start(scan_id: int):
    await manager.send_message(scan_id, {
        "type": "llm_start",
        "message": "Sending results to AI..."
    })

async def broadcast_llm_done(scan_id: int):
    await manager.send_message(scan_id, {
        "type": "llm_done",
        "message": "Analysis complete"
    })

async def broadcast_scan_complete(scan_id: int, risk: str):
    await manager.send_message(scan_id, {
        "type": "scan_complete",
        "scan_id": scan_id,
        "risk": risk
    })

async def broadcast_error(scan_id: int, tool: str, message: str):
    await manager.send_message(scan_id, {
        "type": "error",
        "tool": tool,
        "message": message
    })