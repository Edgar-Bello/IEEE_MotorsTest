import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


# Front Left
FL_IN1 = 5
FL_IN2 = 6
FL_EN  = 12

# Front Right
FR_IN1 = 20
FR_IN2 = 21
FR_EN  = 13

# Back Left
BL_IN1 = 16
BL_IN2 = 19
BL_EN  = 18

# Back Right
BR_IN1 = 23
BR_IN2 = 24
BR_EN  = 25

motor_pins = [
    FL_IN1, FL_IN2, FL_EN,
    FR_IN1, FR_IN2, FR_EN,
    BL_IN1, BL_IN2, BL_EN,
    BR_IN1, BR_IN2, BR_EN
]

GPIO.setup(motor_pins, GPIO.OUT)


FL_ENC_A = 17
FL_ENC_B = 27

FR_ENC_A = 22
FR_ENC_B = 10

BL_ENC_A = 9
BL_ENC_B = 11

BR_ENC_A = 0
BR_ENC_B = 1

encoder_pins = [
    FL_ENC_A, FL_ENC_B,
    FR_ENC_A, FR_ENC_B,
    BL_ENC_A, BL_ENC_B,
    BR_ENC_A, BR_ENC_B
]

GPIO.setup(encoder_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)


fl_pwm = GPIO.PWM(FL_EN, 1000)
fr_pwm = GPIO.PWM(FR_EN, 1000)
bl_pwm = GPIO.PWM(BL_EN, 1000)
br_pwm = GPIO.PWM(BR_EN, 1000)

fl_pwm.start(0)
fr_pwm.start(0)
bl_pwm.start(0)
br_pwm.start(0)

fl_count = 0
fr_count = 0
bl_count = 0
br_count = 0


def fl_encoder(channel):
    global fl_count
    if GPIO.input(FL_ENC_B):
        fl_count += 1
    else:
        fl_count -= 1

def fr_encoder(channel):
    global fr_count
    if GPIO.input(FR_ENC_B):
        fr_count += 1
    else:
        fr_count -= 1

def bl_encoder(channel):
    global bl_count
    if GPIO.input(BL_ENC_B):
        bl_count += 1
    else:
        bl_count -= 1

def br_encoder(channel):
    global br_count
    if GPIO.input(BR_ENC_B):
        br_count += 1
    else:
        br_count -= 1


GPIO.add_event_detect(FL_ENC_A, GPIO.BOTH, callback=fl_encoder)
GPIO.add_event_detect(FR_ENC_A, GPIO.BOTH, callback=fr_encoder)
GPIO.add_event_detect(BL_ENC_A, GPIO.BOTH, callback=bl_encoder)
GPIO.add_event_detect(BR_ENC_A, GPIO.BOTH, callback=br_encoder)


def motors_forward(speed=60):

    GPIO.output(FL_IN1, GPIO.HIGH)
    GPIO.output(FL_IN2, GPIO.LOW)

    GPIO.output(FR_IN1, GPIO.HIGH)
    GPIO.output(FR_IN2, GPIO.LOW)

    GPIO.output(BL_IN1, GPIO.HIGH)
    GPIO.output(BL_IN2, GPIO.LOW)

    GPIO.output(BR_IN1, GPIO.HIGH)
    GPIO.output(BR_IN2, GPIO.LOW)

    fl_pwm.ChangeDutyCycle(speed)
    fr_pwm.ChangeDutyCycle(speed)
    bl_pwm.ChangeDutyCycle(speed)
    br_pwm.ChangeDutyCycle(speed)


def stop_motors():
    fl_pwm.ChangeDutyCycle(0)
    fr_pwm.ChangeDutyCycle(0)
    bl_pwm.ChangeDutyCycle(0)
    br_pwm.ChangeDutyCycle(0)


try:

    print("Starting mecanum motor + encoder test")

    motors_forward(60)

    while True:

        print(
            "FL:", fl_count,
            "FR:", fr_count,
            "BL:", bl_count,
            "BR:", br_count
        )

        time.sleep(0.2)

except KeyboardInterrupt:
    pass

finally:
    stop_motors()
    GPIO.cleanup()