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
    GPIO.setup(buzzerPin, GPIO.OUT, initial=0)
    
    
    with Ultrasonic() as ultrasonic:

       # while loop that runs to constantly check for the ball, obstacles, and boundaries

        try:
            while True:
                # initializes the camera feed and establishes objects for line detection

                distance = ultrasonic.get_distance()
                infra_check = IF.read_all_infrared()
                infra_left = IF.read_one_infrared(1)
                infra_mid = IF.read_one_infrared(2)
                infra_right = IF.read_one_infrared(3)

                # checks to see if a ball is detected, and if it is, checks the color then flashes the LEDs & stops for 5 secs


                # If no ball is detected, it runs the course while checking for objects closer than 30cm and detecting boundaries

                if distance > 18:

                    # if no object is within 30cm & there are no boundaries, it drives straight. Otherwise, it adjusts course

                    if infra_check == 0:

                        PWM.set_motor_model(0,0,0,0)
                        currentPWMValue = [0,0,0,0]
                        
                    elif infra_check == 7:

                        choice = random.randint(0,1)
                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        currentPWMValue = [-1500,-1500,-1500,-1500]
                        time.sleep(.5)

                        if choice:

                            #Turn Right
                            PWM.set_motor_model(1500,1500,-1500,-1500)
                            currentPWMValue = [1500,1500,-1500,-1500]
                            time.sleep(.3)

                        else:

                            #Turn Left
                            PWM.set_motor_model(-1500,-1500,1500,1500)
                            currentPWMValue = [-1500,-1500,1500,1500]
                            time.sleep(.3)

                    if infra_left == 0  and infra_mid == 1 and infra_right == 1:

                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        time.sleep(0.3)
                        PWM.set_motor_model(1500,1500,-1500,-1500)
                        time.sleep(.5)
                        PWM.set_motor_model(650,650,650,650)
                        currentPWMValue = [650,650, 650,650]
                        lastIRValues = [0,1,1]

                    elif infra_left == 1  and infra_mid == 1 and infra_right == 0:

                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        time.sleep(0.3)
                        PWM.set_motor_model(1500,1500,-1500,-1500)
                        time.sleep(.5)
                        PWM.set_motor_model(650,650, 650,650)
                        currentPWMValue = [650,650,650,650]
                        lastIRValues = [1,1,0]
                    
                    # elif infra_left == 0  and infra_mid == 1 and infra_right == 0:

                    #     PWM.set_motor_model(-625,-625,-625,-625)
                    
                    elif infra_left == 0 and infra_mid == 0 and infra_right == 1:

                        if lastIRValues[0] == 1 and lastIRValues[1] == 0 and lastIRValues[2] == 0:

                            backAndForth += 1

                        else:

                            notBackAndForth += 1

                            PWM.set_motor_model(0,0,0,0)
                            #input("Waiting to continue:")
                            PWM.set_motor_model(650,650,650,650)


                        if notBackAndForth > 0:

                            backAndForth = 0
                            notBackAndForth = 0


                        if backAndForth  == 2:

                            PWM.set_motor_model(-1500, -1500, -1500, -1500)
                            time.sleep(0.3)
                            PWM.set_motor_model(-2000,-2000, 2000, 2000)
                            time.sleep(0.8)
                            backAndForth = 0



                        else:

                            PWM.set_motor_model(-1500,-1500,-1500,-1500)
                            time.sleep(0.3)
                            PWM.set_motor_model(-1500,-1500,1500,1500)
                            time.sleep(.5)


                        PWM.set_motor_model(650, 650, 650,650)
                        currentPWMValue = [650,650,650,650]
                        lastIRValues = [0,0,1]
                    
                    elif infra_left == 1 and infra_mid == 0 and infra_right == 0:

                        if lastIRValues[0] == 0 and lastIRValues[1] == 0 and lastIRValues[2] == 1:

                            backAndForth += 1

                        else:

                            notBackAndForth += 1
                            PWM.set_motor_model(0,0,0,0)
                            #input("Waiting to continue:")
                            PWM.set_motor_model(650,650,650,650)
                       
                        if notBackAndForth > 0:

                            backAndForth = 0
                            notBackAndForth = 0


                        if backAndForth == 2:

                            PWM.set_motor_model(-1500,-1500,-1500,-1500)
                            time.sleep(0.3)
                            PWM.set_motor_model(2000,2000,-2000,-2000)
                            time.sleep(0.8)
                            backAndForth = 0


                        else:
                            PWM.set_motor_model(-1500,-1500,-1500,-1500)
                            time.sleep(0.3)
                            PWM.set_motor_model(1500,1500,-1500,-1500)
                            time.sleep(.5)
                       
                        PWM.set_motor_model(650,650,650,650)
                        currentPWMValue = [650,650,650,650]
                        lastIRValues = [1,0,0]
                    
                # If there is an object, it attempts to go around

                else:
                    GPIO.output(buzzerPin, 1)
                    PWM.set_motor_model(-1500,-1500,-1500,-1500)
                    time.sleep(0.75)
                    PWM.set_motor_model(1500,1500,-1500,-1500)
                    time.sleep(0.3)
                    GPIO.output(buzzerPin, 0)
                    None

                if not(round(time.time() - startTime) % 3):
                    print("Taking picture")
                    PWM.set_motor_model(0,0,0,0) 
                    camera.save_image(filename="/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/image.jpg")
                    img = cv2.imread('/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/image.jpg')
                    ballFound, hue_value, xCenter, yCenter = detect.find_ball(img)    
                    PWM.set_motor_model(currentPWMValue[0],currentPWMValue[1],currentPWMValue[2],currentPWMValue[3])
                    if ballFound == True:

                        if 121 <= hue_value <= 160:

                            ballColor = "red"

                        elif 90 <= hue_value <= 120:

                            ballColor = "blue"
                        
                        elif 61 <= hue_value <= 89:

                            ballColor = "green"
                        
                        elif 30 <= hue_value <= 60:

                            ballColor = "yellow"
                        
                        else:

                            print("Color outside Hue range, correction: required.")
                            continue

                        if ballColor in colorList:

                            pass

                        else:

                            ledIndex = [2,3,4,8,16,32,64, 128]

                            if ballColor == "red":
                                for i in ledIndex:
                                    light.ledIndex(i, 255,0,0)

                                PWM.set_motor_model(0,0,0,0)
                                time.sleep(5)
                                colorList.append("red")

                            elif ballColor == "blue":

                                for i in ledIndex:
                                    light.ledIndex(i,0,0,255)
                                PWM.set_motor_model(0,0,0,0)
                                time.sleep(5)
                                colorList.append("blue")

                            elif ballColor == "green":

                                for i in ledIndex:
                                    light.ledIndex(i,0,255,0)
                                PWM.set_motor_model(0,0,0,0)
                                time.sleep(5)
                                colorList.append("green")

                            elif ballColor == "yellow":

                                for i in ledIndex:
                                    light.ledIndex(i,255,255,0)
                                PWM.set_motor_model(0,0,0,0)
                                time.sleep(5)
                                colorList.append("yellow")
                            

        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            print ("\nEnd of program")
        finally:
            camera.close()
            PWM.close()
            IF.close()
            light.colorBlink(0)
            ultrasonic.close()
