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
import qutip
import json

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('..')
from pyThorPM100.pm100 import pm100d

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
    
if len(sys.argv) >2:
    outputfilename = str(sys.argv[2])
else:
    outputfilename=settings["outputFileName"]
if outputfilename[-4:]==".txt":
    outputfilename =outputfilename[:-4]

outputfilename+="QST"
outputfilename+=".txt"
    
outputFile=open(outputfilename, "w")
print("Results for QST protocol", file = outputFile)

#useful values
angleErr=settings["angleErr"]
voltageErr = settings["voltageErr"]
home = settings["home"]
sensor = settings["sensor"]

#pwm configuration and initialization
pwmAverage=settings["pwmAverage"]
pwmWait=settings["pwmWait"]
if sensor == "pwm" or sensor == "PWM":
    print("Initializing PWM")
    pwm = pm100d()

#SPAD configuration and initialization
spadBufNum =settings["spadBufNum"]
spadDelayA=settings["spadDelayA"]
spadDelayB=settings["spadDelayB"]
spadDelayA = spadDelayA*1e-9
spadDelayB = spadDelayB*1e-9
spadChannelA=settings["spadChannelA"]
spadChannelB=settings["spadChannelB"]
delayarray = np.array([0.0, 0.0, 0.0,0.0])
delayarray[spadChannelA]=spadDelayA
delayarray[spadChannelB]=spadDelayB
spadExpTime = settings["spadExpTime"]
spadExpTime = spadExpTime*1e-3
coincWindow = 1*1e-9
if sensor == "spad" or sensor == "SPAD":
    print("Initializing SPAD")
    ttagBuf = ttag.TTBuffer(spadBufNum) 

#LCC1 configuration and initialization
print("Initializing LCC1")
port1=settings["port1"]
lcc1 = ik.thorlabs.LCC25.open_serial(port1, 115200,timeout=1)
lcc1.mode = lcc1.Mode.voltage1
lcc1.enable = True

#LLC2 configuration and initialization
print("Initializing LCC2")
port2=settings["port2"]
lcc2 = ik.thorlabs.LCC25.open_serial(port2, 115200,timeout=1)
lcc2.mode = lcc2.Mode.voltage1
lcc2.enable = True

#ROT1 configuration and initialization
print("Initializing ROT1")
rot1SN = settings["rot1SN"]
rot1 = aptlib.PRM1(serial_number=rot1SN)
if home:
    rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = settings["rot2SN"]
rot2 = aptlib.PRM1(serial_number=rot2SN)
if home:
    rot2.home()

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

#calibration values for ROT1
rot1Angle0=settings["rot1Angle0"]

#calibration values for LCC1
lcc1Voltage0=settings["lcc1Voltage0"]

#calibration values for ROT2
rot2Angle0=settings["rot2Angle0"]

#calibration values for LCC2
lcc2Voltage0=settings["lcc2Voltage0"]

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
        result= float(coinc[spadChannelA, spadChannelB])
    elif sensor == "pwm" or sensor == "PWM":
        singleMeasure = np.zeros(pwmAverage)
        for j in range(pwmAverage):
            time.sleep(pwmWait)
            p = max(pwm.read()*1000, 0.)
            singleMeasure[j] = p
        result = np.mean(singleMeasure)
    return result

#set interferometers
print("Setting the interferometers")
setangle(rot1, rot1Angle0, angleErr)
setvoltage(lcc1, lcc1Voltage0, voltageErr)
setangle(rot2, rot2Angle0, angleErr)
setvoltage(lcc2, lcc2Voltage0, voltageErr)
print("Finished setting the interferometers")

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

rawresult=qutip.Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
result=qutip.Qobj([[rhoVV , -rerhoHV+imrhoHV*1j],[-rerhoVH+imrhoVH*1j, rhoHH]])
resquad=result**2
purity= resquad.tr()

#save qobjs
qutip.qsave([result, resquad, rawresult], outputfilename[:-4])

print("\n\nMeasured Result")
print(rawresult)
print("\n\nIntial state")
print(result)

print("\nRaw result = ", rawresult, file = outputFile)
print("\nCorrected result = ", result, file = outputFile)
print("\nresquad = ", resquad, file = outputFile)
print("\npurity = ", purity, file = outputFile)