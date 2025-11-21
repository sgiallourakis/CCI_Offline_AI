# Smart Node (Raspberry Pi)

Backend service for climate data monitoring with ML analytics.

## Features

- FastAPI REST API and WebSocket server
- SQLite database for sensor readings
- LoRa receiver integration for environmental sensors
- ML-powered anomaly detection and trend analysis
- Power management with idle detection
- Real-time data streaming via WebSockets

## Hardware Requirements

- Raspberry Pi (3B+, 4, or 5 recommended)
- LoRa module (RFM95, SX1276, or compatible)
- Connected via USB or GPIO pins

## Installation

### 1. Install Python Dependencies

```bash
cd smart-node
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `LORA_PORT`: Serial port for LoRa module (e.g., `/dev/ttyUSB0`, `/dev/ttyAMA0`)
- `PORT`: API server port (default: 8000)
- `IDLE_TIMEOUT`: Seconds before entering idle mode (default: 300)

### 3. Test LoRa Connection

```bash
# List available serial ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

### 4. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Readings
- `GET /api/readings` - Get sensor readings
  - Query params: `limit`, `sensor_id`, `hours`
- `POST /api/readings` - Create reading (for testing)

### Sensors
- `GET /api/sensors` - List all sensor IDs

### Anomalies
- `GET /api/anomalies` - Get detected anomalies
- `POST /api/analyze/anomalies` - Run anomaly detection

### Trends
- `GET /api/trends` - Get trend analysis results
- `POST /api/analyze/trends` - Run trend analysis

### System
- `GET /api/system/state` - Get system state and power mode
- `POST /api/system/wake` - Wake system from idle

### WebSocket
- `WS /ws` - Real-time data streaming

## LoRa Message Format

The system expects JSON or CSV formatted messages:

**JSON Format:**
```json
{"sensor_id": "ENV001", "temp": 22.5, "humidity": 65, "aqi": 45, "rssi": -80}
```

**CSV Format:**
```
ENV001,22.5,65,45,-80
```

Fields: `sensor_id, temperature, humidity, air_quality, rssi`

## ML Models

The system uses statistical methods for:
- **Anomaly Detection**: Z-score based outlier detection
- **Trend Analysis**: Linear regression for trend identification

Future: TensorFlow Lite models for advanced time series analysis.

## Auto-Start on Boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/cci-smart-node.service
```

```ini
[Unit]
Description=CCI Smart Node
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CCI_Offline_AI/smart-node
Environment="PATH=/home/pi/CCI_Offline_AI/smart-node/venv/bin"
ExecStart=/home/pi/CCI_Offline_AI/smart-node/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cci-smart-node
sudo systemctl start cci-smart-node
```

## Troubleshooting

### LoRa module not detected
- Check serial port permissions: `sudo usermod -a -G dialout $USER`
- Verify correct port in `.env`
- Test with: `screen /dev/ttyUSB0 115200`

### Database errors
- Ensure write permissions: `chmod 755 db/`
- Delete and reinitialize: `rm db/climate.db && python main.py`

### High CPU usage
- Increase `IDLE_TIMEOUT` in `.env`
- Reduce WebSocket broadcast frequency
