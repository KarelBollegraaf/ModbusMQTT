from datetime import datetime
from enum import StrEnum
from pyModbusTCP.client import ModbusClient
from struct import pack, unpack
from typing import Any, Dict, List, Tuple


class DType(StrEnum):
    ARRAY = "array 0..9 of unsigned int16"
    BOOL = "boolean"
    DATE = "datetime"
    F32 = "float32"
    F64 = "float64"
    I16 = "int16"
    STRING = "string"
    U16 = "unsigned int16"
    U32 = "unsigned int32"

def bitmap_signed_to_unsigned(input: int, bytes: int) -> int:
    int(input)
    inputbytes = input.to_bytes(bytes, 'little', signed=True)
    return int.from_bytes(inputbytes, 'little', signed=False)

def read_bool(client: ModbusClient, register: int) -> bool:
    data = client.read_holding_registers(register, 1)
    if not data:
        raise RuntimeError(f"Failed reading register {register}")
    return data[0] != 0

def read_date(client: ModbusClient, register: int) -> datetime:
    order = ("year", "month", "day", "hour", "minute", "second")
    data = client.read_holding_registers(register, 4)
    unpacked = unpack("Hbbxbbb", pack("HHHH", *data))
    mapped = {key: value for key, value in zip(order, unpacked)}
    return mapped

def read_f32(client: ModbusClient, register: int) -> float:
    return unpack("f", pack("HH", *client.read_holding_registers(register, 2)))[0]

def read_i16(client: ModbusClient, register: int, signed = True) -> int:
    data = client.read_holding_registers(register, 1)
    if not data:
        raise RuntimeError(f"Failed reading i16 register {register}")
    value = data[0]
    return value if signed else bitmap_signed_to_unsigned(value, 2)

def read_i32(client: ModbusClient, register: int, signed = True) -> int:
    data = client.read_holding_registers(register, 2)
    return data if signed else bitmap_signed_to_unsigned(unpack("I", pack("HH", *data))[0], 4)

def read_i32_array(client: ModbusClient, register: int, num: int, signed = True, ) -> List[int]:
    data = client.read_holding_registers(register, num * 2)
    unpacked = unpack("i" * num, pack("H" * len(data), *data))
    if not signed:
        unpacked = [bitmap_signed_to_unsigned(value, 4) for value in unpacked]
    return unpacked

def read_string(client: ModbusClient, register: int, length: int) -> str:
    num_registers = (length + 1) // 2
    data = client.read_holding_registers(register, num_registers)
    data = pack("H" * num_registers, *data)
    string = unpack(f"{length}s", data)[0].decode("ascii").split('\x00')[0]
    return string

def read_bit_array(client: ModbusClient, register: int, signed = True) -> List[int]:
    data = client.read_holding_registers(register, 1)
    unpacked = unpack("H", pack("H", *data))[0]
    bits = [(unpacked >> bit) & 1 for bit in range(16)]
    return bits


def read_variable(client: ModbusClient, register: int, length: int, dtype: DType) -> Any:
    match dtype:
        case DType.ARRAY: return read_i32_array(client, register, length, False)
        case DType.BOOL: return read_bool(client, register)
        case DType.DATE: return read_date(client, register)
        case DType.F32: return read_f32(client, register)
        case DType.I16: return read_i16(client, register)
        case DType.STRING: return read_string(client, register, length)
        case DType.U16: return read_i16(client, register, False)
        case DType.U32: return read_i32(client, register, False)
        case _: raise Exception("Unknown DType")

'''
    Retrieves the fields from various holding registers, the fields contains a dict with the following structure
    the key is the holding register address, then the value consists of the target sql column_name, size for strings 
    and arrays (otherwise ignored), and the stored type. The return value is a dict containing the values per db column
'''
def retrieve_data_fields(client: ModbusClient, fields: Dict[int, Tuple[str, int, DType]]) -> Dict[str, Any]:
    results = {}

    for register, (column, length, dtype) in fields.items():
        results[column] = read_variable(client, register, length, dtype)
    
    return results

'''
    Retrieves Cycle times
'''
def retrieve_cycles(client: ModbusClient, fields: Dict[int, List]) -> List[int]:
    results = []

    for key, metadata in fields.items():
        timings = read_i32_array(client, key, 10, False)
        results.append([*metadata, timings])

    return results

'''
    Retrieve pressure values, the values are mapped in two related lists:
    `high pressure` and `channel pressure`. The metadata contains the offset between the lists (idx 2)
'''
def retrieve_pressure(client: ModbusClient, fields: Dict[int, List]) -> List:
    results = []

    for key, metadata in fields.items():
        high_pressure = read_i32_array(client, key, 10, False)
        channel_pressure = read_i32_array(client, key + metadata["offset"], 10, False)
        results.append({
            **metadata,
            "high_pressure": high_pressure,
            "channel_pressure": channel_pressure
        })

    return results

def retrieve_event_identifier(client: ModbusClient, register: int) -> int:
    return read_bit_array(client, register, False)

def retrieve_bale_ready(client: ModbusClient, register: int) -> int:
    return read_bool(client, register)

def retrieve_bale_click(client: ModbusClient, register: int) -> int:
    return read_i32_array(client, register, 10,False)