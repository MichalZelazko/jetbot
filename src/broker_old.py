#!/usr/bin/python3
import paho.mqtt.client as paho
from getpass import getpass
import serial
import time
from serial.tools import list_ports
from ai import AI
from settings import Settings

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
    AskNextStep()


def on_publish(client, userdata, mid):
    print("Message has been send")


def on_message(client, userdata, msg):
    global response
    message = str(msg.payload)
    sub_message = message[2:len(message) - 1]
    print("Message that has been received: " + sub_message)
    if response == "":
        arduino.flushInput()
        arduino.flushOutput()
        arduino.write(bytes(sub_message + "\r\n\0", 'utf-8'))
        time.sleep(0.2)
        data = arduino.readline()
        if data:
            print('data: ' + str(data.decode('utf-8')))
            response = str(data.decode('utf-8'))
    else: response = ""


def on_reconnect(client, userdata, flags, rc):
    AskNextStep()

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
    client.subscribe("aiproject/#")

def get_ai_speed():
    print(settings.ai_speed)

def get_threshold_blocked():
    print(settings.threshold_blocked)

def get_threshold_turn():
    print(settings.threshold_turn)

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
    val = input("What do you want to do? ")
    my_callback()


def my_callback():
    global val, maxdistance, sensorid, response
    if (val != ""):
        
        # distance
        if val == "getmaxdistance":
            (rc, mid) = client.publish("aiproject/distance", val, qos=1)
            print(response)
            (rc, mid) = client.publish("aiproject/arduino", response , qos=1)
            print("maximum distance: " + maxdistance + "cm")
            AskNextStep()
        elif "setmaxdistance" in val:
            if maxdistance != val[15: len(val)]:
                maxdistance = val[15: len(val)]
                on_change_max_distance(int(maxdistance))
                (rc, mid) = client.publish("aiproject/distance", val, qos=1)
                print("Changing maximum distance to " + maxdistance + "cm")
                AskNextStep()
            else:
                print("Maximum distance already is " + maxdistance + "cm")
                AskNextStep()
        elif "getdistance" in val:
            (rc, mid) = client.publish("aiproject/distance", val, qos=1)
            if sensorid != val[12: len(val)]:
                sensorid = val[12: len(val)]
                print("sensor id: " + sensorid)
            AskNextStep()
        
        #change ai
        elif "change speed" in val:
            speedValue = val[13: len(val)]
            on_change_ai_speed(speedValue)
            AskNextStep()

        elif "change threshold blocked" in val:
            treshHoldBlockedValue = val[25: len(val)]
            print(treshHoldBlockedValue)
            on_change_threshold_blocked(float(treshHoldBlockedValue))
            AskNextStep()

        elif "change threshold turn" in val:
            treshHoldTurnValue = val[22: len(val)]
            print(treshHoldTurnValue)
            on_change_threshold_turn(float(treshHoldTurnValue))
            AskNextStep()

        #get ai settings
        elif val == "get threshold turn":
            get_threshold_turn()
            AskNextStep()
        
        elif val == "get ai speed":
            get_ai_speed()
            AskNextStep()

        elif val == "get threshold blocked":
            get_threshold_blocked()
            AskNextStep()


        # time
        elif "gettime" in val:
            (rc, mid) = client.publish("aiproject/time", val, qos=1)
            AskNextStep()
        elif "settime" in val:
            (rc, mid) = client.publish("aiproject/time", val, qos=1)
            AskNextStep()

        # disconnect
        elif val == "exit":
            client.unsubscribe("aiproject/#")
            print("disconnecting...")
            client.disconnect()  # disconnect gracefully
            client.loop_stop()  # stops network loop

        # not valid command
        else:
            print("This is not a valid command")
            AskNextStep()
