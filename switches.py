#
# Initial code to test the detection of events
#
# This script must be run using sudo
#
import time
import subprocess
import random
import glob
import numpy as np
import RPi.GPIO as io
io.setmode(io.BCM)

# Directory holding all the MP3 files
mp3_directory = '/home/pi/mp3'

# The pause between event detection attempts
time_delay_in_seconds = 0.2

# Number of PIR triggers before music is played
pir_play_trigger_limit = 10

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

# Pick a random song from a list
def random_mp3_file(s):
    return random.choice(s)

# Randomize the list of songs
def randomize_mp3_list(s):
    r = list(np.random.permutation(len(s)))
    return [s[x] for x in r]

play_list = randomize_mp3_list(mp3_list)
number_of_songs = len(mp3_list)

# Main loop
pircount = 0
pir_music_trigger_count = 0
doorcount = 0
play_count = 0
while True:
    print("Listening for events")
    play_this = random_mp3_file(mp3_list)

    # Check the PIR
    # True means that motion was detected
    # False means that no motion was detected
    if io.input(pir_pin):
        # Advance the PIR Count
        pircount +=1
        print("PIR ALARM! - Motion detected %i " % pircount)

        # Advance the PIR music trigger count
        pir_music_trigger_count = pir_music_trigger_count + 1

        # The motion detector has been triggered enough! Now play
        # some music.  A trigger limit is required since the PIR
        # is very sensitive.
        if pir_music_trigger_count > pir_play_trigger_limit:
            print("PIR ALARM! music will now be played")

            # Reset the trigger count
            pir_music_trigger_count = 0

            # Play it
            print 'Will play ' + play_this
            subprocess.call("omxplayer " + play_this, shell=True)

    # Check the door
    # True means the door is open
    # False means the door is closed
    if not io.input(door_pin):
        # Advance the door count
        doorcount +=1
        print("DOOR ALARM! - Door close detected %i " % doorcount)

        # Advance the play counter
        play_count = play_count + 1

        # If we have reached the end of the current randomized
        # play list, randomize the list again and start again
        if play_count > number_of_songs:
            play_list = randomize_mp3_list(mp3_list)
            play_count = 1

        # Get the next mp3
        play_this = play_list[play_count-1]

        # Play it
        subprocess.call("omxplayer " + play_this, shell=True)

    time.sleep(time_delay_in_seconds)

