# CCI_Offline_AI

This repository holds everything related to our Offline AI network. Code for our microcontroller smart nodes, anything related to our LoRa sensors, and everything related to our larger Heavy Nodes (Raspberry Pi, Jetson).

## Project Overview

A dual-dashboard system for climate data monitoring with ML-powered analytics.

### Architecture

**Smart Node (Raspberry Pi - Heavy Node)**
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **ML:** TensorFlow Lite for time series, anomaly detection, trend analysis
- **Communication:** REST API, WebSockets, LoRa receiver
- **Power:** Idle detection with automatic sleep/wake

**PWA Dashboard (Mobile)**
- **Frontend:** Preact + Chart.js
- **Features:** Data visualization, offline caching, real-time updates
- **Communication:** WiFi (WebSocket/REST), LoRa (future)

**Environmental Sensors**
- Remote LoRa nodes transmitting climate data
- Metrics: Temperature, Humidity, Air Quality, Sensor ID

## Project Structure

```
├── smart-node/          # Raspberry Pi backend
│   ├── api/            # FastAPI application
│   ├── db/             # SQLite database
│   ├── ml/             # TensorFlow Lite models
│   └── lora/           # LoRa receiver integration
└── pwa-dashboard/       # Mobile PWA frontend
    ├── src/            # Preact components
    ├── public/         # Static assets
    └── sw.js           # Service worker for offline support
```

## Getting Started

### Smart Node Setup
```bash
cd smart-node
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### PWA Development
```bash
cd pwa-dashboard
npm install
npm run dev
```

## Features

- Real-time climate data monitoring
- Historical data visualization with graphs
- Anomaly detection and trend analysis
- Offline data caching
- Low-power operation with automatic sleep/wake
- LoRa and WiFi connectivity
