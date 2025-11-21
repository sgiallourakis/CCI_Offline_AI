import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ClimateAnalyzer:
    """
    Lightweight ML analyzer for climate data
    Performs anomaly detection and trend analysis without heavy TFLite models initially
    """

    def __init__(self):
        self.temperature_bounds = (0, 50)  # Celsius
        self.humidity_bounds = (0, 100)  # Percent
        self.aqi_bounds = (0, 500)  # AQI scale

    def detect_anomalies(self, readings: List[Dict]) -> List[Dict]:
        """
        Detect anomalies using statistical methods (Z-score)
        Returns list of anomalies with severity scores
        """
        if len(readings) < 10:
            logger.warning("Not enough data for anomaly detection")
            return []

        anomalies = []

        # Extract metrics
        temps = [r['temperature'] for r in readings if r['temperature'] is not None]
        hums = [r['humidity'] for r in readings if r['humidity'] is not None]
        aqis = [r['air_quality'] for r in readings if r['air_quality'] is not None]

        # Detect temperature anomalies
        if temps:
            temp_anomalies = self._detect_zscore_anomalies(
                temps, readings, 'temperature', threshold=2.5
            )
            anomalies.extend(temp_anomalies)

        # Detect humidity anomalies
        if hums:
            hum_anomalies = self._detect_zscore_anomalies(
                hums, readings, 'humidity', threshold=2.5
            )
            anomalies.extend(hum_anomalies)

        # Detect air quality anomalies
        if aqis:
            aqi_anomalies = self._detect_zscore_anomalies(
                aqis, readings, 'air_quality', threshold=2.5
            )
            anomalies.extend(aqi_anomalies)

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def _detect_zscore_anomalies(self, values: List[float], readings: List[Dict],
                                 metric: str, threshold: float = 2.5) -> List[Dict]:
        """Detect anomalies using Z-score method"""
        anomalies = []

        if len(values) < 3:
            return anomalies

        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return anomalies

        for i, reading in enumerate(readings):
            value = reading.get(metric)
            if value is None:
                continue

            z_score = abs((value - mean) / std)

            if z_score > threshold:
                severity = min(z_score / 5.0, 1.0)  # Normalize to 0-1
                anomalies.append({
                    'reading_id': reading.get('id'),
                    'sensor_id': reading['sensor_id'],
                    'anomaly_type': metric,
                    'severity': severity,
                    'value': value,
                    'mean': mean,
                    'std': std,
                    'z_score': z_score
                })

        return anomalies

    def analyze_trends(self, readings: List[Dict], time_window: int = 24) -> List[Dict]:
        """
        Analyze trends using linear regression
        time_window: hours of data to analyze
        """
        if len(readings) < 5:
            logger.warning("Not enough data for trend analysis")
            return []

        trends = []

        # Group by sensor_id
        sensors = {}
        for reading in readings:
            sid = reading['sensor_id']
            if sid not in sensors:
                sensors[sid] = []
            sensors[sid].append(reading)

        for sensor_id, sensor_readings in sensors.items():
            if len(sensor_readings) < 5:
                continue

            # Sort by timestamp
            sensor_readings.sort(key=lambda x: x['timestamp'])

            # Analyze temperature trend
            if any(r['temperature'] is not None for r in sensor_readings):
                temp_trend = self._calculate_trend(
                    sensor_readings, 'temperature', sensor_id, time_window
                )
                if temp_trend:
                    trends.append(temp_trend)

            # Analyze humidity trend
            if any(r['humidity'] is not None for r in sensor_readings):
                hum_trend = self._calculate_trend(
                    sensor_readings, 'humidity', sensor_id, time_window
                )
                if hum_trend:
                    trends.append(hum_trend)

            # Analyze air quality trend
            if any(r['air_quality'] is not None for r in sensor_readings):
                aqi_trend = self._calculate_trend(
                    sensor_readings, 'air_quality', sensor_id, time_window
                )
                if aqi_trend:
                    trends.append(aqi_trend)

        logger.info(f"Calculated {len(trends)} trends")
        return trends

    def _calculate_trend(self, readings: List[Dict], metric: str,
                        sensor_id: str, time_window: int) -> Dict:
        """Calculate trend for a specific metric using linear regression"""
        # Filter valid readings
        valid_readings = [r for r in readings if r.get(metric) is not None]

        if len(valid_readings) < 3:
            return None

        # Convert timestamps to numeric values (hours from first reading)
        first_time = datetime.fromisoformat(valid_readings[0]['timestamp'])
        x_values = []
        y_values = []

        for reading in valid_readings:
            timestamp = datetime.fromisoformat(reading['timestamp'])
            hours_diff = (timestamp - first_time).total_seconds() / 3600
            x_values.append(hours_diff)
            y_values.append(reading[metric])

        # Simple linear regression
        x = np.array(x_values)
        y = np.array(y_values)

        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / \
                (n * np.sum(x ** 2) - np.sum(x) ** 2)

        # Determine trend direction
        if abs(slope) < 0.01:  # Nearly flat
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {
            'sensor_id': sensor_id,
            'metric': metric,
            'trend_direction': direction,
            'slope': float(slope),
            'time_window': time_window
        }

    def predict_next_value(self, readings: List[Dict], metric: str) -> float:
        """Simple prediction based on linear trend"""
        if len(readings) < 3:
            return None

        valid_readings = [r for r in readings if r.get(metric) is not None]
        if len(valid_readings) < 3:
            return None

        # Get last few readings for prediction
        recent = valid_readings[-10:]

        values = [r[metric] for r in recent]
        x = np.arange(len(values))
        y = np.array(values)

        # Linear regression
        slope = np.polyfit(x, y, 1)[0]

        # Predict next value
        next_value = values[-1] + slope

        return float(next_value)
