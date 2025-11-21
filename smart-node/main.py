import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from db.database import Database
from ml.analyzer import ClimateAnalyzer
from lora.receiver import LoRaReceiver
from api import router, manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DB_PATH = os.getenv("DB_PATH", "./db/climate.db")
LORA_PORT = os.getenv("LORA_PORT", "/dev/ttyUSB0")
LORA_BAUDRATE = int(os.getenv("LORA_BAUDRATE", 115200))
IDLE_TIMEOUT = int(os.getenv("IDLE_TIMEOUT", 300))

# Background task for LoRa listening
lora_task = None

async def handle_lora_data(data: dict):
    """Callback for processing LoRa data"""
    try:
        logger.info(f"Received LoRa data: {data}")

        # Store in database
        db = app.state.db
        reading_id = await db.insert_reading(
            sensor_id=data['sensor_id'],
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            air_quality=data.get('air_quality'),
            rssi=data.get('rssi')
        )

        # Add reading_id to data for WebSocket broadcast
        data['id'] = reading_id
        data['timestamp'] = 'now'  # Will be replaced with actual timestamp

        # Broadcast to WebSocket clients
        await manager.send_reading(data)

        # Update activity
        await db.update_activity()

    except Exception as e:
        logger.error(f"Error handling LoRa data: {e}")

async def start_lora_listener():
    """Start LoRa receiver in background"""
    lora = app.state.lora
    if lora.connect():
        lora.set_callback(handle_lora_data)
        await lora.start_listening()
    else:
        logger.warning("Could not connect to LoRa module - running without LoRa")

async def power_management_task():
    """Monitor system activity and manage power states"""
    db = app.state.db
    while True:
        try:
            state = await db.get_system_state()
            last_activity = state.get('last_activity')
            current_mode = state.get('power_mode')

            if last_activity and current_mode == 'active':
                # Check if we should enter idle mode
                from datetime import datetime
                last_time = datetime.fromisoformat(last_activity)
                idle_seconds = (datetime.now() - last_time).total_seconds()

                if idle_seconds > IDLE_TIMEOUT:
                    logger.info("Entering idle mode due to inactivity")
                    await db.update_power_mode('idle')
                    await manager.send_system_status({
                        'power_mode': 'idle',
                        'idle_seconds': idle_seconds
                    })

        except Exception as e:
            logger.error(f"Error in power management: {e}")

        # Check every 30 seconds
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CCI Smart Node...")

    # Initialize database
    db = Database(DB_PATH)
    await db.initialize()
    app.state.db = db
    logger.info("Database initialized")

    # Initialize ML analyzer
    analyzer = ClimateAnalyzer()
    app.state.analyzer = analyzer
    logger.info("ML Analyzer initialized")

    # Initialize LoRa receiver
    lora = LoRaReceiver(port=LORA_PORT, baudrate=LORA_BAUDRATE)
    app.state.lora = lora

    # Start background tasks
    global lora_task
    lora_task = asyncio.create_task(start_lora_listener())

    power_task = asyncio.create_task(power_management_task())

    logger.info(f"Server running on {HOST}:{PORT}")

    yield

    # Shutdown
    logger.info("Shutting down CCI Smart Node...")

    # Stop LoRa receiver
    lora.stop()
    lora.disconnect()
    if lora_task:
        lora_task.cancel()

    power_task.cancel()

    # Close database
    await db.close()

# Create FastAPI app
app = FastAPI(
    title="CCI Smart Node API",
    description="Climate monitoring smart node with ML analytics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for PWA access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.debug(f"Received from client: {data}")

            # Update activity on any WebSocket message
            await app.state.db.update_activity()

            # Echo back for now (can be extended for commands)
            await websocket.send_json({"type": "ack", "message": "received"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # Set to True for development
        log_level="info"
    )
