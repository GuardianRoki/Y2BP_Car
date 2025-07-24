import time
import random
import yolov5
import cv2
import os
import numpy as np
from infrared import Infrared
from control import Ordinary_Car
from pca9685 import PCA9685
from led import Led
from camera import Camera
import DetectBalls_w_color as detect
from ultrasonic import Ultrasonic
import RPi.GPIO as GPIO

def forward(PWM, duration):

    PWM.set_motor_model(650,650,650,650)
    time.sleep(duration)
    PWM.set_motor_model(0, 0, 0, 0)
    currentPWMValue = [0, 0, 0, 0]
   
# drives the car fast as to ram an object

def ram(PWM):

    PWM.set_motor_model(3000,3000,3000,3000)
    currentPWMValue = [3000, 3000, 3000, 3000]

# turns the car right

def turnRight(PWM, duration):

    PWM.set_motor_model(2000,2000,-2000,-2000)
    time.sleep(duration)
    PWM.set_motor_model(0,0,0,0)

# turns the car left

def turnLeft(PWM, duration):

    PWM.set_motor_model(-2000,-2000,2000,2000)
    time.sleep(duration)
    PWM.set_motor_model(0,0,0,0)

def picture(PWM,camera,targets):

    print("Taking picture-\n")
    PWM.set_motor_model(0,0,0,0)
    time.sleep(0.5)
    camera.save_image(filename="/home/circlekenjoyers/raspPi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/image.jpg")
    img = cv2.imread('/home/circlekenjoyers/raspPi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/image.jpg')  
    objectName, hue_value, xCenter, yCenter = detect.find_ball(img, targets[0])  
    PWM.set_motor_model(currentPWMValue[0],currentPWMValue[1],currentPWMValue[2],currentPWMValue[3])
    return objectName, hue_value, xCenter, yCenter

def transcendance(hue_value):

    ballColor = None

    if 121 <= hue_value <= 185:

        ballColor = "red"

    elif 90 <= hue_value <= 120:

        ballColor = "blue"

    elif 61 <= hue_value <= 89:

        ballColor = "green"

    elif 20 <= hue_value <= 60:

        ballColor = "yellow"
   
    return ballColor

def eliminate(targets, ballColor, PWM, IF, xCenter, yCenter, xMax, yMax):

    elseCounter = 0
    objectName = None
    hue_value = None
    ramVal = False
    startTime = time.time()

    print(f"First while loop check in eliminate: {ballColor} == {targets[0]}")
    while ballColor == targets[0]:

        infra_check = IF.read_all_infrared()

        if infra_check > 0:

            PWM.set_motor_model(-1500,-1500,-1500,-1500)
            time.sleep(1)
            PWM.set_motor_model(0,0,0,0)
            del targets[0]
            print(targets)
            print(ballColor)
            return
       
        if ramVal == False:

            if 1 <= xCenter <= 80:
                print("Left quadrant.")
                turnLeft(PWM, 0.125)
                objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)

            elif xCenter <= 175:
                print("Middle left quadrant")
                turnLeft(PWM, 0.0725)
                objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
           
            elif xCenter <= 230:
               
                if 0 < yCenter <= 212:
                    forward(PWM, 0.7)
                    objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
                    continue  

                elif yCenter <= 300:
                    ram(PWM)
                    ramVal = True
                    continue
           
            elif xCenter <= 320:
                print("Right middle quadrant")
                turnRight(PWM, 0.0725)
                objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
           
            elif xCenter <= 400:
                print("Far right quadrant")
                turnRight(PWM, 0.125)
                objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
           
            else:
                elseCounter += 1
                print("Ball not in frame")
                turnLeft(PWM, 0.125)
                objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
          
            if elseCounter == 3:
                return

        print(f"In while loop check eliminate: {ballColor} == {targets[0]}")

def illuminate(targets, ballColor, light, fate, genesis, colorDict):

    ledIndex = [2,3,4,8,16,32,64,128]
    ledLeft = [4,8,16,32]
    ledRight = [2,3,64,128]
    colorList = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "pink"]

    
    if ballColor == None:
        light.colorBlink(0)

    if fate == "hunt":

        if genesis == "ball":

            if ballColor == "red":
                for i in ledRight:
                    light.ledIndex(i, 255,0,0)

            elif ballColor == "blue":

                for i in ledRight:
                    light.ledIndex(i,0,0,255)

            elif ballColor == "green":

                for i in ledRight:
                    light.ledIndex(i,0,255,0)

            elif ballColor == "yellow":

                for i in ledRight:
                    light.ledIndex(i,255,255,0)

        elif genesis == "item":

            light.rainbowCycle()
            time.sleep(5)
        
    elif fate == "search":

        if genesis == "ball":

            if targets[0] == "red":
                for i in ledLeft:
                    light.ledIndex(i, 255,0,0)

            elif targets[0] == "blue":

                for i in ledLeft:
                    light.ledIndex(i,0,0,255)

            elif targets[0] == "green":

                for i in ledLeft:
                    light.ledIndex(i,0,255,0)

            elif targets[0] == "yellow":

                for i in ledLeft:
                    light.ledIndex(i,255,255,0)

        elif genesis == "item":

            for index in ledIndex:

                colorReceive = colorDict[colorList[index]]
                light.ledIndex(index, *colorReceive)
                time.sleep(1)
                light.colorBlink(0)


def acknowledge(targets):

    print()

if __name__=='__main__':
    startTime = time.time()
    GPIO.setmode(GPIO.BCM)
    # Establishes objects for most of the imported classes as well as the list for already detected colors
   
    PWM = Ordinary_Car()  
    IF = Infrared()
    camera = Camera()
    camera.start_stream()
    light = Led()  
    colorList = []
    lastIRValues = [0,0,0]
    backAndForth = 0
    notBackAndForth = 0
    currentPWMValue = [0,0,0,0]
    buzzerPin = 17
    targets = []
    colorOptions = ["red","blue","green","yellow"]
    itemOptions = ["pendant", "battery"]
    colorDict = {"red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255], "yellow": [255, 255, 0], 
                 "purple": [128, 0, 128], "orange": [255, 165, 0], "cyan": [0, 255, 255], "pink": [255, 20, 147]}
    GPIO.setup(buzzerPin, GPIO.OUT, initial=0)
    xMax = 400
    yMax = 300
   
    with Ultrasonic() as ultrasonic:

        try:

            for i in range(6):

                hitMark = input(f"Target {i+1}: ")

                if hitMark.lower() not in colorOptions or itemOptions:

                    while hitMark.lower() not in colorOptions or itemOptions:

                        print("Incorrect input - Retry\n")
                        hitMark = input(f"Target {i+1}: ")

                targets.append(hitMark)

            ballColor = None

            if targets[0] in colorOptions:
                illuminate(targets, ballColor, light, "search", "ball", colorDict)
            else:
                illuminate(targets, ballColor, light, "search", "item", colorDict)

            turnRight(PWM, 1)
            objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
            ballColor = transcendance(hue_value)
           
            while len(targets):

                if ballColor == targets[0]:

                    illuminate(targets, ballColor, light, "hunt", "ball", colorDict)
                    eliminate(targets, ballColor, PWM, IF, xCenter, yCenter, xMax, yMax)
                    ballColor = None
                    light.colorBlink(0)

                else:

                    illuminate(targets, ballColor, light, "search", "ball", colorDict)
                    turnLeft(PWM, 0.4)
                    objectName, hue_value, xCenter, yCenter = picture(PWM, camera, targets)
                    ballColor = transcendance(hue_value)
                    illuminate(targets, ballColor, light, "hunt", "ball", colorDict)
                    print(targets)
                                
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            print ("\nEnd of program")
        finally:
            camera.close()
            PWM.close()
            IF.close()
            light.colorBlink(0)
            ultrasonic.close()
