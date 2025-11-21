# Quick Start Guide

Get your CCI Climate Monitoring system up and running in minutes.

## Prerequisites

- Raspberry Pi (3B+, 4, or 5)
- LoRa module connected to Pi
- Phone or computer for PWA access
- Same WiFi network for both devices

## Step 1: Set Up the Smart Node (Raspberry Pi)

```bash
# Clone or navigate to the project
cd CCI_Offline_AI/smart-node

# Create Python virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit LORA_PORT if needed

# Start the server
python main.py
```

The server will start on `http://0.0.0.0:8000`

## Step 2: Find Your Pi's IP Address

```bash
hostname -I
```

Note the first IP address (e.g., `192.168.1.100`)

## Step 3: Set Up the PWA Dashboard

On your computer or phone:

```bash
# Navigate to PWA directory
cd CCI_Offline_AI/pwa-dashboard

# Install dependencies
npm install

# Configure API endpoint
cp .env.example .env
nano .env  # Set VITE_API_URL to http://YOUR_PI_IP:8000

# Start development server
npm run dev
```

## Step 4: Access the Dashboard

Open your browser to `http://localhost:3000`

You should see:
- Current sensor readings (if sensors are transmitting)
- Real-time charts
- Connection status

## Step 5: Install as PWA (Optional)

### On Phone:
1. Open the dashboard in your mobile browser
2. Use "Add to Home Screen" option
3. Launch from your home screen like a native app

### On Desktop:
1. Look for the install icon in the address bar
2. Click to install
3. Launch from your applications

## Testing Without LoRa Sensors

You can test the system without physical sensors using the API:

```bash
# Send a test reading
curl -X POST http://localhost:8000/api/readings \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "TEST001",
    "temperature": 22.5,
    "humidity": 65,
    "air_quality": 45
  }'
```

The dashboard will update in real-time!

## Next Steps

### Run ML Analysis

In the PWA dashboard:
1. Click "Run Anomaly Detection" to detect outliers
2. Click "Run Trend Analysis" to identify patterns

### Add More Sensors

Configure your environmental LoRa nodes to send data in this format:

**JSON:**
```json
{"sensor_id": "ENV001", "temp": 22.5, "humidity": 65, "aqi": 45}
```

**Or CSV:**
```
ENV001,22.5,65,45
```

### Production Deployment

**Smart Node:**
```bash
# Set up systemd service (see smart-node/README.md)
sudo systemctl enable cci-smart-node
sudo systemctl start cci-smart-node
```

**PWA:**
```bash
# Build for production
cd pwa-dashboard
npm run build

# Deploy dist/ folder to your hosting service
```

## Troubleshooting

### "Cannot connect to API"
- Verify Pi IP address: `hostname -I`
- Check firewall: `sudo ufw allow 8000`
- Test API: `curl http://YOUR_PI_IP:8000/api/`

### "LoRa module not detected"
- Check serial port: `ls /dev/tty*`
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Verify LORA_PORT in `.env`

### Dashboard shows "No data"
- Send a test reading (see above)
- Check WebSocket connection in browser DevTools
- Verify CORS settings

## Architecture Overview

```
Environmental Sensors (LoRa)
         ↓
    Raspberry Pi (Smart Node)
    - Receives LoRa data
    - Runs ML models
    - Stores in SQLite
    - Serves REST API
    - Broadcasts WebSocket
         ↓
    PWA Dashboard (Phone/Browser)
    - Displays real-time data
    - Shows charts
    - Offline caching
```

## Support

- Smart Node API docs: `http://YOUR_PI_IP:8000/docs`
- Check logs: `tail -f smart-node/logs/*.log`
- GitHub Issues: [Link to your repo]

## What's Next?

- Add more environmental sensors
- Train custom TensorFlow Lite models
- Set up alerts and notifications
- Integrate with other services
- Add data export features

Happy monitoring!
