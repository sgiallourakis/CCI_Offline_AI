import { API_BASE_URL } from './config';

class API {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  async get(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  async post(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Sensor readings
  async getReadings(limit = 100, sensorId = null, hours = null) {
    let endpoint = `/api/readings?limit=${limit}`;
    if (sensorId) endpoint += `&sensor_id=${sensorId}`;
    if (hours) endpoint += `&hours=${hours}`;
    return this.get(endpoint);
  }

  // Sensors list
  async getSensors() {
    return this.get('/api/sensors');
  }

  // Anomalies
  async getAnomalies(limit = 50) {
    return this.get(`/api/anomalies?limit=${limit}`);
  }

  async runAnomalyDetection(sensorId = null, hours = 24) {
    let endpoint = `/api/analyze/anomalies?hours=${hours}`;
    if (sensorId) endpoint += `&sensor_id=${sensorId}`;
    return this.post(endpoint);
  }

  // Trends
  async getTrends(sensorId = null) {
    let endpoint = '/api/trends';
    if (sensorId) endpoint += `?sensor_id=${sensorId}`;
    return this.get(endpoint);
  }

  async runTrendAnalysis(sensorId = null, hours = 24) {
    let endpoint = `/api/analyze/trends?hours=${hours}`;
    if (sensorId) endpoint += `&sensor_id=${sensorId}`;
    return this.post(endpoint);
  }

  // System state
  async getSystemState() {
    return this.get('/api/system/state');
  }

  async wakeSystem() {
    return this.post('/api/system/wake');
  }
}

export const api = new API(API_BASE_URL);
