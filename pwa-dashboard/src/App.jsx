import { useState, useEffect, useRef } from 'preact/hooks';
import { api } from './api';
import { WS_URL, POLL_INTERVAL, RECONNECT_INTERVAL, DEFAULT_HOURS } from './config';
import { SensorCard } from './components/SensorCard';
import { Chart } from './components/Chart';

export function App() {
  const [readings, setReadings] = useState([]);
  const [latestReadings, setLatestReadings] = useState({});
  const [anomalies, setAnomalies] = useState([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Fetch initial data
  const fetchData = async () => {
    try {
      const [readingsData, anomaliesData] = await Promise.all([
        api.getReadings(50, selectedSensor, DEFAULT_HOURS),
        api.getAnomalies(10),
      ]);

      setReadings(readingsData);
      setAnomalies(anomaliesData);

      // Group latest readings by sensor
      const latest = {};
      readingsData.forEach(reading => {
        if (!latest[reading.sensor_id] ||
            new Date(reading.timestamp) > new Date(latest[reading.sensor_id].timestamp)) {
          latest[reading.sensor_id] = reading;
        }
      });
      setLatestReadings(latest);

      setError(null);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data. Check connection to smart node.');
      setLoading(false);
    }
  };

  // Connect to WebSocket
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'reading' && message.data) {
            // Add new reading to list
            setReadings(prev => [message.data, ...prev].slice(0, 50));

            // Update latest readings
            setLatestReadings(prev => ({
              ...prev,
              [message.data.sensor_id]: message.data,
            }));
          } else if (message.type === 'anomaly' && message.data) {
            setAnomalies(prev => [message.data, ...prev].slice(0, 10));
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        wsRef.current = null;

        // Attempt reconnection
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, RECONNECT_INTERVAL);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, RECONNECT_INTERVAL);
    }
  };

  // Run anomaly detection
  const runAnomalyDetection = async () => {
    setAnalyzing(true);
    try {
      const result = await api.runAnomalyDetection(selectedSensor, DEFAULT_HOURS);
      console.log('Anomaly detection result:', result);
      await fetchData(); // Refresh data
    } catch (err) {
      console.error('Failed to run anomaly detection:', err);
    }
    setAnalyzing(false);
  };

  // Run trend analysis
  const runTrendAnalysis = async () => {
    setAnalyzing(true);
    try {
      const result = await api.runTrendAnalysis(selectedSensor, DEFAULT_HOURS);
      console.log('Trend analysis result:', result);
    } catch (err) {
      console.error('Failed to run trend analysis:', err);
    }
    setAnalyzing(false);
  };

  // Initial load
  useEffect(() => {
    fetchData();
    connectWebSocket();

    // Poll for data as fallback
    const pollInterval = setInterval(fetchData, POLL_INTERVAL);

    return () => {
      clearInterval(pollInterval);
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [selectedSensor]);

  if (loading) {
    return (
      <div class="app">
        <div class="loading">Loading climate data...</div>
      </div>
    );
  }

  const sensorIds = Object.keys(latestReadings);

  return (
    <div class="app">
      <header class="header">
        <h1>CCI Climate Monitor</h1>
        <div class="status">
          <span class={`status-badge ${connected ? 'online' : 'offline'}`}>
            {connected ? 'Connected' : 'Offline'}
          </span>
          <span class="status-badge">{sensorIds.length} Sensors</span>
        </div>
      </header>

      {error && <div class="error">{error}</div>}

      <div class="controls">
        <button
          class="btn btn-primary"
          onClick={runAnomalyDetection}
          disabled={analyzing}
        >
          {analyzing ? 'Analyzing...' : 'Run Anomaly Detection'}
        </button>
        <button
          class="btn btn-primary"
          onClick={runTrendAnalysis}
          disabled={analyzing}
        >
          {analyzing ? 'Analyzing...' : 'Run Trend Analysis'}
        </button>
        <button class="btn btn-secondary" onClick={fetchData}>
          Refresh Data
        </button>
      </div>

      <div class="sensor-grid">
        {sensorIds.map(sensorId => (
          <SensorCard key={sensorId} reading={latestReadings[sensorId]} />
        ))}
      </div>

      {readings.length > 0 && (
        <>
          <div class="chart-container">
            <h2>Temperature History</h2>
            <Chart
              data={readings.slice().reverse()}
              title="Temperature"
              metric="temperature"
            />
          </div>

          <div class="chart-container">
            <h2>Humidity History</h2>
            <Chart
              data={readings.slice().reverse()}
              title="Humidity"
              metric="humidity"
            />
          </div>

          <div class="chart-container">
            <h2>Air Quality History</h2>
            <Chart
              data={readings.slice().reverse()}
              title="Air Quality"
              metric="air_quality"
            />
          </div>
        </>
      )}

      {anomalies.length > 0 && (
        <div class="anomaly-list">
          <h2>Recent Anomalies</h2>
          {anomalies.map((anomaly, idx) => (
            <div key={idx} class="anomaly-item">
              <strong>Sensor {anomaly.sensor_id}</strong> - {anomaly.anomaly_type}
              <br />
              Severity: {(anomaly.severity * 100).toFixed(0)}% at{' '}
              {new Date(anomaly.detected_at).toLocaleString()}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
