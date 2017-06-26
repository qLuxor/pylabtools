# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:21:17 2017

@author: Giulio Foletto
"""

import sys
import json
import time
import numpy as np

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('..')
from pyThorPM100.pm100 import pm100d

if len(sys.argv) >1:
    filename = str(sys.argv[1])
else:
    filename ='readsettings.json'
if filename[-5:]!=".json":
    filename +=".json"

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()
    
sensor = settings["sensor"]
repetitions =1
if "repetitions" in settings:
    repetitions = settings["repetitions"]

if len(sys.argv) >2:
    outputfilename = str(sys.argv[2])
elif "outputFileName" in settings:
    outputfilename=settings["outputFileName"]
else:
    outputfilename = "dump"
if outputfilename[-4:]==".txt":
    outputfilename =outputfilename[:-4]

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

results = np.zeros(repetitions)
cont=0 
print("Starting Measurements")
for cont in range(repetitions):
    if sensor == "spad" or sensor == "SPAD":
        time.sleep(spadExpTime)
        if spadChannelA == spadChannelB:
            singles = ttagBuf.singles(spadExpTime)
            results[cont]=singles[spadChannelA]
            print(cont,"\tCounts on Channel ", spadChannelA, " = ", singles[spadChannelA])
        else:
            coinc= ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
            results[cont]=coinc[spadChannelA, spadChannelB]
            print(cont,"\tCounts on Channel ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA], 
                   "\tCounts on Channel ", spadChannelB, " = ", coinc[spadChannelB, spadChannelB], 
                   "\tCoincidences = ", coinc[spadChannelA, spadChannelB])
    elif sensor == "pwm" or sensor == "PWM":
        singleMeasure = np.zeros(pwmAverage)
        for j in range(pwmAverage):
            time.sleep(pwmWait)
            p = max(pwm.read()*1000, 0.)
            singleMeasure[j] = p
        results[cont]=np.mean(singleMeasure)
        print(cont,"\tPWM measured = ", np.mean(singleMeasure), " mW")
        
np.savez(outputfilename, results=results)