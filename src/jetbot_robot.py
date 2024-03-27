from jetbot import Robot
import time

class JetbotRobot(Robot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def forward(self, speed=1.0):
        super().left_motor.alpha = 1
        #super().right_motor.alpha = self.find_alpha(speed)
        super().forward(speed)
        
        
    def forward_gradual(self, target_speed=1.0, timespan=1.0):
        steps = 10
        delta_time = timespan / steps
        delta_speed = target_speed / steps
            
        super().stop()
        speed = 0
        for step in range(0, steps):
            speed += delta_speed
            self.forward(speed)
            time.sleep(delta_time)
            
        self.forward(speed)
    
    
    def backward(self, speed=1.0):
        super().left_motor.alpha = 1
        super().right_motor.alpha = self.find_alpha(speed)
        super().backward(speed)
        
        
    def set_motors(self, left_speed, right_speed):
        super().left_motor.alpha = 1
        super().right_motor.alpha = self.find_alpha(right_speed)
        super.set_motors(left_speed, right_speed)
        
        
    def stop_gradual(self, timespan=1.0):
        steps = 10
        delta_time = timespan / steps
        delta_right_motor_speed = super().right_motor.value / steps
        delta_left_motor_speed = super().left_motor.value / steps
            
        for step in range(0, steps):
            super().right_motor.value -= delta_right_motor_speed
            super().left_motor.value -= delta_left_motor_speed
            time.sleep(delta_time)
            
        super().stop()
        
    
    def calc_linear(self, x, ax, ay, bx, by):
        return (ay - by) / (ax - bx) * x + (ay - (ay - by) / (ax - bx) * ax)

    
    def find_alpha(self, speed):
        if 0 < speed and speed <= 1:
            return 0.9415
        elif 1 < speed and speed <= 2:
            return calc_linear(speed, 1, find_alpha(1), 2, 0.98)
        elif 2 < speed and speed <= 3:
            return calc_linear(speed, 2, find_alpha(2), 3, 0.98)
        elif 3 < speed and speed <= 4:
            return calc_linear(speed, 3, find_alpha(3), 4, 0.9805)
        elif 4 < speed and speed <= 5:
            return calc_linear(speed, 4, find_alpha(4), 5, 0.96)
        elif 5 < speed and speed <= 6:
            return calc_linear(speed, 5, find_alpha(5), 6, 0.95)
        elif 6 < speed and speed <= 7:
            return calc_linear(speed, 6, find_alpha(6), 7, 0.95)
        elif 7 < speed and speed <= 8:
            return calc_linear(speed, 7, find_alpha(7), 8, 0.89)
        else:
            return 0


        