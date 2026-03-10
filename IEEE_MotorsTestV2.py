import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

FL_IN1 = 17  # It might change
FL_IN2 = 27  # It might change
FL_EN  = 22  # It might change

FR_IN1 = 5   # It might change
FR_IN2 = 6   # It might change
FR_EN  = 13  # It might change

BL_IN1 = 23  # It might change
BL_IN2 = 24  # It might change
BL_EN  = 25  # It might change

BR_IN1 = 16  # It might change
BR_IN2 = 20  # It might change
BR_EN  = 21  # It might change

motor_pins = [
    FL_IN1,FL_IN2,FL_EN,
    FR_IN1,FR_IN2,FR_EN,
    BL_IN1,BL_IN2,BL_EN,
    BR_IN1,BR_IN2,BR_EN
]

for p in motor_pins:
    GPIO.setup(p,GPIO.OUT)

FL_pwm = GPIO.PWM(FL_EN,1000)
FR_pwm = GPIO.PWM(FR_EN,1000)
BL_pwm = GPIO.PWM(BL_EN,1000)
BR_pwm = GPIO.PWM(BR_EN,1000)

FL_pwm.start(0)
FR_pwm.start(0)
BL_pwm.start(0)
BR_pwm.start(0)

def run_motor(in1,in2,pwm,name):

    print("Running",name)

    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)

    pwm.ChangeDutyCycle(50)

    time.sleep(2)

    pwm.ChangeDutyCycle(0)

    time.sleep(1)

try:

    while True:

        run_motor(FL_IN1,FL_IN2,FL_pwm,"Front Left")
        run_motor(FR_IN1,FR_IN2,FR_pwm,"Front Right")
        run_motor(BL_IN1,BL_IN2,BL_pwm,"Back Left")
        run_motor(BR_IN1,BR_IN2,BR_pwm,"Back Right")

except KeyboardInterrupt:

    GPIO.cleanup()