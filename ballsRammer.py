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

def picture(PWM,camera,ballTargets):

    print("Taking picture-\n")
    PWM.set_motor_model(0,0,0,0)
    time.sleep(0.5)
    camera.save_image(filename="/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/image.jpg")
    img = cv2.imread('/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/image.jpg')  
    ballFound, hue_value, xCenter, yCenter = detect.find_ball(img, ballTargets[0])  
    PWM.set_motor_model(currentPWMValue[0],currentPWMValue[1],currentPWMValue[2],currentPWMValue[3])
    return ballFound, hue_value, xCenter, yCenter

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

def eliminate(ballTargets, ballColor, PWM, IF, xCenter, yCenter, xMax, yMax):

    elseCounter = 0
    ballFound = None
    hue_value = None
    ramVal = False
    startTime = time.time()

    print(f"First while loop check in eliminate: {ballColor} == {ballTargets[0]}")
    # input("Waiting for input")
    while ballColor == ballTargets[0]:

        infra_check = IF.read_all_infrared()

        if infra_check > 0:

            PWM.set_motor_model(-1500,-1500,-1500,-1500)
            time.sleep(1)
            PWM.set_motor_model(0,0,0,0)
            del ballTargets[0]
            print(ballTargets)
            print(ballColor)
            return
       
        if ramVal == False:

            if 1 <= xCenter <= 80:
                print("Left quadrant.")
                turnLeft(PWM, 0.125)
                ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)

            elif xCenter <= 175:
                print("Middle left quadrant")
                turnLeft(PWM, 0.0725)
                ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
           
            elif xCenter <= 230:
               
                if 0 < yCenter <= 212:

                    forward(PWM, 0.7)
                    ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
                    continue  

                elif yCenter <= 300:

                    # input("Ramming")
                    ram(PWM)
                    ramVal = True
                    continue
           
            elif xCenter <= 320:
                print("Right middle quadrant")
                turnRight(PWM, 0.0725)
                ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
           
            elif xCenter <= 400:
                print("Far right quadrant")
                turnRight(PWM, 0.125)
                ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
           
            else:
                elseCounter += 1
                print("Ball not in frame")
                turnLeft(PWM, 0.125)
                ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
          
            if elseCounter == 3:
                return
            # if not(round(time.time() - startTime) % 3):

            #     ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)

        print(f"In while loop check eliminate: {ballColor} == {ballTargets[0]}")

def illuminate(ballTargets, ballColor, light, fate):

    ledIndex = [2,3,4,8,16,32,64,128]
    ledLeft = [2, 4, 16, 64]
    ledRight = [3, 8, 32, 128]

    if fate == "hunt":

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
    
        else:

            pass
        
    elif fate == "search":

        if ballTargets[0] == "red":
            for i in ledLeft:
                light.ledIndex(i, 255,0,0)

        elif ballTargets[0] == "blue":

            for i in ledLeft:
                light.ledIndex(i,0,0,255)

        elif ballTargets[0] == "green":

            for i in ledLeft:
                light.ledIndex(i,0,255,0)

        elif ballTargets[0] == "yellow":

            for i in ledLeft:
                light.ledIndex(i,255,255,0)
            
    elif fate == "search" or fate == "hunt":

        if ballTargets[0] == "red" and ballColor == "red":

            for i in ledIndex:
                light.ledIndex(i, 255, 0, 0)
        
        elif ballTargets[0] == "blue" and ballColor == "blue":

            for i in ledIndex:
                light.ledIndex(i, 0, 0, 255)
        
        elif ballTargets[0] == "green" and ballColor == "green":

            for i in ledIndex:
                light.ledIndex(i, 0, 255, 0)
            
        elif ballTargets[0] == "yellow" and ballColor == "yellow":

            for i in ledIndex:
                light.ledIndex(255, 255, 0)

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
    ballTargets = []
    colorOptions = ["red","blue","green","yellow"]
    GPIO.setup(buzzerPin, GPIO.OUT, initial=0)
    xMax = 400
    yMax = 300
   
    with Ultrasonic() as ultrasonic:

       # while loop that runs to constantly check for the ball, obstacles, and boundaries

        try:

            for i in range(4):

                ballMark = input(f"Target color {i+1}: ")

                if ballMark.lower() not in colorOptions:

                    while ballMark.lower() not in colorOptions:

                        print("Incorrect input - Retry\n")
                        ballMark = input(f"Target color {i+1}: ")

                print(ballMark)
                ballTargets.append(ballMark)

            print(ballTargets)
            ballColor = None

            turnRight(PWM, 1)
            ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
            ballColor = transcendance(hue_value)
           
            # input("Done taking picture")

            while len(ballTargets):

                if ballColor == ballTargets[0]:

                    illuminate(ballTargets, ballColor, light, "search")
                    eliminate(ballTargets, ballColor, PWM, IF, xCenter, yCenter, xMax, yMax)
                    ballColor = None
                    light.colorBlink(0)

                else:

                    illuminate(ballTargets, ballColor, light, "search")
                    turnLeft(PWM, 0.4)
                    ballFound, hue_value, xCenter, yCenter = picture(PWM, camera, ballTargets)
                    ballColor = transcendance(hue_value)
                    illuminate(ballTargets, ballColor, light, "hunt")
                    print(ballTargets)
                                
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            print ("\nEnd of program")
        finally:
            camera.close()
            PWM.close()
            IF.close()
            light.colorBlink(0)
            ultrasonic.close()
