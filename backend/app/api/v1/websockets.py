"""
WebSocket Endpoints
Real-time updates for pipeline executions
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi import status

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class ConnectionManager:
    """Manages WebSocket connections for pipeline executions."""
    
    def __init__(self):
        # Map execution_id to list of WebSockets
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, execution_id: str):
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = []
        self.active_connections[execution_id].append(websocket)
        logger.info("websocket_connected", execution_id=execution_id)

    def disconnect(self, websocket: WebSocket, execution_id: str):
        if execution_id in self.active_connections:
            if websocket in self.active_connections[execution_id]:
                self.active_connections[execution_id].remove(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
        logger.info("websocket_disconnected", execution_id=execution_id)

    async def broadcast(self, message: dict, execution_id: str):
        if execution_id in self.active_connections:
            for connection in self.active_connections[execution_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("websocket_send_error", error=str(e))


manager = ConnectionManager()


@router.websocket("/executions/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for streaming execution updates.
    Authenticated via Ticket/Token in query param (TODO)
    """
    await manager.connect(websocket, execution_id)
    try:
        while True:
            # Keep connection alive, maybe receive commands (cancel, etc.)
            data = await websocket.receive_text()
            # Echo for now or handle client messages
            await websocket.send_json({"message": "received", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, execution_id)
    except Exception as e:
        logger.error("websocket_error", error=str(e), execution_id=execution_id)
        manager.disconnect(websocket, execution_id)
