# PWA Dashboard

Progressive Web App for mobile climate monitoring.

## Features

- Real-time sensor data visualization
- Interactive charts for temperature, humidity, and air quality
- WebSocket connection for live updates
- Offline support with service worker caching
- Responsive design for mobile devices
- Anomaly alerts and trend analysis
- Lightweight (Preact + Chart.js)

## Installation

### 1. Install Dependencies

```bash
cd pwa-dashboard
npm install
```

### 2. Configure API Endpoint

Create `.env` file:
```bash
VITE_API_URL=http://192.168.1.100:8000
VITE_WS_URL=ws://192.168.1.100:8000/ws
```

Replace `192.168.1.100` with your Raspberry Pi's IP address.

### 3. Development Mode

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

### 4. Production Build

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Deployment

### Option 1: Serve from Raspberry Pi

```bash
# Build the PWA
npm run build

# Copy to Pi
scp -r dist/* pi@192.168.1.100:/var/www/html/

# Or serve with Python
cd dist
python -m http.server 3000
```

### Option 2: Static Hosting

Deploy `dist/` folder to:
- Netlify
- Vercel
- GitHub Pages
- Any static host

## Installing as PWA

### On Android
1. Open the dashboard in Chrome
2. Tap the menu (three dots)
3. Select "Add to Home Screen"
4. The app will install and appear on your home screen

### On iOS
1. Open the dashboard in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add"

## Offline Support

The PWA caches data for offline viewing:
- Last 50 sensor readings
- Recent anomalies
- Application assets

When offline, the app will display cached data and automatically sync when reconnected.

## Features Overview

### Real-Time Monitoring
- WebSocket connection for instant updates
- Automatic reconnection on disconnect
- Live sensor cards with current readings

### Data Visualization
- Temperature history chart
- Humidity history chart
- Air quality history chart
- Interactive Chart.js graphs

### ML Analytics
- Run anomaly detection on demand
- View trend analysis results
- Anomaly severity indicators
- Color-coded air quality levels

## Customization

### Styling
Edit [src/style.css](src/style.css) to customize colors and layout.

### Update Intervals
Edit [src/config.js](src/config.js):
```javascript
export const POLL_INTERVAL = 5000; // 5 seconds
export const MAX_CHART_POINTS = 50; // Max chart data points
```

### API Configuration
Edit [src/config.js](src/config.js) or use environment variables.

## Troubleshooting

### Cannot connect to API
- Verify Raspberry Pi IP address
- Check firewall settings on Pi
- Ensure smart node is running: `curl http://192.168.1.100:8000/api/`

### WebSocket connection fails
- Check CORS configuration in smart node
- Verify WebSocket URL includes `ws://` not `http://`
- Test WebSocket: Use browser DevTools Network tab

### PWA not installing
- Ensure HTTPS (or localhost for development)
- Check manifest.json is accessible
- Verify service worker registration in DevTools

### Charts not displaying
- Open browser console for errors
- Ensure Chart.js is loaded
- Check data format from API

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 11.3+)
- Opera: Full support

## Performance

Built bundle size:
- JS: ~50KB gzipped (Preact + Chart.js)
- CSS: ~5KB gzipped
- Total: ~55KB gzipped

First load: <1 second on 3G
Subsequent loads: Instant (cached)
