#
# Code to find songs and play them in reaction
# to events triggered through the door detector
# and the motion detector
#
# Run the script using the crontab
# For example, on rebooting.
# @reboot sudo /usr/bin/python /path/to/script/switches2.py
#
# TODO: send printed output to a log file
#

import time
import subprocess
import random
import glob
import os
import fnmatch
import signal
import psutil
import numpy as np
import RPi.GPIO as io
io.setmode(io.BCM)

# Directory holding all the song files
song_directory = '/home/pi/music'
song_directory = '/home/pi/mp3'

# The pause between event detection attempts
time_delay_in_seconds = 0.2

# Number of PIR triggers before music is played
pir_play_trigger_limit = 0  # The PIR is not used
# pir_play_trigger_limit = 10

# Passive infrared (PIR) motion sensor pin on the breadboard
pir_pin = 18

# Door pin on the breadboard
door_pin = 23

# Activate input of the PIR
io.setup(pir_pin, io.IN)

# Activate input of the door
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)

######################################################
# Process monitoring and management
# Process monitoring - check if a process is running
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                print proc.name().lower()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# Process monitoring - find a named process in the list of processes
def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
 
    listOfProcessObjects = []
 
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess):
           pass
 
    return listOfProcessObjects

# Kill a process tree
def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            p.send_signal(sig)
        gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    except psutil.NoSuchProcess:
        print 'No such process'
        gone = None
        alive = None
    return (gone, alive)

# Kill processes
def kill_processes(listOfProcessObjects):
    kill_list = list()
    if len(listOfProcessObjects) == 0:
        pass
    else:
        for d in listOfProcessObjects:
            killed = kill_proc_tree(d['pid'])
            kill_list.append(killed)
    return kill_list

###################################################
# Song list management
# Recursively find all the filepaths for the songs
def get_filepaths(song_directory, file_extension):
    matches = []
    for root, dirnames, filenames in os.walk(song_directory):
        filtered_filenames = []
        for f in filenames:
            if f[0] is not '.':
                filtered_filenames.append(f)
        for filename in fnmatch.filter(filtered_filenames, '*.' + file_extension):
            matches.append(os.path.join(root, filename))
    return matches

# Find all the music file paths in the music directory
def get_music_list(song_directory, file_extensions=['mp3', 'm4a']):
    music = []
    for file_extension in file_extensions:
        files = get_filepaths(song_directory, file_extension)
        music = music + files
    return music

# Randomize the list of songs
def randomize_music_list(s):
    r = list(np.random.permutation(len(s)))
    return [s[x] for x in r]

# Print the song
def show_song(title):
    print 'Will play this song: ' + title
    return None

# Play the song
def play_song(title):
    cmd = 'omxplayer "' + title + '"'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return p

def play_song_and_notify(title, time_delay_in_seconds):
    show_song(title)
    p = play_song(title)
    return p


# Get a list of all the music files
music_list = get_music_list(song_directory)

# Randomize the play list
play_list = randomize_music_list(music_list)
number_of_songs = len(play_list)

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

# The first song that is played when the door is
# opened for the first time
welcome_song = '/home/pi/mp3/John_Wesley_Coleman_-_07_-_Tequila_10_Seconds.mp3'
play_welcome_song = True
"""
Basic Behaviour

When the door opens, the initial welcome song is played.
If the door is open, keep playing songs.
Any time the door is closed, the playing song is stopped.

"""
while True:
    print("Listening for events")

    # Detect if the door is open
    # True means that the door is open
    # False means that the door is closed
    door_open = io.input(door_pin)
    print door_open
    # If the door is closed then kill all the song processes
    if door_open == 0:
        # Find the song processes and kill them
        print 'Door closed'
        song_processes = findProcessIdByName('omxplayer.bin')
        kill_processes(song_processes)
        play_welcome_song = True
    if door_open == 1:
        print 'Door open'
        # Check if a song is playing
        player_running = checkIfProcessRunning('omxplayer.bin')
        if player_running:
            print('Player running')
            pass
        else:
            print('Player not running')
            # No player running?  Play a song!
            # Play the welcome song the first time the door is open
            if play_welcome_song:
                playing_song = play_song_and_notify(welcome_song, time_delay_in_seconds)
                play_welcome_song = False
            else:
                # If we have reached the end of the current randomized
                # play list, randomize the list again and start again
                if play_count > number_of_songs:
                    play_list = randomize_music_list(music_list)
                    play_count = 1

                # Get the next music
                play_this = play_list[play_count-1]

                # Advance the play counter
                play_count = play_count + 1

                # Play it
                playing_song = play_song_and_notify(play_this, time_delay_in_seconds)
