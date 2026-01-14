import json

def init():
    with open("/cfg-data/Param.JSON", "r") as f:
        global MODBUS_BALER_IP, MODBUS_BALER_PORT, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_MB_TOPIC
        dParam = json.load(f)
        MODBUS_BALER_IP = dParam["Modbus_IP"]
        MODBUS_BALER_PORT = dParam["Modbus_port"]
        MQTT_BROKER = dParam["MQTT_BROKER"]
        MQTT_PORT = dParam["MQTT_PORT"]
        MQTT_USER = dParam["MQTT_USER"]
        MQTT_PASSWORD = dParam["MQTT_PASSWORD"]
        MQTT_MB_TOPIC = dParam["MQTT_MB_TOPIC"]