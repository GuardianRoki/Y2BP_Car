import time
from infrared import Infrared
from control import Ordinary_Car
from pca9685 import PCA9685
from led import Led
from ultrasonic import Ultrasonic

if __name__=='__main__':
    PWM = Ordinary_Car()  
    IF = Infrared()   
    with Ultrasonic() as ultrasonic:
        try:
            while True:
                distance = ultrasonic.get_distance()
                infra_check = IF.read_all_infrared()
                infra_left = IF.read_one_infrared(1)
                infra_mid = IF.read_one_infrared(2)
                infra_right = IF.read_one_infrared(3)

                if distance > 50:

                    if infra_check == 0:

                        PWM.set_motor_model(625,625,625,625)
                        
                    elif infra_check == 7:

                        PWM.set_motor_model(-675,-675,-675,-675)

                    if infra_left == 0  and infra_mid == 1 and infra_right == 1:

                        PWM.set_motor_model(640,640,625,625)
                        time.sleep(.3)
                        PWM.set_motor_model(625,625,625,625)

                    elif infra_left == 1  and infra_mid == 1 and infra_right == 0:

                        PWM.set_motor_model(625,625,640,640)
                        time.sleep(.3)
                        PWM.set_motor_model(625,625,625,625)
                    
                    elif infra_left == 0  and infra_mid == 1 and infra_right == 0:

                        PWM.set_motor_model(-625,-625,-625,-625)
                    
                    elif infra_left == 0 and infra_mid == 0 and infra_right == 1:

                        PWM.set_motor_model(-1500,-1500,1500,1500)
                    
                    elif infra_left == 1 and infra_mid == 0 and infra_right == 0:

                        PWM.set_motor_model(1500,1500,-1500,-1500)

                else:

                    PWM.set_motor_model(-2000,-2000,-2000,-2000)
                    time.sleep(1)
            
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            print ("\nEnd of program")
        finally:
            PWM.close()
