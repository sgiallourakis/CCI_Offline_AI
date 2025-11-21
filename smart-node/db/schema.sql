-- Climate sensor data table
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    air_quality REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    rssi INTEGER,  -- LoRa signal strength
    INDEX idx_sensor_timestamp (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- Anomaly detection results
CREATE TABLE IF NOT EXISTS anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    reading_id INTEGER,
    anomaly_type TEXT,  -- 'temperature', 'humidity', 'air_quality'
    severity REAL,  -- 0.0 to 1.0
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES sensor_readings(id)
);

-- Trend analysis cache
CREATE TABLE IF NOT EXISTS trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    metric TEXT,  -- 'temperature', 'humidity', 'air_quality'
    trend_direction TEXT,  -- 'increasing', 'decreasing', 'stable'
    slope REAL,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_window INTEGER  -- hours of data analyzed
);

-- System state for power management
CREATE TABLE IF NOT EXISTS system_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    power_mode TEXT DEFAULT 'active',  -- 'active', 'idle', 'sleep'
    ml_last_run DATETIME
);

-- Initialize system state
INSERT OR IGNORE INTO system_state (id, last_activity, power_mode) VALUES (1, CURRENT_TIMESTAMP, 'active');
