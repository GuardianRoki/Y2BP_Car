import time
from infrared import Infrared
from control import Ordinary_Car
from pca9685 import PCA9685
from ultrasonic import Ultrasonic
import random




if __name__=='__main__':
    PWM = Ordinary_Car()  
    IF = Infrared()        
    ultraSensor = Ultrasonic()
    lastIRValues = [0,0,0]
    backAndForth = 0
    notBackAndForth = 0
    try:
        while True:
            infra_check = IF.read_all_infrared()
            infra_left = IF.read_one_infrared(1)
            infra_mid = IF.read_one_infrared(2)
            infra_right = IF.read_one_infrared(3)
            distance = ultraSensor.get_distance()

            if distance > 10:

                    # if no object is within 30cm & there are no boundaries, it drives straight. Otherwise, it adjusts course

                    if infra_check == 0:

                        PWM.set_motor_model(650,650,650,650)
                        
                    elif infra_check == 7:

                        choice = random.randint(0,1)
                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        time.sleep(.5)

                        if choice:

                            #Turn Right
                            PWM.set_motor_model(1500,1500,-1500,-1500)
                            time.sleep(.3)

                        else:

                            #Turn Left
                            PWM.set_motor_model(-1500,-1500,1500,1500)
                            time.sleep(.3)

                    if infra_left == 0  and infra_mid == 1 and infra_right == 1:

                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        time.sleep(0.3)
                        PWM.set_motor_model(1500,1500,-1500,-1500)
                        time.sleep(.5)
                        PWM.set_motor_model(650,650,650,650)
                        lastIRValues = [0,1,1]

                    elif infra_left == 1  and infra_mid == 1 and infra_right == 0:

                        PWM.set_motor_model(-1500,-1500,-1500,-1500)
                        time.sleep(0.3)
                        PWM.set_motor_model(1500,1500,-1500,-1500)
                        time.sleep(.5)
                        PWM.set_motor_model(650,650, 650,650)
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


                        if notBackAndForth > 2:

                            backAndForth = 0
                            notBackAndForth = 0


                        if backAndForth  == 3:

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
                        lastIRValues = [0,0,1]
                    
                    elif infra_left == 1 and infra_mid == 0 and infra_right == 0:

                        if lastIRValues[0] == 0 and lastIRValues[1] == 0 and lastIRValues[2] == 1:

                            backAndForth += 1

                        else:

                            notBackAndForth += 1

                            PWM.set_motor_model(0,0,0,0)
                            #input("Waiting to continue:")
                            PWM.set_motor_model(650,650,650,650)
                       
                        if notBackAndForth > 2:

                            backAndForth = 0
                            notBackAndForth = 0


                        if backAndForth == 3:

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
                        lastIRValues = [1,0,0]
                    
                # If there is an object, it attempts to go around

            else:

                #PWM.set_motor_model(-1000,-1000,-1000,-1000)
                #time.sleep(1)
                #PWM.set_motor_model(1500,1500,-1500,-1500)
                #time.sleep(.5)
                #PWM.set_motor_model(625,625,625,625)
                #time.sleep(.5)
                #PWM.set_motor_model(-1500,-1500,1500,1500)
                #time.sleep(1)
                #PWM.set_motor_model(625,625,625,625)
                #time.sleep(.5)
                #PWM.set_motor_model(1500,1500,-1500,-1500)
                #time.sleep(.5)
                None
            
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        print ("\nEnd of program")
    finally:
        PWM.close()
