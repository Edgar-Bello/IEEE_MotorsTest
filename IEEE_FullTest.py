import time
import math
import RPi.GPIO as GPIO

WHEEL_DIAMETER = 4.0  # is in inches and will probably change
ENCODER_PULSES_PER_REV = 330  # depends on gear ratio of your motor

WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER
INCHES_PER_TICK = WHEEL_CIRCUMFERENCE / ENCODER_PULSES_PER_REV

ROBOT_RADIUS = 8.0   # distance from center to wheel (inches)

USE_IMU = True

FL_INVERT = False
FR_INVERT = True
BL_INVERT = False
BR_INVERT = True

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


IMU_SDA = 2  # It might change
IMU_SCL = 3  # It might change


motor_pins = [
    FL_IN1, FL_IN2, FL_EN,
    FR_IN1, FR_IN2, FR_EN,
    BL_IN1, BL_IN2, BL_EN,
    BR_IN1, BR_IN2, BR_EN
]

for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

encoder_pins = [
    FL_ENC_A, FL_ENC_B,
    FR_ENC_A, FR_ENC_B,
    BL_ENC_A, BL_ENC_B,
    BR_ENC_A, BR_ENC_B
]

for pin in encoder_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


FL_pwm = GPIO.PWM(FL_EN, 1000)
FR_pwm = GPIO.PWM(FR_EN, 1000)
BL_pwm = GPIO.PWM(BL_EN, 1000)
BR_pwm = GPIO.PWM(BR_EN, 1000)

FL_pwm.start(0)
FR_pwm.start(0)
BL_pwm.start(0)
BR_pwm.start(0)


encoder_counts = {
    "fl": 0,
    "fr": 0,
    "bl": 0,
    "br": 0
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

GPIO.add_event_detect(FL_ENC_A, GPIO.RISING, callback=fl_encoder, bouncetime=1)
GPIO.add_event_detect(FR_ENC_A, GPIO.RISING, callback=fr_encoder, bouncetime=1)
GPIO.add_event_detect(BL_ENC_A, GPIO.RISING, callback=bl_encoder, bouncetime=1)
GPIO.add_event_detect(BR_ENC_A, GPIO.RISING, callback=br_encoder, bouncetime=1)


odom_x = 0.0
odom_y = 0.0
odom_theta = 0.0


def get_encoders():
    return encoder_counts.copy()

def get_imu_rotation():
    return 0.0


def set_motor(in1, in2, pwm, power, invert=False):

    if invert:
        power = -power

    if power >= 0:
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
    else:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)

    pwm.ChangeDutyCycle(abs(power) * 100)


def set_drive_power(fl, fr, bl, br):

    set_motor(FL_IN1, FL_IN2, FL_pwm, fl, FL_INVERT)
    set_motor(FR_IN1, FR_IN2, FR_pwm, fr, FR_INVERT)
    set_motor(BL_IN1, BL_IN2, BL_pwm, bl, BL_INVERT)
    set_motor(BR_IN1, BR_IN2, BR_pwm, br, BR_INVERT)

def stop_drive():
    set_drive_power(0,0,0,0)


def update_odometry(prev):

    global odom_x, odom_y, odom_theta

    curr = get_encoders()

    dFL = (curr["fl"] - prev["fl"]) * INCHES_PER_TICK
    dFR = (curr["fr"] - prev["fr"]) * INCHES_PER_TICK
    dBL = (curr["bl"] - prev["bl"]) * INCHES_PER_TICK
    dBR = (curr["br"] - prev["br"]) * INCHES_PER_TICK

    d_forward = (dFL + dFR + dBL + dBR) / 4.0
    d_strafe  = (-dFL + dFR + dBL - dBR) / 4.0

    if USE_IMU:
        curr_imu = get_imu_rotation()
        d_theta = math.radians(curr_imu - prev["imu"])
        prev["imu"] = curr_imu
    else:
        d_theta = (-dFL + dFR - dBL + dBR) / (4.0 * ROBOT_RADIUS)

    avg_theta = odom_theta + d_theta/2

    odom_x += d_strafe * math.cos(avg_theta) - d_forward * math.sin(avg_theta)
    odom_y += d_strafe * math.sin(avg_theta) + d_forward * math.cos(avg_theta)

    odom_theta += d_theta

    while odom_theta > math.pi:
        odom_theta -= 2*math.pi

    while odom_theta < -math.pi:
        odom_theta += 2*math.pi

    prev.update(curr)


def mecanum_drive(forward, strafe, turn):

    fl = forward + strafe + turn
    fr = forward - strafe - turn
    bl = forward - strafe + turn
    br = forward + strafe - turn

    max_val = max(abs(fl),abs(fr),abs(bl),abs(br),1.0)

    fl /= max_val
    fr /= max_val
    bl /= max_val
    br /= max_val

    set_drive_power(fl,fr,bl,br)


def go_to_point(target_x,target_y):

    while True:

        update_odometry(prev_state)

        dx = target_x - odom_x
        dy = target_y - odom_y

        distance = math.sqrt(dx**2 + dy**2)

        if distance < 0.5:
            break

        target_angle = math.atan2(dy,dx)

        angle_error = target_angle - odom_theta

        while angle_error > math.pi:
            angle_error -= 2*math.pi

        while angle_error < -math.pi:
            angle_error += 2*math.pi

        forward = math.cos(angle_error)*distance*0.5
        strafe  = math.sin(angle_error)*distance*0.5
        turn    = angle_error

        forward = max(min(forward,0.6),-0.6)
        strafe  = max(min(strafe,0.6),-0.6)
        turn    = max(min(turn,0.5),-0.5)

        mecanum_drive(forward,strafe,turn)

        time.sleep(0.01)

    stop_drive()


def turn_to_angle(target_theta):

    while True:

        update_odometry(prev_state)

        error = target_theta - odom_theta

        while error > math.pi:
            error -= 2*math.pi

        while error < -math.pi:
            error += 2*math.pi

        if abs(error) < 0.01:
            break

        turn = max(min(error*1.2,0.5),-0.5)

        mecanum_drive(0,0,turn)

        time.sleep(0.01)

    stop_drive()


def autonomous():

    print("Starting autonomous...")

    go_to_point(24,0)
    go_to_point(24,24)
    turn_to_angle(math.pi)

    print("Done.")


if __name__ == "__main__":

    prev_state = get_encoders()

    if USE_IMU:
        prev_state["imu"] = get_imu_rotation()

    autonomous()

    GPIO.cleanup()