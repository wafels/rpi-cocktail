import time
import subprocess
import RPi.GPIO as io
io.setmode(io.BCM)

pir_pin = 18
door_pin = 23

io.setup(pir_pin, io.IN) # activate input
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP) # activate input

pircount = 0
doorcount = 0
while True:
    if io.input(pir_pin):
        pircount +=1 
        print("PIR ALARM! - Motion detected %i " % pircount)
    if not io.input(door_pin):
        doorcount +=1
        print("DOOR ALARM! - Door close detected %i " % doorcount)
        subprocess.call("omxplayer example.mp3", shell=True)
    time.sleep(0.2)

