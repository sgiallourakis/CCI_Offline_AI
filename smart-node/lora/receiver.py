import serial
import asyncio
import json
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class LoRaReceiver:
    """
    LoRa receiver for environmental sensor data
    Expects JSON format: {"sensor_id": "ENV001", "temp": 22.5, "humidity": 65, "aqi": 45}
    """
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.callback: Optional[Callable] = None

    def connect(self):
        """Connect to LoRa module"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            logger.info(f"Connected to LoRa module on {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to LoRa module: {e}")
            return False

    def disconnect(self):
        """Disconnect from LoRa module"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Disconnected from LoRa module")

    def set_callback(self, callback: Callable):
        """Set callback function for received data"""
        self.callback = callback

    async def start_listening(self):
        """Start listening for LoRa messages"""
        self.running = True
        logger.info("LoRa receiver started")

        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    # Read line from serial
                    line = self.serial_conn.readline().decode('utf-8').strip()

                    if line:
                        logger.debug(f"Received: {line}")
                        data = self._parse_message(line)

                        if data and self.callback:
                            await self.callback(data)

                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)

            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                await asyncio.sleep(1)  # Wait before retry
            except Exception as e:
                logger.error(f"Error reading LoRa data: {e}")
                await asyncio.sleep(0.5)

    def _parse_message(self, message: str) -> Optional[dict]:
        """Parse incoming LoRa message"""
        try:
            # Try JSON format first
            data = json.loads(message)

            # Validate required fields
            if "sensor_id" in data:
                return {
                    "sensor_id": data.get("sensor_id"),
                    "temperature": data.get("temp", data.get("temperature")),
                    "humidity": data.get("humidity", data.get("hum")),
                    "air_quality": data.get("aqi", data.get("air_quality")),
                    "rssi": data.get("rssi")
                }
        except json.JSONDecodeError:
            # Try CSV format: sensor_id,temp,humidity,aqi,rssi
            try:
                parts = message.split(',')
                if len(parts) >= 4:
                    return {
                        "sensor_id": parts[0].strip(),
                        "temperature": float(parts[1]),
                        "humidity": float(parts[2]),
                        "air_quality": float(parts[3]),
                        "rssi": int(parts[4]) if len(parts) > 4 else None
                    }
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse CSV message: {e}")

        logger.warning(f"Could not parse message: {message}")
        return None

    def stop(self):
        """Stop listening"""
        self.running = False
        logger.info("LoRa receiver stopped")

    def send_message(self, message: str):
        """Send message via LoRa (for future bidirectional communication)"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{message}\n".encode('utf-8'))
                logger.debug(f"Sent: {message}")
            except serial.SerialException as e:
                logger.error(f"Failed to send message: {e}")
