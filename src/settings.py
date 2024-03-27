import pickle as cPickle

class Settings():
    filename = "jetbot_settings.txt"

    ai_speed: float
    max_distance: int
    threshold_blocked: float
    threshold_turn: float


    def setInitValues(self):
        self.ai_speed = 0.3
        self.max_distance = 12
        self.threshold_blocked = 0.5
        self.threshold_turn = 0.5


    def __init__(self):
        self.setInitValues()
        return


    def load(self):
        try:
            file = open(self.filename, 'rb')
            tmp_dict = cPickle.load(file)
            file.close()          
            self.__dict__.update(tmp_dict) 
        except:
            print("Warning: couldn't load settings.")

    def save(self):
        try:
            file = open(self.filename, 'wb')
            cPickle.dump(self.__dict__, file, 2)
            file.close()
        except:
            print("Warning: couldn't save settings")