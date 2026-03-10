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


FL_ENC_A = 4   # It might change
FL_ENC_B = 18  # It might change

FR_ENC_A = 19  # It might change
FR_ENC_B = 26  # It might change

BL_ENC_A = 12  # It might change
BL_ENC_B = 7   # It might change

BR_ENC_A = 8   # It might change
BR_ENC_B = 9   # It might change


motor_pins = [
    FL_IN1,FL_IN2,FL_EN,
    FR_IN1,FR_IN2,FR_EN,
    BL_IN1,BL_IN2,BL_EN,
    BR_IN1,BR_IN2,BR_EN
]

for p in motor_pins:
    GPIO.setup(p,GPIO.OUT)

encoder_pins = [
    FL_ENC_A,FL_ENC_B,
    FR_ENC_A,FR_ENC_B,
    BL_ENC_A,BL_ENC_B,
    BR_ENC_A,BR_ENC_B
]

for p in encoder_pins:
    GPIO.setup(p,GPIO.IN,pull_up_down=GPIO.PUD_UP)


FL_pwm = GPIO.PWM(FL_EN,1000)
FR_pwm = GPIO.PWM(FR_EN,1000)
BL_pwm = GPIO.PWM(BL_EN,1000)
BR_pwm = GPIO.PWM(BR_EN,1000)

FL_pwm.start(0)
FR_pwm.start(0)
BL_pwm.start(0)
BR_pwm.start(0)


encoder_counts = {
    "fl":0,
    "fr":0,
    "bl":0,
    "br":0
}


def fl_encoder(channel):
    if GPIO.input(FL_ENC_B):
        encoder_counts["fl"] += 1
    else:
        encoder_counts["fl"] -= 1

def fr_encoder(channel):
    if GPIO.input(FR_ENC_B):
        encoder_counts["fr"] += 1
    else:
        encoder_counts["fr"] -= 1

def bl_encoder(channel):
    if GPIO.input(BL_ENC_B):
        encoder_counts["bl"] += 1
    else:
        encoder_counts["bl"] -= 1

def br_encoder(channel):
    if GPIO.input(BR_ENC_B):
        encoder_counts["br"] += 1
    else:
        encoder_counts["br"] -= 1

GPIO.add_event_detect(FL_ENC_A,GPIO.RISING,callback=fl_encoder,bouncetime=1)
GPIO.add_event_detect(FR_ENC_A,GPIO.RISING,callback=fr_encoder,bouncetime=1)
GPIO.add_event_detect(BL_ENC_A,GPIO.RISING,callback=bl_encoder,bouncetime=1)
GPIO.add_event_detect(BR_ENC_A,GPIO.RISING,callback=br_encoder,bouncetime=1)


def set_motor(in1,in2,pwm,power):

    if power >= 0:
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
    else:
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)

    pwm.ChangeDutyCycle(abs(power)*100)

def set_drive_power(fl,fr,bl,br):

    set_motor(FL_IN1,FL_IN2,FL_pwm,fl)
    set_motor(FR_IN1,FR_IN2,FR_pwm,fr)
    set_motor(BL_IN1,BL_IN2,BL_pwm,bl)
    set_motor(BR_IN1,BR_IN2,BR_pwm,br)

def stop_drive():
    set_drive_power(0,0,0,0)



print("Calibration ready.")
input("Place robot at start line and press ENTER")

encoder_counts = {"fl":0,"fr":0,"bl":0,"br":0}

print("Driving forward for calibration...")

set_drive_power(0.3,0.3,0.3,0.3)

input("Press ENTER when robot reaches measured distance")

stop_drive()

ticks = (
    abs(encoder_counts["fl"]) +
    abs(encoder_counts["fr"]) +
    abs(encoder_counts["bl"]) +
    abs(encoder_counts["br"])
) / 4

distance = float(input("Enter distance traveled in inches: "))

inches_per_tick = distance / ticks

print("\n===== CALIBRATION RESULT =====")
print("Ticks:",ticks)
print("Distance:",distance)
print("INCHES_PER_TICK =",inches_per_tick)

GPIO.cleanup()