from MBReading import *
from MQTTOut import *
from pyModbusTCP.client import ModbusClient
from time import sleep
from enum import IntEnum

import settings

settings.init()

class Part(IntEnum):
    Ram = 1,
    Flap = 2,
    NeedlesVertical = 3,
    NeedlesHorizontal = 4,
    KnotterVertical = 5,
    KnotterHorizontal = 6,
    Knife = 7

class Direction(IntEnum):
    Forward = 1,
    Reverse = 2,

def update(client: ModbusClient, MQTT_client):
    field_mapping = {
#       addr     col name               len     data type
        28_000: ["bale_number",         None,   DType.U32],
        28_002: ["recipe_number",       None,   DType.I16],
        28_003: ["material_name",       20,     DType.STRING],
        28_013: ["user_id",             None,   DType.I16],
        28_014: ["username",            16,     DType.STRING],
        28_022: ["customer_number",     None,   DType.I16],
        28_023: ["shift_number",        None,   DType.I16],
        28_026: ["timestamp",           None,   DType.DATE],

        28_032: ["kwh_used",            None,   DType.F32],
        28_034: ["bale_length",         None,   DType.U16],
        28_035: ["wires_vertical",      None,   DType.U16],
        28_036: ["wires_horizontal",    None,   DType.U16],
        28_037: ["knots_vertical",      None,   DType.U16],
        28_038: ["knots_horizontal",    None,   DType.U16],
        28_039: ["weight",              None,   DType.U16],
        28_040: ["volume",              None,   DType.U16],
        28_041: ["oil_temperature",     None,   DType.I16],
        28_042: ["oil_level",           None,   DType.I16],

        28_044: ["total_time",          None,   DType.U16],
        28_045: ["auto_time",           None,   DType.U16],
        28_046: ["standby_time",        None,   DType.U16],
        28_047: ["empty_time",          None,   DType.U16],

        28_308: ["valve_lp",            None,   DType.U16],
        28_309: ["valve_hp",            None,   DType.U16],
        28_310: ["valve_ko1",           None,   DType.U16],
        28_311: ["valve_ko2",           None,   DType.U16],
        28_312: ["valve_kd1",           None,   DType.U16],
        28_313: ["valve_kd2",           None,   DType.U16],
        28_314: ["valve_rp1",           None,   DType.U16],
        28_315: ["valve_rp2",           None,   DType.U16],
        28_316: ["valve_rr1",           None,   DType.U16],
        28_317: ["valve_rr2",           None,   DType.U16],
        28_318: ["valve_ch",            None,   DType.U16],
        28_319: ["valve_mes",           None,   DType.U16]
    }

    cycle_mapping = {
        28_048: [Part.Ram,                 Direction.Forward],
        28_068: [Part.Ram,                 Direction.Reverse],
        28_088: [Part.Flap,                Direction.Forward],
        28_108: [Part.Flap,                Direction.Reverse],
        28_128: [Part.NeedlesVertical,     Direction.Forward],
        28_148: [Part.NeedlesVertical,     Direction.Reverse],
        28_168: [Part.NeedlesHorizontal,   Direction.Forward],
        28_188: [Part.NeedlesHorizontal,   Direction.Reverse],
        28_208: [Part.KnotterVertical,     Direction.Forward],
        28_228: [Part.KnotterVertical,     Direction.Reverse],
        28_248: [Part.KnotterHorizontal,   Direction.Forward],
        28_268: [Part.KnotterHorizontal,   Direction.Reverse],
        28_288: [Part.Knife,               None]
    }

    channel_pressure_mapping = {
        28_320: {"part": Part.Ram,  "direction": Direction.Forward, "offset": 80},
        28_340: {"part": Part.Ram,  "direction": Direction.Reverse, "offset": 80},
        28_360: {"part": Part.Flap, "direction": Direction.Forward, "offset": 80},
        28_380: {"part": Part.Flap, "direction": Direction.Reverse, "offset": 80},
    }



    fields = retrieve_data_fields(client, field_mapping)
    print("fields: {}", fields, "\n")

    cycles = retrieve_cycles(client, cycle_mapping)
    print("cycles: {}", cycles, "\n")

    pressure = retrieve_pressure(client, channel_pressure_mapping)
    print("pressure: {}", pressure, "\n")



    try:
        publish_Json(MQTT_client, settings.MQTT_MB_TOPIC, fields, cycles, pressure)
        print("MQTT message published successfully.")
    except Exception as e:
        print(f"Error publishing MQTT message: {e}")

def main():
    settings.init()
    client = ModbusClient(settings.MODBUS_BALER_IP, port=settings.MODBUS_BALER_PORT)
    MQTT_client = mqtt.Client(client_id = "CustomMB")
    StartMQTT(MQTT_client)  
    bale_nr_reg, bale_nr_dtype = 28_000, DType.U32
    bale_number = -1
    while True:
        new_number = read_variable(client, bale_nr_reg, None, bale_nr_dtype)
        if bale_number != new_number:
            bale_number = new_number
            update(client, MQTT_client)
        
        EventIdentivier = retrieve_event_identifier(client, 70)
        BaleReadyd = retrieve_bale_ready(client, 28024)
        BaleClickd = retrieve_bale_click(client, 28480)
        try:
            publish_Lenght_JSON(MQTT_client, settings.MQTT_MB_TOPIC, EventIdentivier, BaleReadyd, BaleClickd)
            print("Length MQTT message published successfully.")
        except Exception as e:
            print(f"Error publishing Length MQTT message: {e}")
        publish_Lenght_JSON(MQTT_client, settings.MQTT_MB_TOPIC, EventIdentivier, BaleReadyd, BaleClickd)
           
        sleep(3) # sleep 1 second before checking again

if __name__ == "__main__":
    main()