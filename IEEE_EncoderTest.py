import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

FL_ENC_A = 4   # It might change
FL_ENC_B = 18  # It might change

FR_ENC_A = 19  # It might change
FR_ENC_B = 26  # It might change

BL_ENC_A = 12  # It might change
BL_ENC_B = 7   # It might change

BR_ENC_A = 8   # It might change
BR_ENC_B = 9   # It might change

encoder_counts = {
    "fl":0,
    "fr":0,
    "bl":0,
    "br":0
}

pins = [
    FL_ENC_A,FL_ENC_B,
    FR_ENC_A,FR_ENC_B,
    BL_ENC_A,BL_ENC_B,
    BR_ENC_A,BR_ENC_B
]

for p in pins:
    GPIO.setup(p,GPIO.IN,pull_up_down=GPIO.PUD_UP)

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

print("Encoder test started. Spin wheels.")

try:
    while True:
        print(encoder_counts)
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()