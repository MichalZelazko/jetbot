#!/usr/bin/python3
import paho.mqtt.client as paho
from getpass import getpass
import serial
import time
from serial.tools import list_ports
from ai import AI
from settings import Settings
import traceback

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


# qos 0 --> message send only once, not stored, not acknowledged it is not send again
# qos 1 --> message send at least once, in case not acknowledged it is send again (even if it was received, can be received twice)
# qos 2 --> message send exactly once, always delivered once --> safest but slowest way

host = "jetbot"
val = ""
sensorid = '0'
maxdistance = '30'
response = ""

arduino = serial.Serial(
    port=find_serial_device(),
    baudrate=9600,
    timeout = 0.1,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code =", rc)
    else:
        print("Bad connection Returned code =", rc)
        client.disconnect()  # disconnect gracefully
        client.loop_stop()  # stops network loop


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))
    return


def on_publish(client, userdata, mid):
    return


def on_reconnect(client, userdata, flags, rc):
    return

client = None
ai: AI
settings: Settings
def config_broker(conf_ai: AI, conf_settings: Settings): 
    global ai, settings, client
    ai = conf_ai
    settings = conf_settings
    client = paho.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_reconnect = on_reconnect
    user = "testbot" #input("Username: ")
    psswd = "jetbot123" #getpass("Password: ")
    client.username_pw_set(user, psswd)  # needs to be before client.connect
    client.connect(host, keepalive=3600)
    client.subscribe("aiproject/command")

def get_ai_speed():
    return str(settings.ai_speed)

def get_threshold_blocked():
    return str(settings.threshold_blocked)

def get_threshold_turn():
    return str(settings.threshold_turn)

def on_change_ai_speed(ai_speed: float):
    ai.changeSpeed(ai_speed)
    settings.ai_speed = ai_speed
    settings.save()

def on_change_threshold_blocked(threshold_blocked: float):
    ai.threshold_blocked = threshold_blocked
    settings.threshold_blocked = threshold_blocked
    settings.save()

def on_change_threshold_turn(threshold_turn: float):
    ai.threshold_turn = threshold_turn
    settings.threshold_turn = threshold_turn
    settings.save()

def on_change_max_distance(max_distance: int):
    settings.max_distance = max_distance
    settings.save()

def start_broker():
    client.loop_forever()


def AskNextStep():
    global val

def on_message(client, userdata, msg):
    try:
        handle_request(client, userdata, msg)
    except:
        traceback.print_exc()
        return

def handle_request(client, userdata, msg):
    if "aiproject/command" not in msg.topic:
        return

    message = str(msg.payload)
    sub_message = message[2:len(message) - 1]

    response = f"{sub_message}: "
    #arduino
    if "getmaxdistance" in sub_message:
        response += askArduino(sub_message).replace('\r\n', '')
        response += " cm"

    elif "setmaxdistance" in sub_message:
        maxdistance = sub_message[15: len(sub_message)]
        on_change_max_distance(int(maxdistance))
        response += askArduino(sub_message).replace('\r\n', '')

    elif "getdistance" in sub_message:
        response += askArduino(sub_message).replace('\r\n', '')
        response += " cm"

    elif "gettime" in sub_message:
        response += askArduino(sub_message).replace('\r\n', '')

    elif "settime" in sub_message:
        response += askArduino(sub_message).replace('\r\n', '')

    #set ai
    elif "change speed" in sub_message:
        speedValue = float(sub_message[13: len(sub_message)])
        on_change_ai_speed(speedValue)
        response += "OK"

    elif "change threshold blocked" in sub_message:
        treshHoldBlockedValue = float(sub_message[25: len(sub_message)])
        on_change_threshold_blocked(float(treshHoldBlockedValue))
        response += "OK"

    elif "change threshold turn" in sub_message:
        treshHoldTurnValue = float(sub_message[22: len(sub_message)])
        on_change_threshold_turn(float(treshHoldTurnValue))
        response += "OK"

    #get ai settings
    elif sub_message == "get threshold turn":
        response += get_threshold_turn()
    
    elif sub_message == "get speed":
        response += get_ai_speed()

    elif sub_message == "get threshold blocked":
        response += get_threshold_blocked()

    client.publish("aiproject/response", response , qos=1)

def askArduino(message):
    tellArduino(message)
    time.sleep(0.2)
    data = arduino.readline()
    response = str(data.decode('utf-8'))
    return response

def tellArduino(message):
    arduino.flushInput()
    arduino.flushOutput()
    arduino.write(bytes(message + "\r\n\0", 'utf-8'))
    return 