# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 22:40:37 2017

@author: Giulio Foletto
"""

#necessary imports

from ThorCon import ThorCon
import instruments as ik
import json
import sys

#functions that set apparatus to specific settings
def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)

def setvoltage(lcc, voltage, voltageErr):
    if abs(float(lcc.voltage1) - voltage) > voltageErr:
        lcc.voltage1=voltage

if len(sys.argv) >1:
    filename = str(sys.argv[1])
else:
    filename ='settings.json'
if filename[-5:]!=".json":
    filename +=".json"

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()

#useful values
angleErr=settings["angleErr"]
voltageErr = settings["voltageErr"]
home = settings["home"]

print("Setting everything for tilting adjustement phase and calibration of LCR1, please send D polarzation, close off deflected ray in int2\n\n")

#LCC1 configuration and initialization
print("Initializing LCC1")
port1=settings["port1"]
lcc1 = ik.thorlabs.LCC25.open_serial(port1, 115200,timeout=1)
lcc1.mode = lcc1.Mode.voltage1
lcc1.enable = True
lcc1Voltage180=settings["lcc1Voltage180"]

#ROT1 configuration and initialization
print("Initializing ROT1")
rot1SN = settings["rot1SN"]
rot1 = ThorCon(serial_number=rot1SN)
if home:
    rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = settings["rot2SN"]
rot2 = ThorCon(serial_number=rot2SN)
if home:
    rot2.home()

#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= settings["rotHWPSN"]
rotHWP = ThorCon(serial_number=rotHWPSN)
if home:
    rotHWP.home() #beware of bug in rotator

#ROTQWP configuration and initialization
print("Initializing ROTQWP")
rotQWPSN= settings["rotQWPSN"]
rotQWP = ThorCon(serial_number=rotQWPSN)
if home:
    rotQWP.home()

rot1Angle180=settings["rot1Angle180"]
rot2Angle0=settings["rot2Angle0"]
rotHWPAngle675=settings["rotHWPAngle675"]
rotHWPAngle0=settings["rotHWPAngle0"]
rotQWPAngle45=settings["rotQWPAngle45"]

print("Finished initialization\n\n")

print("Moving rotators")
setangle(rot1, rot1Angle180, angleErr)
setangle(rot2, rot2Angle0, angleErr)
setangle(rotHWP, rotHWPAngle675, angleErr)
setangle(rotQWP, rotQWPAngle45, angleErr)

print("Setting LCC1 for faster tilting")
setvoltage(lcc1, lcc1Voltage180, voltageErr)

print("Disconnecting rotators")
rot1.close()
rot2.close()
rotHWP.close()
rotQWP.close()

print("\n\nFinished all preparation for LCR1, please proceed with tilting and calibration of LCR1. You don't have to close this script")

input("If all rotators are ready to be controlled again, press Enter to prepare the setup for calibration of LCR2, enter with D, block deflected ray in int1")
rot1 = aptlib.PRM1(serial_number=rot1SN)
rot2 = aptlib.PRM1(serial_number=rot2SN)
rotHWP = aptlib.PRM1(serial_number=rotHWPSN)
rotQWP = aptlib.PRM1(serial_number=rotQWPSN)

print("Moving rotators")
setangle(rot1, rot1Angle180, angleErr)
setangle(rotHWP, rotHWPAngle0, angleErr)
setangle(rotQWP, rotQWPAngle45, angleErr)

print("\n\nFinished all preparation for LCR2, please proceed with calibration of LCR2. This script ends here")