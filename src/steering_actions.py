
class SteeringActions():
    speed: float # -1 = backward, +1 = forward
    turn: float # -1 = left, +1 = right

    def __init__(self):
        self.speed = 0
        self.turn = 0
        return

    def set_speed(self, speed: float):
        self.speed = speed

    def get_speed(self):
        return self.speed

    def set_turn(self, turn: float):
        self.turn = turn

    def get_turn(self):
        return self.turn