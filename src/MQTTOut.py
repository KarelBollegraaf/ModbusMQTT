import paho.mqtt.client as mqtt
import json
import time
import datetime   
import settings 



#start mqtt client
def StartMQTT(MQTT_client):
    MQTT_client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
    MQTT_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
    MQTT_client.subscribe(settings.MQTT_MB_TOPIC)
    MQTT_client.loop_start()
    if MQTT_client.is_connected():
        MQTT_client.publish(settings.MQTT_MB_TOPIC, "Connected")
        print(f"Connected to MQTT Broker: {settings.MQTT_BROKER} on topic: {settings.MQTT_MB_TOPIC}")
    return MQTT_client

def publish_Json(MQTT_client, MQTT_MB_TOPIC, fields, cycles, pressure):
    mqtt_payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "fields": fields,
        "cycles": cycles,
        "pressure": pressure,
        
    }
    mqtt_payload_str = json.dumps(mqtt_payload)
    msg = MQTT_client.publish(MQTT_MB_TOPIC, mqtt_payload_str)
    if msg.is_published():
        print(f"Published to {MQTT_MB_TOPIC}: {mqtt_payload_str}")
    time.sleep(3)

def publish_Lenght_JSON(MQTT_client, MQTT_MB_TOPIC, EventIdentivier, BaleReadyd, BaleClickd):
    
    mqtt_payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "EventIdentifier": EventIdentivier,
        "Bale_Ready": BaleReadyd,
        "Bale_Click": BaleClickd
    }
    mqtt_payload_str = json.dumps(mqtt_payload)
    msg = MQTT_client.publish(MQTT_MB_TOPIC, mqtt_payload_str)
    if msg.is_published():
        print(f"Published to {MQTT_MB_TOPIC}: {mqtt_payload_str}")
    time.sleep(3)