#
# Initial code to test the detection of events
#
# This script must be run using sudo
#
import time
import subprocess
import random
import glob
import RPi.GPIO as io
io.setmode(io.BCM)

# Directory holding all the MP3 files
mp3_directory = '/home/pi/mp3'


# Passive infrared (PIR) motion sensor pin on the breadboard
pir_pin = 18

# Door pin on the breadboard
door_pin = 23

# Activate input of the PIR
io.setup(pir_pin, io.IN)

# Activate input of the door
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)

# Get a list of all the mp3 files
mp3_list = glob.glob(mp3_directory + '/*.mp3')

def random_mp3_file(s):
    return random.choice(s)
    

# Main loop
pircount = 0
doorcount = 0
while True:
    play_this = random_mp3_file(mp3_list)
    if io.input(pir_pin):
        pircount +=1 
        print("PIR ALARM! - Motion detected %i " % pircount)
        print 'Will play ' + play_this
        subprocess.call("omxplayer " + play_this, shell=True)
    if not io.input(door_pin):
        doorcount +=1
        print("DOOR ALARM! - Door close detected %i " % doorcount)
    time.sleep(0.2)

