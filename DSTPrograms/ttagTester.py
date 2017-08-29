# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 15:06:54 2017

@author: Giulio Foletto
"""

import sys

sys.path.append('..')
sys.path.append('../..')
import json
import time
from timeit import default_timer as timer
import numpy as np

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

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
print("Initializing SPAD")
ttagBuf = ttag.TTBuffer(spadBufNum) 


cont=0 
totaltimeKwiat=0
totaltimeKwiatSingles=0
totaltimeLuxor=0
totaltimeLuxorSorting=0
print("Starting Measurements")
for cont in range(repetitions):
    time.sleep(spadExpTime)
    if spadChannelA == spadChannelB:
        start=timer()
        coinc= ttagBuf.fastcoincidences(spadExpTime,coincWindow,-delayarray, False)
        end =timer()
        totaltimeLuxor += end-start
        print(cont," LUXOR: Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA])
        
        start=timer()
        coinc= ttagBuf.fastcoincidences(spadExpTime,coincWindow,-delayarray, True)
        end =timer()
        totaltimeLuxorSorting += end-start
        print(cont," LUXOR (sort): Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA])
        start=timer()
        singles = ttagBuf.singles(spadExpTime)
        end=timer()
        totaltimeKwiatSingles += end-start
        print(cont," Kwiat singles: Time = ", end-start,
              "s Ch ", spadChannelA, " = ", singles[spadChannelA])
        
        start=timer()
        coinc= ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
        end =timer()
        totaltimeKwiat += end-start
        print(cont," Kwiat coinc: Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA])
        
        
        
        print("\n\n")
    else:
        start=timer()
        coinc= ttagBuf.fastcoincidences(spadExpTime,coincWindow,-delayarray, False)
        end =timer()
        totaltimeLuxor += end-start
        print(cont," LUXOR: Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA], 
               " Ch ", spadChannelB, " = ", coinc[spadChannelB, spadChannelB], 
               " Coinc = ", coinc[spadChannelA, spadChannelB])
        start=timer()
        coinc= ttagBuf.fastcoincidences(spadExpTime,coincWindow,-delayarray, True)
        end =timer()
        totaltimeLuxorSorting += end-start
        print(cont," LUXOR (sort): Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA], 
               " Ch ", spadChannelB, " = ", coinc[spadChannelB, spadChannelB], 
               " Coinc = ", coinc[spadChannelA, spadChannelB])
        start=timer()
        coinc= ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
        end =timer()
        totaltimeKwiat += end-start
        print(cont," Kwiat coinc: Time = ", end-start, 
              "s Ch ", spadChannelA, " = ", coinc[spadChannelA, spadChannelA], 
               " Ch ", spadChannelB, " = ", coinc[spadChannelB, spadChannelB], 
               " Coinc = ", coinc[spadChannelA, spadChannelB])
        
        print("\n\n")


if spadChannelA == spadChannelB:
    print("Average time:\tKwiatSingles = ",totaltimeKwiatSingles/repetitions, "s\tKwiat = ", totaltimeKwiat/repetitions,"s\tLUXOR = ", totaltimeLuxor/repetitions,"s\tLUXOR (sorting) = ", totaltimeLuxorSorting/repetitions)
else:
    print("Average time:\tKwiat = ", totaltimeKwiat/repetitions,"s\tLUXOR = ", totaltimeLuxor/repetitions,"s\tLUXOR (sorting) = ", totaltimeLuxorSorting/repetitions)
