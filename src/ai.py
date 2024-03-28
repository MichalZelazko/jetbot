import re
from steering_actions import SteeringActions
import torch
import torchvision
import cv2
import numpy as np
from jetbot import Camera, bgr8_to_jpeg
from settings import Settings
import torch.nn.functional as F
import time
# tensor rt cores imports 
from torch2trt import TRTModule
import PIL.Image
import torchvision.transforms as transforms
import random


"""
Ai class, all AI configurations are here.
To change to diffrent Neural networks model change init function (comment and uncomment) and in update change preprocess if needed  
"""
class AI(SteeringActions):
    ai_speed = 0
    threshold_blocked = 0
    threshold_turn = 0
    reverseSpeed = 0

    """
    In this automatically called init funtion threshold, turn and speed values are set, according to init file.
    Initial value for probability for turn is set here as a safty measure, so sensors wont stop robot until first frame is process by a model
    """    
    def __init__(self, settings: Settings):
        self.settings = settings

        self.ai_speed = settings.ai_speed
        self.threshold_blocked = settings.threshold_blocked
        self.threshold_turn = settings.threshold_turn

        self.changeSpeed(settings.ai_speed)
        
        self.prob_left = 0
        self.prob_mid = 1
        self.prob_right = 0

        super().__init__()


    """
    This function sets parameters for diffrent speed of a robot (reverse, turn, etc.), acording to some hardcodded values
    """
    def changeSpeed(self, ai_speed):
        self.ai_speed = ai_speed
        self.targetSpeed = self.ai_speed
        self.turnSpeed = self.ai_speed * 0.2
        self.reverseSpeed = self.ai_speed * 0.6


    """
    Function for freeing camera, called when closing program 
    (if camera is not free, then robot must be resterted to access camera again)
    """
    def __del__(self):
        self.camera.stop()


    """
    Init function called in nn threat, it is use to init all variables need for model to work.
    When changing the model comment and uncomment given lines
    """
    def init(self):
            # Alexnet no trt 
            # AlexNet_final_NllLoss (9/10) - erros only with big speeds - good in bad and good light
            # AlexNet_final_CrossEntropy - 
        # self.model = torchvision.models.alexnet(pretrained=True)
        # self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, 5)
        # self.model.load_state_dict(torch.load('AlexNet_final_CrossEntropy.pth'))
        # self.device = torch.device('cuda')
        # self.model = self.model.to(self.device)
        # self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        # self.std = 255.0 * np.array([0.229, 0.224, 0.225])
            # End Alexnet no trt
            # Alexnet trt - works very poorly. For AlexNet_final_NllLoss_TRT a little better (6/10) then for AlexNet_final_CrossEntropy_TRT (5/10)
        # self.device = torch.device('cuda')
        # self.model = TRTModule()
        # self.model.load_state_dict(torch.load('AlexNet_final_NllLoss_TRT.pth'))
        # self.mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
        # self.std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()
            # End Alexnet trt
            # ResNet18 no trt (Resnet18_final_CrossEntropy 6.5/10, Resnet18_final_nllLoss 5/10)
        self.set_speed(0)
        self.set_turn(0)
        self.model = torchvision.models.resnet18(pretrained=True)
        self.model.fc = torch.nn.Linear(512, 5)
        self.model.load_state_dict(torch.load('best_model_resnet18.pth'))
        self.device = torch.device('cuda')
        self.model = self.model.to(self.device)
        self.model = self.model.eval().half()
        self.mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
        self.std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()
            # End ResNet18 no trt
            # ResNet18 trt (Resnet18_final_CrossEntropy_TRT 6.5/10, Resnet18_final_nllLoss_TRT best trt model 7.2/10, usefull for good lightining conditions
        # self.device = torch.device('cuda')
        # self.model = TRTModule()
        # self.model.load_state_dict(torch.load('Resnet18_final_nllLoss_TRT.pth'))
        # self.mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
        # self.std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()
            # End ResNet18 trt
            # common part
        self.normalize = torchvision.transforms.Normalize(self.mean, self.std)
        self.camera = Camera.instance(width=224, height=224)


    """
    Preprocess function for Alexnet network without tensor cores,
    it takes camera frame and returns preprocessed frame (normalized, with filter color and as a np array)
    """
    def preprocess_Anet_noTrt(self, camera_value):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        return x


    """
    Preprocess function for all networks, exept Alexnet without tensor rt cores 
    For Resnet18 with and without Trt, and alexnet with trt
    It takes camera frame and returns preprocessed frame.
    """
    def preprocess_ResNet18_alexNet(self, camera_value):
        image = PIL.Image.fromarray(camera_value)
        image = transforms.functional.to_tensor(camera_value).to(self.device).half()
        image.sub_(self.mean[:, None, None]).div_(self.std[:, None, None])
        return image[None, ...]


    
    speedBlocked = 0
    turnBlocked = reverseSpeed
    """
    Function read camera frame, send it to preprocess and send it to model.
    Then apply softmax and flatten functions (normalization for model response)
    It the end it set speed of a robot according to model response and basing on values of threshold and speed
    """
    def update(self):
        # print("model start")
        # start = time.perf_counter()
        x = self.camera.value
        x = self.preprocess_Anet_noTrt(x)
        y = self.model(x)
        y = F.softmax(y, dim=1)
        # print("model finish")
        prob_blocked = float(y.flatten()[0])
        prob_free = float(y.flatten()[1])
        self.prob_left = float(y.flatten()[2])
        self.prob_mid = float(y.flatten()[3])
        self.prob_right = float(y.flatten()[4])
         
        if prob_blocked < self.threshold_blocked:
            self.set_speed(self.targetSpeed)
            if self.prob_right > self.threshold_turn:
                self.set_turn(self.turnSpeed)
            elif self.prob_left > self.threshold_turn:
                self.set_turn(-self.turnSpeed)
            else:
                self.set_turn(0)

            self.speedBlocked = -0.2 if random.randint(1,100) < 50 else 0
            self.turnBlocked = self.reverseSpeed if random.randint(1,100) < 50 else -self.reverseSpeed
        else:
            self.set_speed(self.speedBlocked)
            self.set_turn(self.turnBlocked)
        # print((time.perf_counter() - start) * 1000)


    """
    Funtion returning True if model detects that path is blocked, free when it is free.
    Used for distance sensors
    """
    def is_blocked(self):
        if self.prob_left > self.threshold_turn or \
            self.prob_mid > self.threshold_turn or \
            self.prob_right > self.threshold_turn:
            return True
        else:
            return False