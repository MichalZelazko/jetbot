import aifc
from jetbot_gamepad import JetbotGamepad
from jetbot_robot import JetbotRobot
from steering_actions import SteeringActions
from jetbot_gamepad import JetbotGamepad
from ai import AI
import RPi.GPIO as GPIO
import time

class Steering():
    gamepad: JetbotGamepad
    ai: AI
    empty = SteeringActions()
    currentSteeringSource: SteeringActions
    jetbotRobot: JetbotRobot

    front_warning_pin = 11
    back_warning_pin = 12

    wasCrossPressed = False
    wasUpPressed = False
    wasDownPressed = False

    lastFrontDetected = 0
    lastBackDetected = 0

    def __init__(self, jetbotRobot: JetbotRobot, gamepad: JetbotGamepad, ai: AI):
        self.jetbotRobot = jetbotRobot
        self.gamepad = gamepad
        self.ai = ai
        self.currentSteeringSource = self.empty

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.front_warning_pin, GPIO.IN)
        GPIO.setup(self.back_warning_pin, GPIO.IN)
        GPIO.add_event_detect(self.front_warning_pin, GPIO.RISING, callback=self.warningFront, bouncetime=10)
        GPIO.add_event_detect(self.back_warning_pin, GPIO.RISING, callback=self.warningBack, bouncetime=10)
        self.jetbotRobot.stop()
        return


    def __del__(self):
        GPIO.cleanup()


    """
    Interrupt function for detected front obstacle.
    It stops the robot and switches steering to manual.
    """
    def warningFront(self, channel):
        now = time.perf_counter()
        if self.ai.is_blocked() or self.ai.get_speed() <= 0:
            self.lastFrontDetected = now
            return
        
        delta = (now - self.lastFrontDetected) * 1000

        if delta < 50:
            pass
        elif delta < 1000:
            self.jetbotRobot.stop()
            self.currentSteeringSource = self.gamepad
            self.lastFrontDetected = now
        else:
            self.lastFrontDetected = now
        return

    """
    Interrupt function for detected back obstacle.
    It stops the robot and switches steering to manual.
    """
    def warningBack(self, channel):
        now = time.perf_counter()
        if self.ai.is_blocked() or self.ai.get_speed() <= 0:
            self.lastBackDetected = now
            return
        
        delta = (now - self.lastBackDetected) * 1000

        if delta < 50:
            pass
        elif delta < 1000:
            self.jetbotRobot.stop()
            self.currentSteeringSource = self.gamepad
            self.lastBackDetected = now
        else:
            self.lastBackDetected = now
        return

    """
    Returns True if current steering source is AI.
    """
    def isAI(self):
        return (self.currentSteeringSource == self.ai)

    """
    1) Handles buttons on gamepad:
        A -> switch the steering source (AI<->manual)
        X -> increase the AI speed
        Y -> decrease the AI speed
        *** Note that names of buttons on gamepad are different than ones in the library! ***
    2) Applies steering from the current source.
    """
    def update(self):
        if self.gamepad.gamepad.isPressed("CROSS") and self.wasCrossPressed == False:
            self.wasCrossPressed = True
            if self.currentSteeringSource == self.gamepad:
                self.currentSteeringSource = self.ai
            else:
                self.currentSteeringSource = self.gamepad
        elif not self.gamepad.gamepad.isPressed("CROSS") and self.wasCrossPressed == True:
            self.wasCrossPressed = False

        if self.gamepad.gamepad.isPressed("SQUARE") and self.wasUpPressed == False:
            print("faster")
            self.wasUpPressed = True
            self.ai.changeSpeed(min(self.ai.ai_speed + 0.02, 1))
        elif not self.gamepad.gamepad.isPressed("SQUARE") and self.wasUpPressed == True:
            self.wasUpPressed = False

        if self.gamepad.gamepad.isPressed("L1") and self.wasDownPressed == False:
            print("slower")
            self.wasDownPressed = True
            self.ai.changeSpeed(max(self.ai.ai_speed - 0.02, 0))
        elif not self.gamepad.gamepad.isPressed("L1") and self.wasDownPressed == True:
            self.wasDownPressed = False

        if self.currentSteeringSource == None:
            return
        speed = self.currentSteeringSource.get_speed()
        turn = self.currentSteeringSource.get_turn()
        self.jetbotRobot.left_motor.value = min(speed + turn, 1)
        self.jetbotRobot.right_motor.value = min(speed - turn, 1)


        time.sleep(0.005)
        return

        