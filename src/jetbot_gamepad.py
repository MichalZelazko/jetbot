
from Gamepad import Gamepad
import ipywidgets.widgets as widgets
from steering_actions import SteeringActions
import time


class JetbotGamepad(SteeringActions):
    #_jetbotRobot: JetbotRobot
    _controller: widgets.Controller

    gamepadType = Gamepad.PS4
    gamepad: any
    buttonHappy = 'CROSS'
    buttonBeep = 'CIRCLE'
    buttonExit = 'PS'
    joystickSpeed = 'LEFT-X'
    joystickSteering = 'RIGHT-X'
    pollInterval = 0.1

    switch = False

    """
    Initializes the inherited 'SteeringActions' class.
    Uses custom Gamepad library for connecting the gamepad.
    """
    def __init__(self):
        super().__init__()
        #self._jetbotRobot = jetbotRobot
        # self._controller = controller
        # print(self._controller)

        if not Gamepad.available():
            print('Please connect your gamepad...')
            while not Gamepad.available():
                time.sleep(1.0)
        self.gamepad = self.gamepadType()
        print('Gamepad connected')

        self.gamepad.startBackgroundUpdates()

    """
    Updates read values of joystick to 'speed' and 'turn' variables using polling.
    """
    def update(self):
        try:
            while self.gamepad.isConnected():

                super().set_turn(self.gamepad.axis(self.joystickSpeed) * 0.2)
                super().set_speed(-self.gamepad.axis(self.joystickSteering) * 0.35)

                time.sleep(self.pollInterval)
        finally:
            # Ensure the background thread is always terminated when we are done
            # self.gamepad.disconnect()
            return