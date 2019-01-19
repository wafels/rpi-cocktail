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

# Print the song
def show_song(title):
    print 'Will play this song: ' + title
    return None

# Play the song
def play_song(title):
    subprocess.call("omxplayer " + title, shell=True)
    return None

def play_song_and_notify(title, time_delay_in_seconds):
    show_song(title)
    play_song(title)

    # A short pause before the next song
    time.sleep(time_delay_in_seconds)
    return None


play_list = randomize_mp3_list(mp3_list)
number_of_songs = len(mp3_list)

# Main loop

# Count the number of times the PIR has been detected
pircount = 0

# The PIR is sensitive and can be triggered multiple times
# by a single motion.  This counter counts the number of
# times the PIR is triggered after the initial trigger.
pir_music_trigger_count = 0

# Count the number of times the door has been triggered
doorcount = 0

# Count the number of times a song has been played
play_count = 0

#
first_song_when_door_is_opened = '/home/pi/mp3/John_Wesley_Coleman_-_07_-_Tequila_10_Seconds.mp3'

"""
Basic Behaviour

When the door opens, the initial welcome song is played.
At this point the PIR is not activated.  After the door
is opened, the PIR is available to be triggered.

"""
door_open_for_first_time = False
while True:
    print("Listening for events")

    # Detect if the door is open
    # True means that the door is open
    # False means that the door is closed
    door_open = io.input(door_pin)

    # Print statuses
    print('Door open: ' + str(door_open))
    print('Door open for the first time: ' + str(door_open_for_first_time))

    # If the door is open play the first song 
    if door_open and ~door_open_for_first_time:
        play_song_and_notify(first_song_when_door_is_opened, time_delay_in_seconds)
        door_open_for_first_time = True

    while door_open:
        # Detect motion
        # Check the PIR
        # True means that motion was detected
        # False means that no motion was detected
        motion_detected = io.input(pir_pin)
        door_open = io.input(door_pin)
        print('Motion detected: ' + str(motion_detected))
        if motion_detected and door_open:
            # Advance the PIR Count
            pircount +=1
            print("PIR ALARM! - Motion detected %i " % pircount)

            # Advance the PIR music trigger count
            pir_music_trigger_count = pir_music_trigger_count + 1

            # If we have reached the end of the current randomized
            # play list, randomize the list again and start again
            if play_count > number_of_songs:
                play_list = randomize_mp3_list(mp3_list)
                play_count = 1

            # Get the next mp3
            play_this = play_list[play_count-1]

            # The motion detector has been triggered enough! Now play
            # some music.  A trigger limit is required since the PIR
            # is very sensitive.
            if pir_music_trigger_count > pir_play_trigger_limit:
                print("PIR ALARM! music will now be played")

                # Reset the trigger count
                pir_music_trigger_count = 0

                # Advance the play counter
                play_count = play_count + 1

                # Play it
                play_song_and_notify(play_this, time_delay_in_seconds)

    if ~door_open:
        door_open_for_first_time = False
