import sys
import threading
import time
import atexit
from queue import Queue

from scipy import False_
from broker import config_broker
from broker import start_broker
from jetbot_gamepad import JetbotGamepad
from jetbot_robot import JetbotRobot
from steering import Steering
from ai import AI
from settings import Settings

run = True

settings = Settings()
robot = JetbotRobot()
gamepad = JetbotGamepad()
ai = AI(settings)
steering = Steering(robot, gamepad, ai)

def neural_network():
    print("Loading NN")
    ai.init()
    print("nn init")
    while (run):
        if steering.isAI():
            ai.update()
            # time.sleep(0.001) # TODO set it
    return


def controller():
    while (run):
        steering.update()


def communication():
    config_broker(ai, settings)
    start_broker()


def manual_steering():
    while (run):
        gamepad.update()


def manage_threads():
    q = Queue()
    q2 = Queue()
    key = 0
    global run

    t_nn = threading.Thread(target=neural_network)
    # t_communication = threading.Thread(target=communication)
    t_controller = threading.Thread(target=controller)
    t_manual_steering = threading.Thread(target=manual_steering)

    t_nn.daemon = True
    t_controller.daemon = True
    t_manual_steering.daemon = True
    # t_communication.daemon = True

    t_controller.start()
    t_nn.start()  # default steering
    t_manual_steering.start()
    # t_communication.start()

    while True:
        if not q.empty():
            key = q.get()
        if key == 0:  # nn
            pass
        elif key == 1:  # manual steering
            manual_steering(q2)  # do it with second q or directly in function
        elif key == 2:  # stop robot
            run = False
            time.sleep(1)
            break  # TODO turn off the robot

        time.sleep(0.01)  # TODO make waiting as in robot in jupyter


def exit_handler():
    run = False
    global steering, ai, gamepad, robot
    settings.save()
    del steering
    del ai
    del gamepad
    del robot


atexit.register(exit_handler)


if __name__ == "__main__":
    settings.load()
    manage_threads()
