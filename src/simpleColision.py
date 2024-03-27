import torch
import torchvision
import cv2
import numpy as np
from jetbot import Robot
import traitlets
from IPython.display import display
import ipywidgets.widgets as widgets
from jetbot import Camera, bgr8_to_jpeg
import torch.nn.functional as F
import time

print("libraries loaded")

model = torchvision.models.alexnet(pretrained=False)
model.classifier[6] = torch.nn.Linear(model.classifier[6].in_features, 2)
model.load_state_dict(torch.load('best_model.pth'))

print("model loaded")

device = torch.device('cuda')
model = model.to(device)

print("model tranfred to gpu")

mean = 255.0 * np.array([0.485, 0.456, 0.406])
stdev = 255.0 * np.array([0.229, 0.224, 0.225])

normalize = torchvision.transforms.Normalize(mean, stdev)

def preprocess(camera_value):
    global device, normalize
    x = camera_value
    x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
    x = x.transpose((2, 0, 1))
    x = torch.from_numpy(x).float()
    x = normalize(x)
    x = x.to(device)
    x = x[None, ...]
    return x

camera = Camera.instance(width=224, height=224)
image = widgets.Image(format='jpeg', width=224, height=224)
speed_slider = 0.12
# camera_link = traitlets.dlink((camera, 'value'), (image, 'value'), transform=bgr8_to_jpeg)

robot = Robot()

def update(change):
    global robot
    x = change['new'] 
    x = preprocess(x)
    y = model(x)
    
    # we apply the `softmax` function to normalize the output vector so it sums to 1 (which makes it a probability distribution)
    y = F.softmax(y, dim=1)
    
    prob_blocked = float(y.flatten()[0])
    
    # blocked_slider.value = prob_blocked
    print(prob_blocked)
    
    if prob_blocked < 0.5:
        print("forward")
        robot.forward(speed_slider)
    else:
        print("left")
        robot.left(speed_slider)
    
    time.sleep(0.0005)


while(1): 
    update({'new': camera.value})  # we call the function once to initialize
    camera.observe(update, names='value')

print("done")