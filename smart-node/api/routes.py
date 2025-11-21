from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from .models import (
    SensorReading, ReadingResponse, AnomalyResponse,
    TrendResponse, SystemStateResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Database and analyzer will be injected via app state
def get_db():
    from main import app
    return app.state.db

def get_analyzer():
    from main import app
    return app.state.analyzer

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "service": "CCI Smart Node API"}

@router.post("/readings", response_model=ReadingResponse)
async def create_reading(reading: SensorReading):
    """Create a new sensor reading (primarily for testing, LoRa is main input)"""
    db = get_db()
    await db.update_activity()

    reading_id = await db.insert_reading(
        sensor_id=reading.sensor_id,
        temperature=reading.temperature,
        humidity=reading.humidity,
        air_quality=reading.air_quality,
        rssi=reading.rssi
    )

    # Return the created reading
    readings = await db.get_recent_readings(limit=1)
    if readings:
        return ReadingResponse(**readings[0])

    raise HTTPException(status_code=500, detail="Failed to create reading")

@router.get("/readings", response_model=List[ReadingResponse])
async def get_readings(
    limit: int = Query(100, ge=1, le=1000),
    sensor_id: Optional[str] = None,
    hours: Optional[int] = Query(None, ge=1, le=168)  # Max 1 week
):
    """Get sensor readings"""
    db = get_db()
    await db.update_activity()

    if hours:
        # Get readings from last N hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        readings = await db.get_readings_in_range(start_time, end_time, sensor_id)
    else:
        # Get recent readings
        readings = await db.get_recent_readings(limit, sensor_id)

    return [ReadingResponse(**r) for r in readings]

@router.get("/sensors")
async def get_sensors():
    """Get list of all sensor IDs"""
    db = get_db()
    await db.update_activity()

    readings = await db.get_recent_readings(limit=1000)
    sensors = list(set(r['sensor_id'] for r in readings))

    return {"sensors": sensors, "count": len(sensors)}

@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(limit: int = Query(50, ge=1, le=500)):
    """Get detected anomalies"""
    db = get_db()
    await db.update_activity()

    anomalies = await db.get_anomalies(limit)
    return [AnomalyResponse(**a) for a in anomalies]

@router.post("/analyze/anomalies")
async def run_anomaly_detection(
    sensor_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Run anomaly detection on recent data"""
    db = get_db()
    analyzer = get_analyzer()
    await db.update_activity()

    # Get recent readings
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    readings = await db.get_readings_in_range(start_time, end_time, sensor_id)

    if len(readings) < 10:
        return {"message": "Not enough data for analysis", "anomalies_detected": 0}

    # Run anomaly detection
    anomalies = analyzer.detect_anomalies(readings)

    # Store anomalies in database
    for anomaly in anomalies:
        await db.insert_anomaly(
            sensor_id=anomaly['sensor_id'],
            reading_id=anomaly['reading_id'],
            anomaly_type=anomaly['anomaly_type'],
            severity=anomaly['severity']
        )

    return {
        "message": "Anomaly detection completed",
        "anomalies_detected": len(anomalies),
        "data_points_analyzed": len(readings)
    }

@router.get("/trends", response_model=List[TrendResponse])
async def get_trends(sensor_id: Optional[str] = None):
    """Get trend analysis results"""
    db = get_db()
    await db.update_activity()

    trends = await db.get_latest_trends(sensor_id)
    return [TrendResponse(**t) for t in trends]

@router.post("/analyze/trends")
async def run_trend_analysis(
    sensor_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Run trend analysis on recent data"""
    db = get_db()
    analyzer = get_analyzer()
    await db.update_activity()

    # Get recent readings
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    readings = await db.get_readings_in_range(start_time, end_time, sensor_id)

    if len(readings) < 5:
        return {"message": "Not enough data for analysis", "trends_calculated": 0}

    # Run trend analysis
    trends = analyzer.analyze_trends(readings, hours)

    # Store trends in database
    for trend in trends:
        await db.insert_trend(
            sensor_id=trend['sensor_id'],
            metric=trend['metric'],
            trend_direction=trend['trend_direction'],
            slope=trend['slope'],
            time_window=trend['time_window']
        )

    return {
        "message": "Trend analysis completed",
        "trends_calculated": len(trends),
        "data_points_analyzed": len(readings)
    }

@router.get("/system/state", response_model=SystemStateResponse)
async def get_system_state():
    """Get system state and power mode"""
    db = get_db()
    state = await db.get_system_state()
    return SystemStateResponse(**state)

@router.post("/system/wake")
async def wake_system():
    """Wake system from idle/sleep mode"""
    db = get_db()
    await db.update_power_mode('active')
    await db.update_activity()
    return {"message": "System awakened", "power_mode": "active"}
