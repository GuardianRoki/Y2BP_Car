from courseNav import Ordinary_Car
from pca9685 import PCA9685
from gpiozero import DistanceSensor, PWMSoftwareFallback, DistanceSensorNoEcho
import warnings
import time 
from ultrasonic import Ultrasonic

if __name__ == '__main__':
    PWM = Ordinary_Car()
    counter = 0
    with Ultrasonic() as ultrasonic:
        try:
            while True:

                distance = ultrasonic.get_distance() # Get the distance measurement in centimeters
                print(f"The distance in cm is: {distance}")

                if distance > 30:

                    PWM.set_motor_model(2000,2000,2000,2000) #Forward
                else:
                 
                    PWM.set_motor_model(-2000,-2000,-2000,-2000) #Back

        except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
            print ("\nEnd of program")
        finally:
            PWM.close()

