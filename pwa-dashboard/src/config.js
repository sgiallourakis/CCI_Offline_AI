// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Update intervals (ms)
export const POLL_INTERVAL = 5000; // 5 seconds
export const RECONNECT_INTERVAL = 3000; // 3 seconds

// Data display limits
export const MAX_CHART_POINTS = 50;
export const DEFAULT_HOURS = 24;
