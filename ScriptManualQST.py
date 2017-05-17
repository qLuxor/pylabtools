# -*- coding: utf-8 -*-
"""
Created on Wed May 10 22:22:38 2017

@author: Giulio Foletto
"""

#necessary imports
import sys
sys.path.append('..')
import time
import aptlib
import numpy as np
import qutip
import json

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('..')
from pyThorPM100.pm100 import pm100d

def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)

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

outputfilename+="ManualQST"
outputfilename+=".txt"
    
outputFile=open(outputfilename, "w")
print("Results for Manual QST protocol", file = outputFile)

#useful values
angleErr=settings["angleErr"]
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
    
#calibration values for ROTHWP
rotHWPAngle675=settings["rotHWPAngle675"]

#calibration values for ROTQWP
rotQWPAngle45=settings["rotQWPAngle45"]

#calibration values for Manual HWP
manualHWPAngle0=settings["manualHWPAngle0"]
manualHWPAngle225=settings["manualHWPAngle225"]
manualHWPAngle45=settings["manualHWPAngle45"]

#calibration values for Manual QWP
manualQWPAngle0=settings["manualQWPAngle0"]
manualQWPAngle45=settings["manualQWPAngle45"]

#functions that implements settings
def measure():
    if sensor == "spad" or sensor == "SPAD":
        time.sleep(spadExpTime)
        if spadChannelA == spadChannelB:
            singles = ttagBuf.singles(spadExpTime)
            result=float(singles[spadChannelA])
        else:
            coincidences = ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
            result= float(coincidences[spadChannelA, spadChannelB])
    elif sensor == "pwm" or sensor == "PWM":
        singleMeasure = np.zeros(pwmAverage)
        for j in range(pwmAverage):
            time.sleep(pwmWait)
            p = max(pwm.read()*1000, 0.)
            singleMeasure[j] = p
        result = np.mean(singleMeasure)
    return result

#setting plates
print("Setting plates")
setangle(rotHWP, rotHWPAngle675, angleErr)
setangle(rotQWP, rotQWPAngle45, angleErr)
print("Finished setting plates")

input("Please block V and A paths, then press enter")

#Measurement on H
print("Measuring H")
instruction = "Please set HWP to ", "{:5.1}".format(manualHWPAngle0), "\tandQWP to ", "{:5.1}".format(manualQWPAngle0), "\tthen press enter"
input(instruction)
countH = measure()
print("Counts for H = ", countH)
print("Counts for H = ", countH, file = outputFile)

#measurement on V
print("Measuring V")
instruction =("Please set HWP to ", "{:5.1}".format(manualHWPAngle45), "\tandQWP to ", "{:5.1}".format(manualQWPAngle0), "\tthen press enter")
input(instruction)
countV = measure()
print("Counts for V = ", countV)
print("Counts for V = ", countV, file = outputFile)

#Measurement on R
print("Measuring R")
instruction=("Please set HWP to ", "{:5.1}".format(manualHWPAngle225), "\tandQWP to ", "{:5.1}".format(manualQWPAngle0), "\tthen press enter")
input(instruction)
countR = measure()
print("Counts for R = ", countR)
print("Counts for R = ", countR, file = outputFile)

#Measurement on D
print("Measuring D")
instruction=("Please set HWP to ", "{:5.1}".format(manualHWPAngle225), "\tandQWP to ", "{:5.1}".format(manualQWPAngle45), "\tthen press enter")
input(instruction)
countD = measure()
print("Counts for D = ", countD)
print("Counts for D = ", countD, file = outputFile)

normconstant=countH+countV
print("Normalization constant = ", normconstant)
print("Normalization constant = ", normconstant, file = outputFile)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

rhoHH=countH/normconstant
rhoVV=countV/normconstant

rerhoHV=countD/normconstant-0.5
imrhoHV=countR/normconstant-0.5

rerhoVH=rerhoHV
imrhoVH=-imrhoHV

result=qutip.Qobj([[rhoVV , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoHH]])
resquad=result**2
purity= resquad.tr()

#save qobjs
qutip.qsave([result, resquad], outputfilename[:-4])

#output of final results
print("Final result")
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

print("\nCorrected result = ", result, file = outputFile)
print("\nresquad = ", resquad, file = outputFile)
print("\npurity = ", purity, file = outputFile)