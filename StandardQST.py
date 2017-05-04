# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 22:50:52 2017

@author: Giulio Foletto 2
"""

#necessary imports
import sys
sys.path.append('..')
import time
import aptlib
import numpy as np
import instruments as ik
from qutip import *
import json

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('..')
from pyThorPM100.pm100 import pm100d

#functions that set apparatus to specific settings
def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)
        
if len(sys.argv) >1:
    filename = str(sys.argv[1])
else:
    filename ='settings.json'

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()
    
if len(sys.argv) >2:
    outputfilename = str(sys.argv[2])
else:
    outputfilename=settings["outputFileName"]
    
outputFile=open(outputfilename, "w")

#useful values
angleErr=settings["angleErr"]
home = settings["home"]
sensor = settings["sensor"]

#pwm configuration and initialization
pwmAverage=settings["pwmAverage"]
pwmWait=settings["pwmWait"]
if sensor == "pwm" or sensor == "PWM":
    pwm = pm100d()

#SPAD configuration and initialization
print("Initializing SPAD")
spadBufNum =settings["spadBufNum"]
spadDelay=settings["spadDelay"]
spadDelay = spadDelay*1e-9
spadChannelA=settings["spadChannelA"]
spadChannelB=settings["spadChannelB"]
delayarray = np.array([spadDelay, 0.0, 0.0,0.0])
spadExpTime = settings["spadExpTime"]
spadExpTime = spadExpTime*1e-3
coincWindow = 2*1e-9
if sensor == "spad" or sensor == "SPAD":
    ttagBuf = ttag.TTBuffer(spadBufNum) 


#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= settings["rotHWPSN"]
rotHWP = aptlib.PRM1(serial_number=rotHWPSN)
if home:
    rotHWP.home() #beware of bug in rotator

#ROTQWP configuration and initialization
print("Initializing ROTQWP")
rotQWPSN= settings["rotQWPSN"]
rotQWP = aptlib.PRM1(serial_number=rotQWPSN)
if home:
    rotQWP.home()

print("Finished initialization\n\n")

#calibration values for ROTHWP
rotHWPAngle0=settings["rotHWPAngle0"]
rotHWPAngle225=settings["rotHWPAngle225"]
rotHWPAngle45=settings["rotHWPAngle45"]

#calibration values for ROTQWP
rotQWPAngle0=settings["rotQWPAngle0"]
rotQWPAngle45=settings["rotQWPAngle45"]

#functions that implements settings
def measure(rotHWPangle, rotQWPangle):
    setangle(rotHWP, rotHWPangle, angleErr)
    setangle(rotQWP, rotQWPangle, angleErr)
    if sensor == "spad" or sensor == "SPAD":
        time.sleep(spadExpTime)
        coinc= ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
        result= coinc[spadChannelA, spadChannelB]
    elif sensor == "pwm" or sensor == "PWM":
        singleMeasure = np.zeros(pwmAverage)
        for j in range(pwmAverage):
            time.sleep(pwmWait)
            p = max(pwm.read()*1000, 0.)
            singleMeasure[j] = p
        result = np.mean(singleMeasure)
    return result

#Measurement on H
print("Measuring H")
countH = measure(rotHWPAngle0, rotQWPAngle0)
print("Counts for H = ", countH)
print("Counts for H = ", countH, file = outputFile)

#measurement on V
print("Measuring V")
countV = measure(rotHWPAngle45, rotQWPAngle0)
print("Counts for V = ", countV)
print("Counts for V = ", countV, file = outputFile)

#Measurement on R
print("Measuring R")
countR = measure(rotHWPAngle225, rotQWPAngle0)
print("Counts for R = ", countR)
print("Counts for R = ", countR, file = outputFile)

#Measurement on D
print("Measuring D")
countD = measure(rotHWPAngle225, rotQWPAngle45)
print("Counts for D = ", countD)
print("Counts for D = ", countD, file = outputFile)

normconstant=countH+countV
print("Normalization constant = ", normconstant)
print("Normalization constant = ", normconstant, file = outputFile)

rhoHH=countH/normconstant
rhoVV=countV/normconstant

rerhoHV=countD/normconstant-0.5
imrhoHV=countR/normconstant-0.5

rerhoVH=rerhoHV
imrhoVH=-imrhoHV

result=Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
corresult=Qobj([[rhoVV , -rerhoHV+imrhoHV*1j],[-rerhoVH+imrhoVH*1j, rhoHH]])

print("\n\nMeasured Result")
print(result)
print("\n\nIntial state")
print(corresult)

print("\n\nMeasured Result", file = outputFile)
print(result, file = outputFile)
print("\n\nIntial state", file = outputFile)
print(corresult, file = outputFile)