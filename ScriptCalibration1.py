# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 22:40:37 2017

@author: Giulio Foletto
"""

#necessary imports

import aptlib
import instruments as ik
import json

#functions that set apparatus to specific settings
def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)

def setvoltage(lcc, voltage, voltageErr):
    if abs(float(lcc.voltage1) - voltage) > voltageErr:
        lcc.voltage1=voltage

with open('cal1settings.json') as json_settings:
    settings = json.load(json_settings)
    json_settings.close()

angleErr=settings["angleErr"]
voltageErr = settings["voltageErr"]
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
rot1 = aptlib.PRM1(serial_number=rot1SN)
rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = settings["rot2SN"]
rot2 = aptlib.PRM1(serial_number=rot2SN)
rot2.home()

#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= settings["rotHWPSN"]
rotHWP = aptlib.PRM1(serial_number=rotHWPSN)
#rotHWP.home() #commented out due to bug in rotator

#ROTQWP configuration and initialization
print("Initializing ROTQWP")
rotQWPSN= settings["rotQWPSN"]
rotQWP = aptlib.PRM1(serial_number=rotQWPSN)
rotQWP.home()

rot1Angle180=settings["rot1Angle180"]
rot2Angle0=settings["rot2Angle0"]
rotHWPAngle675=settings["rotHWPAngle675"]
rotQWPAngle45=settings["rotQWPAngle45"]

print("Finished initialization\n\n")

print("Moving rotators")
setangle(rot1, rot1Angle180, angleErr)
setangle(rot2, rot2Angle0, angleErr)
setangle(rotHWP, rotHWPAngle675, angleErr)
setangle(rotQWP, rotQWPAngle45, angleErr)

print("Setting LCC1 for faster tilting")
setvoltage(lcc1, lcc1Voltage180, voltageErr)

print("\n\nFinished all, please proceed with calibration of LCR2")