def calc_linear(x, ax, ay, bx, by):
    return (ay - by) / (ax - bx) * x + (ay - (ay - by) / (ax - bx) * ax)

def find_alpha(speed):
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
    
print(find_alpha(7.5))