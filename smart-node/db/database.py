import aiosqlite
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "./db/climate.db"):
        self.db_path = db_path
        self.connection = None

    async def initialize(self):
        """Initialize database and create tables"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row

        # Read and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema = f.read()
        await self.connection.executescript(schema)
        await self.connection.commit()

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()

    async def insert_reading(self, sensor_id: str, temperature: float,
                            humidity: float, air_quality: float, rssi: int = None) -> int:
        """Insert a new sensor reading"""
        cursor = await self.connection.execute(
            """INSERT INTO sensor_readings (sensor_id, temperature, humidity, air_quality, rssi)
               VALUES (?, ?, ?, ?, ?)""",
            (sensor_id, temperature, humidity, air_quality, rssi)
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def get_recent_readings(self, limit: int = 100, sensor_id: Optional[str] = None) -> List[Dict]:
        """Get recent sensor readings"""
        if sensor_id:
            cursor = await self.connection.execute(
                """SELECT * FROM sensor_readings
                   WHERE sensor_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (sensor_id, limit)
            )
        else:
            cursor = await self.connection.execute(
                """SELECT * FROM sensor_readings
                   ORDER BY timestamp DESC LIMIT ?""",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_readings_in_range(self, start_time: datetime, end_time: datetime,
                                   sensor_id: Optional[str] = None) -> List[Dict]:
        """Get sensor readings within a time range"""
        if sensor_id:
            cursor = await self.connection.execute(
                """SELECT * FROM sensor_readings
                   WHERE sensor_id = ? AND timestamp BETWEEN ? AND ?
                   ORDER BY timestamp ASC""",
                (sensor_id, start_time.isoformat(), end_time.isoformat())
            )
        else:
            cursor = await self.connection.execute(
                """SELECT * FROM sensor_readings
                   WHERE timestamp BETWEEN ? AND ?
                   ORDER BY timestamp ASC""",
                (start_time.isoformat(), end_time.isoformat())
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def insert_anomaly(self, sensor_id: str, reading_id: int,
                            anomaly_type: str, severity: float):
        """Insert detected anomaly"""
        await self.connection.execute(
            """INSERT INTO anomalies (sensor_id, reading_id, anomaly_type, severity)
               VALUES (?, ?, ?, ?)""",
            (sensor_id, reading_id, anomaly_type, severity)
        )
        await self.connection.commit()

    async def get_anomalies(self, limit: int = 50) -> List[Dict]:
        """Get recent anomalies"""
        cursor = await self.connection.execute(
            """SELECT a.*, s.temperature, s.humidity, s.air_quality, s.timestamp
               FROM anomalies a
               JOIN sensor_readings s ON a.reading_id = s.id
               ORDER BY a.detected_at DESC LIMIT ?""",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def insert_trend(self, sensor_id: str, metric: str,
                          trend_direction: str, slope: float, time_window: int):
        """Insert trend analysis result"""
        await self.connection.execute(
            """INSERT INTO trends (sensor_id, metric, trend_direction, slope, time_window)
               VALUES (?, ?, ?, ?, ?)""",
            (sensor_id, metric, trend_direction, slope, time_window)
        )
        await self.connection.commit()

    async def get_latest_trends(self, sensor_id: Optional[str] = None) -> List[Dict]:
        """Get latest trend analysis"""
        if sensor_id:
            cursor = await self.connection.execute(
                """SELECT * FROM trends
                   WHERE sensor_id = ?
                   ORDER BY calculated_at DESC LIMIT 3""",
                (sensor_id,)
            )
        else:
            cursor = await self.connection.execute(
                """SELECT * FROM trends
                   ORDER BY calculated_at DESC LIMIT 10"""
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def update_activity(self):
        """Update last activity timestamp"""
        await self.connection.execute(
            """UPDATE system_state SET last_activity = CURRENT_TIMESTAMP WHERE id = 1"""
        )
        await self.connection.commit()

    async def get_system_state(self) -> Dict:
        """Get current system state"""
        cursor = await self.connection.execute(
            """SELECT * FROM system_state WHERE id = 1"""
        )
        row = await cursor.fetchone()
        return dict(row) if row else {}

    async def update_power_mode(self, mode: str):
        """Update system power mode"""
        await self.connection.execute(
            """UPDATE system_state SET power_mode = ? WHERE id = 1""",
            (mode,)
        )
        await self.connection.commit()
