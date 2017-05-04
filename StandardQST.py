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

#useful values
angleErr=settings["angleErr"]

#pwm configuration and initialization
pwm = pm100d()
pwmAverage=settings["pwmAverage"]
pwmWait=settings["pwmWait"]

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
ttagBuf = ttag.TTBuffer(spadBufNum) 


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
    #time.sleep(spadExpTime)
    #coinc ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
    #return coinc[spadChannelA, spadChannelB]
    singleMeasure = np.zeros(pwmAverage)
    for j in range(pwmAverage):
        time.sleep(pwmWait)
        p = max(pwm.read()*1000, 0.)
        singleMeasure[j] = p
    return np.mean(singleMeasure)

#Measurement on H
print("Measuring H")
countH = measure(rotHWPAngle0, rotQWPAngle0)

#measurement on V
print("Measuring V")
countV = measure(rotHWPAngle45, rotQWPAngle0)

#Measurement on R
print("Measuring R")
countR = measure(rotHWPAngle225, rotQWPAngle0)

#Measurement on D
print("Measuring D")
countD = measure(rotHWPAngle225, rotQWPAngle45)

normconstant=countH+countV

rhoHH=countH/normconstant
rhoVV=countV/normconstant

rerhoHV=countD/normconstant-0.5
imrhoHV=countR/normconstant-0.5

rerhoVH=rerhoHV
imrhoVH=-imrhoHV

result=Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
print("\n\nMeasured Result")
print(result)
corresult=Qobj([[rhoVV , -rerhoHV+imrhoHV*1j],[-rerhoVH+imrhoVH*1j, rhoHH]])
print("\n\nIntial state")
print(corresult)