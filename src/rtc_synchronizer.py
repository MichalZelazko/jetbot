#!/usr/bin/python3
from datetime import datetime
from tokenize import Number
import serial
import time
from serial.tools import list_ports
import os

import serial.tools.list_ports as list_ports

device_signature = '1a86:7523'

def find_serial_device():
    """Return the device path based on vender & product ID.
    
    The device is something like (like COM4, /dev/ttyUSB0 or /dev/cu.usbserial-1430)
    """
    candidates = list(list_ports.grep(device_signature))
    if not candidates:
        raise ValueError(f'No device with signature {device_signature} found')
    if len(candidates) > 1:
        raise ValueError(f'More than one device with signature {device_signature} found')
    return candidates[0].device

arduino = serial.Serial(
    port=find_serial_device(),
    baudrate=9600,
    timeout = 0.1,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

def get_time():
    arduino.flushInput()
    arduino.flushOutput()

    arduino.write(bytes("\r\n\0", 'utf-8'))
    time.sleep(0.2)
    arduino.readline()
    arduino.write(bytes("\r\n\0", 'utf-8'))
    time.sleep(0.2)
    arduino.readline()

    arduino.write(bytes("gettime all\r\n", 'utf-8'))
    time.sleep(0.2)
    TimeStr = str(arduino.readline().decode('utf-8').replace('\r\n', ''))
    print(TimeStr)
    
    os.system("""/bin/date --set=\"{}\"""".format(TimeStr))
    arduino.close()
        
get_time()