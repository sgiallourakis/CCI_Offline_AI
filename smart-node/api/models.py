from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SensorReading(BaseModel):
    sensor_id: str = Field(..., description="Unique sensor identifier")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    air_quality: Optional[float] = Field(None, description="Air Quality Index")
    rssi: Optional[int] = Field(None, description="Signal strength")

class ReadingResponse(SensorReading):
    id: int
    timestamp: str

class AnomalyResponse(BaseModel):
    id: int
    sensor_id: str
    reading_id: int
    anomaly_type: str
    severity: float
    detected_at: str

class TrendResponse(BaseModel):
    id: int
    sensor_id: str
    metric: str
    trend_direction: str
    slope: float
    calculated_at: str
    time_window: int

class SystemStateResponse(BaseModel):
    last_activity: str
    power_mode: str
    ml_last_run: Optional[str]
