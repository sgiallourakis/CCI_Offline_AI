export function SensorCard({ reading }) {
  if (!reading) {
    return (
      <div class="sensor-card">
        <div class="loading">No data</div>
      </div>
    );
  }

  const formatValue = (value, unit) => {
    if (value === null || value === undefined) return 'N/A';
    return `${value.toFixed(1)}${unit}`;
  };

  const getAQIColor = (aqi) => {
    if (aqi === null) return '#94a3b8';
    if (aqi <= 50) return '#10b981'; // Good
    if (aqi <= 100) return '#f59e0b'; // Moderate
    if (aqi <= 150) return '#ef4444'; // Unhealthy for sensitive
    return '#7f1d1d'; // Unhealthy
  };

  return (
    <div class="sensor-card">
      <h3>Sensor {reading.sensor_id}</h3>

      <div class="metric">
        <span class="metric-label">Temperature</span>
        <span class="metric-value">{formatValue(reading.temperature, '°C')}</span>
      </div>

      <div class="metric">
        <span class="metric-label">Humidity</span>
        <span class="metric-value">{formatValue(reading.humidity, '%')}</span>
      </div>

      <div class="metric">
        <span class="metric-label">Air Quality</span>
        <span
          class="metric-value"
          style={{ color: getAQIColor(reading.air_quality) }}
        >
          {formatValue(reading.air_quality, ' AQI')}
        </span>
      </div>

      {reading.rssi && (
        <div class="metric">
          <span class="metric-label">Signal</span>
          <span class="metric-value">{reading.rssi} dBm</span>
        </div>
      )}

      <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: '#64748b' }}>
        Last updated: {new Date(reading.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}
