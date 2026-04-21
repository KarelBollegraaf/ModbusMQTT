import os

def init():
    global MODBUS_BALER_IP, MODBUS_BALER_PORT, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_MB_TOPIC

    MODBUS_BALER_IP = os.getenv("MODBUS_BALER_IP", "192.168.1.15")
    MODBUS_BALER_PORT = int(os.getenv("MODBUS_BALER_PORT", "502"))
    MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-dashboard.com")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USER = os.getenv("MQTT_USER", "")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
    MQTT_MB_TOPIC = os.getenv("MQTT_MB_TOPIC", "ModbusTest/1")

    print("Loaded config from environment/defaults")