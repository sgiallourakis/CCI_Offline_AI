from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections for real-time data streaming"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_reading(self, reading: dict):
        """Send sensor reading to all clients"""
        message = {
            "type": "reading",
            "data": reading
        }
        await self.broadcast(message)

    async def send_anomaly(self, anomaly: dict):
        """Send anomaly alert to all clients"""
        message = {
            "type": "anomaly",
            "data": anomaly
        }
        await self.broadcast(message)

    async def send_trend(self, trend: dict):
        """Send trend update to all clients"""
        message = {
            "type": "trend",
            "data": trend
        }
        await self.broadcast(message)

    async def send_system_status(self, status: dict):
        """Send system status update to all clients"""
        message = {
            "type": "system_status",
            "data": status
        }
        await self.broadcast(message)

# Global connection manager instance
manager = ConnectionManager()
