from jetbot_robot import JetbotRobot
from jetbot_gamepad import JetbotGamepad
from steering import Steering
import ipywidgets.widgets as widgets
import serial
import time
import sys

#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)

def arduino():
    # ser.flushInput()
    # ser.flushOutput()

    #ser.write(bytes("gettime all\r\n", 'utf-8'))
    time.sleep(0.05)
    
    return
    

def main():
    robot = JetbotRobot()
    steering = Steering(robot)
    gamepad = JetbotGamepad(robot, steering)

    while True:
        #arduino()
        gamepad.update()
        # time.sleep(1)

if __name__ == "__main__":
    main()
