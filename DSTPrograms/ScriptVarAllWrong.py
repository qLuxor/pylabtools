# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 20:49:26 2017

@author: Giulio Foletto
"""

#necessary imports
import sys
sys.path.append('..')
sys.path.append('../..')
import time
import datetime
from ThorCon import ThorCon
import numpy as np
import instruments as ik
import qutip
import json

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

from pyThorPM100.pm100 import pm100d

def alarm():
    f=open("/dev/console", "w")
    for i in range(0, 10):
        print('\a', file=f)
        time.sleep(0.1)
    f.close()

#functions that set apparatus to specific settings
def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)

def setvoltage(lcc, voltage, voltageErr):
    if abs(float(lcc.voltage1) - voltage) > voltageErr:
        lcc.voltage1=voltage

starttime=datetime.datetime.now()

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

outputfilename+="VarAll"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for VarAll protocols", file = outputFile)

#useful values
allowTime=settings["allowTime"]
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
lcc2.enable = False #due to malfunctioning, change if necessary

#rotQWP1 configuration and initialization
print("Initializing rotQWP1")
rotQWP1SN= settings["rotQWP1SN"]
rotQWP1 = ThorCon(serial_number=rotQWP1SN)
if home:
    rotQWP1.home() 

#rotHWP1 configuration and initialization
print("Initializing rotHWP1")
rotHWP1SN = settings["rotHWP1SN"]
rotHWP1 = ThorCon(serial_number=rotHWP1SN)
if home:
    rotHWP1.home()
    
#rotQWP2 configuration and initialization
print("Initializing rotQWP2")
rotQWP2SN= settings["rotQWP2SN"]
rotQWP2 = ThorCon(serial_number=rotQWP2SN)
if home or not home:
    rotQWP2.home()

#rotHWP2 configuration and initialization
print("Initializing rotHWP2")
rotHWP2SN = settings["rotHWP2SN"]
rotHWP2 = ThorCon(serial_number=rotHWP2SN)
if home:
    rotHWP2.home()

#rotHWPFin configuration and initialization
print("Initializing rotHWPFin")
rotHWPFinSN = settings["rotHWPFinSN"]
rotHWPFin = ThorCon(serial_number=rotHWPFinSN)
if home or not home:
    rotHWPFin.home()
    
print("Finished initialization\n\n")
#calibration values for LCC1
lcc1Voltage180=settings["lcc1Voltage180"]

#calibration values for LCC2
lcc2Voltage0=settings["lcc2Voltage0"]
lcc2Voltage90=settings["lcc2Voltage90"]

#calibration values for rotLCC
rotLCR1Angle0=settings["rotLCR1Angle0"]
rotLCR2Angle0=settings["rotLCR2Angle0"]
rotLCR2Angle315=settings["rotLCR2Angle315"]

#calibration values for rotQWP1
rotQWP1Angle0=settings["rotQWP1Angle0"]
rotQWP1Angle45=settings["rotQWP1Angle45"]
rotQWP1Angle90=settings["rotQWP1Angle90"]
rotQWP1Angle315=settings["rotQWP1Angle315"]

rotQWP1AngleQST0=settings["rotQWP1AngleQST0"]
rotQWP1AngleQST45=settings["rotQWP1AngleQST45"]
rotQWP1AngleQST315=settings["rotQWP1AngleQST315"]
rotQWP1AngleQST90=settings["rotQWP1AngleQST90"]

#calibration values for rotHWP1
rotHWP1Angle0=settings["rotHWP1Angle0"]
rotHWP1Angle45=settings["rotHWP1Angle45"]
rotHWP1Angle225=settings["rotHWP1Angle225"]
rotHWP1Angle675=settings["rotHWP1Angle675"]

rotHWP1AngleQST0=settings["rotHWP1AngleQST0"]
rotHWP1AngleQST45=settings["rotHWP1AngleQST45"]
rotHWP1AngleQST225=settings["rotHWP1AngleQST225"]
rotHWP1AngleQST675=settings["rotHWP1AngleQST675"]

#calibration values for rotQWP2
rotQWP2Angle0=settings["rotQWP2Angle0"]
rotQWP2Angle45=settings["rotQWP2Angle45"]
rotQWP2Angle90=settings["rotQWP2Angle90"]
rotQWP2Angle315=settings["rotQWP2Angle315"]

#calibration values for rotHWP2
rotHWP2Angle0=settings["rotHWP2Angle0"]
rotHWP2Angle315=settings["rotHWP2Angle315"]
rotHWP2Angle225=settings["rotHWP2Angle225"]
rotHWP2Angle675=settings["rotHWP2Angle675"]

#calibration values for rotHWPFin
rotHWPFinAngle0=settings["rotHWPFinAngle0"]
rotHWPFinAngle45=settings["rotHWPFinAngle45"]
rotHWPFinAngle225=settings["rotHWPFinAngle225"]
rotHWPFinAngle675=settings["rotHWPFinAngle675"]

#calibration values for rotHWPFin
rotHWPInizAngle0=settings["rotHWPInizAngle0"]
rotHWPInizAngle45=settings["rotHWPInizAngle45"]

#calibration values for strPlates
strHWP1Angle0=settings["strHWP1Angle0"]
strHWP2Angle0=settings["strHWP2Angle0"]
strQWP1Angle0=settings["strQWP1Angle0"]
strQWP2Angle0=settings["strQWP2Angle0"]

strengthA=settings["strengthA"]
strengthB=settings["strengthB"]
strSignA=np.sign(strengthA)

#functions that implements settings
def measure(rotQWP1angle, rotHWP1angle, rotQWP2angle,rotHWP2angle, rotHWPFinangle, lcc1voltage, lcc2voltage):
    setangle(rotQWP1, rotQWP1angle, angleErr)
    setangle(rotHWP1, rotHWP1angle, angleErr)
    setangle(rotQWP2, rotQWP2angle, angleErr)
    setangle(rotHWP2, rotHWP2angle, angleErr)
    setangle(rotHWPFin, rotHWPFinangle, angleErr)
    setvoltage(lcc1, lcc1voltage, voltageErr)
    setvoltage(lcc2, lcc2voltage, voltageErr)
    time.sleep(allowTime)
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

resultdata={}
resultdata.update({"strengthA": strengthA, "strengthB": strengthB})
alarm()
instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0+strengthA/2) +"\tInt2 " +str(strHWP2Angle0+strengthB/2)  +" then press Enter"
input(instruction)
instruction = "Please rotate LCR1 to " + str(rotLCR1Angle0) + " and LCR2 to " + str(rotLCR2Angle315) + ", then press Enter"
input(instruction)
instruction = "Please rotate the initial HWP to "+str(rotHWPInizAngle0) + ", then press Enter"
input(instruction)
input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring VVHH")
VVHH = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVHH = ", VVHH)
print("Counts for VVHH = ", VVHH, file = outputFile)
resultdata.update({"VVHH": VVHH})

print("Measuring VVHV")
VVHV = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVHV = ", VVHV)
print("Counts for VVHV = ", VVHV, file = outputFile)
resultdata.update({"VVHV": VVHV})

alarm()
input("Please block Non1 path, unblock all others, then press Enter")

print("Measuring VDHV")
VDHV = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VDHV = ", VDHV)
print("Counts for VDHV = ", VDHV, file = outputFile)
resultdata.update({"VDHV": VDHV})

print("Measuring VDHH")
VDHH = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VDHH = ", VDHH)
print("Counts for VDHH = ", VDHH, file = outputFile)
resultdata.update({"VDHH": VDHH})

print("Measuring VAHH")
VAHH = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VAHH = ", VAHH)
print("Counts for VAHH = ", VAHH, file = outputFile)
resultdata.update({"VAHH": VAHH})

print("Measuring VAHV")
VAHV = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VAHV = ", VAHV)
print("Counts for VAHV = ", VAHV, file = outputFile)
resultdata.update({"VAHV": VAHV})

alarm()
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring DVHV")
DVHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVHV = ", DVHV)
print("Counts for DVHV = ", DVHV, file = outputFile)
resultdata.update({"DVHV": DVHV})

print("Measuring DVHH")
DVHH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVHH = ", DVHH)
print("Counts for DVHH = ", DVHH, file = outputFile)
resultdata.update({"DVHH": DVHH})

print("Measuring AVHH")
AVHH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVHH = ", AVHH)
print("Counts for AVHH = ", AVHH, file = outputFile)
resultdata.update({"AVHH": AVHH})

print("Measuring AVHV")
AVHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVHV = ", AVHV)
print("Counts for AVHV = ", AVHV, file = outputFile)
resultdata.update({"AVHV": AVHV})

print("Measuring LVHV")
LVHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVHV = ", LVHV)
print("Counts for LVHV = ", LVHV, file = outputFile)
resultdata.update({"LVHV": LVHV})

print("Measuring LVHH")
LVHH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVHH = ", LVHH)
print("Counts for LVHH = ", LVHH, file = outputFile)
resultdata.update({"LVHH": LVHH})

print("Measuring RVHH")
RVHH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVHH = ", RVHH)
print("Counts for RVHH = ", RVHH, file = outputFile)
resultdata.update({"RVHH": RVHH})

print("Measuring RVHV")
RVHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVHV = ", RVHV)
print("Counts for RVHV = ", RVHV, file = outputFile)
resultdata.update({"RVHV": RVHV})

alarm()
input("Please unblock all paths, then press Enter")

print("Measuring RLHV")
RLHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLHV = ", RLHV)
print("Counts for RLHV = ", RLHV, file = outputFile)
resultdata.update({"RLHV": RLHV})

print("Measuring RLHH")
RLHH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLHH = ", RLHH)
print("Counts for RLHH = ", RLHH, file = outputFile)
resultdata.update({"RLHH": RLHH})

print("Measuring RRHH")
RRHH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRHH = ", RRHH)
print("Counts for RRHH = ", RRHH, file = outputFile)
resultdata.update({"RRHH": RRHH})

print("Measuring RRHV")
RRHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRHV = ", RRHV)
print("Counts for RRHV = ", RRHV, file = outputFile)
resultdata.update({"RRHV": RRHV})

print("Measuring LRHV")
LRHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRHV = ", LRHV)
print("Counts for LRHV = ", LRHV, file = outputFile)
resultdata.update({"LRHV": LRHV})

print("Measuring LRHH")
LRHH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRHH = ", LRHH)
print("Counts for LRHH = ", LRHH, file = outputFile)
resultdata.update({"LRHH": LRHH})

print("Measuring LLHH")
LLHH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LLHH = ", LLHH)
print("Counts for LLHH = ", LLHH, file = outputFile)
resultdata.update({"LLHH": LLHH})

print("Measuring LLHV")
LLHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LLHV = ", LLHV)
print("Counts for LLHV = ", LLHV, file = outputFile)
resultdata.update({"LLHV": LLHV})

print("Measuring DLHV")
DLHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DLHV = ", DLHV)
print("Counts for DLHV = ", DLHV, file = outputFile)
resultdata.update({"DLHV": DLHV})

print("Measuring DLHH")
DLHH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DLHH = ", DLHH)
print("Counts for DLHH = ", DLHH, file = outputFile)
resultdata.update({"DLHH": DLHH})

print("Measuring DRHH")
DRHH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRHH = ", DRHH)
print("Counts for DRHH = ", DRHH, file = outputFile)
resultdata.update({"DRHH": DRHH})

print("Measuring DRHV")
DRHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRHV = ", DRHV)
print("Counts for DRHV = ", DRHV, file = outputFile)
resultdata.update({"DRHV": DRHV})

print("Measuring DDHV")
DDHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DDHV = ", DDHV)
print("Counts for DDHV = ", DDHV, file = outputFile)
resultdata.update({"DDHV": DDHV})

print("Measuring DDHH")
DDHH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DDHH = ", DDHH)
print("Counts for DDHH = ", DDHH, file = outputFile)
resultdata.update({"DDHH": DDHH})

print("Measuring DAHH")
DAHH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DAHH = ", DAHH)
print("Counts for DAHH = ", DAHH, file = outputFile)
resultdata.update({"DAHH": DAHH})

print("Measuring DAHV")
DAHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DAHV = ", DAHV)
print("Counts for DAHV = ", DAHV, file = outputFile)
resultdata.update({"DAHV": DAHV})

print("Measuring LAHV")
LAHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LAHV = ", LAHV)
print("Counts for LAHV = ", LAHV, file = outputFile)
resultdata.update({"LAHV": LAHV})

print("Measuring LAHH")
LAHH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LAHH = ", LAHH)
print("Counts for LAHH = ", LAHH, file = outputFile)
resultdata.update({"LAHH": LAHH})

print("Measuring RAHH")
RAHH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RAHH = ", RAHH)
print("Counts for RAHH = ", RAHH, file = outputFile)
resultdata.update({"RAHH": RAHH})

print("Measuring RAHV")
RAHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RAHV = ", RAHV)
print("Counts for RAHV = ", RAHV, file = outputFile)
resultdata.update({"RAHV": RAHV})

print("Measuring AAHV")
AAHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for AAHV = ", AAHV)
print("Counts for AAHV = ", AAHV, file = outputFile)
resultdata.update({"AAHV": AAHV})

print("Measuring AAHH")
AAHH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AAHH = ", AAHH)
print("Counts for AAHH = ", AAHH, file = outputFile)
resultdata.update({"AAHH": AAHH})

print("Measuring ALHH")
ALHH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALHH = ", ALHH)
print("Counts for ALHH = ", ALHH, file = outputFile)
resultdata.update({"ALHH": ALHH})

print("Measuring ALHV")
ALHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALHV = ", ALHV)
print("Counts for ALHV = ", ALHV, file = outputFile)
resultdata.update({"ALHV": ALHV})

print("Measuring ARHV")
ARHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARHV = ", ARHV)
print("Counts for ARHV = ", ARHV, file = outputFile)
resultdata.update({"ARHV": ARHV})

print("Measuring ARHH")
ARHH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARHH = ", ARHH)
print("Counts for ARHH = ", ARHH, file = outputFile)
resultdata.update({"ARHH": ARHH})

print("Measuring ADHH")
ADHH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ADHH = ", ADHH)
print("Counts for ADHH = ", ADHH, file = outputFile)
resultdata.update({"ADHH": ADHH})

print("Measuring ADHV")
ADHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ADHV = ", ADHV)
print("Counts for ADHV = ", ADHV, file = outputFile)
resultdata.update({"ADHV": ADHV})

print("Measuring RDHV")
RDHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RDHV = ", RDHV)
print("Counts for RDHV = ", RDHV, file = outputFile)
resultdata.update({"RDHV": RDHV})

print("Measuring RDHH")
RDHH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RDHH = ", RDHH)
print("Counts for RDHH = ", RDHH, file = outputFile)
resultdata.update({"RDHH": RDHH})

print("Measuring LDHH")
LDHH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LDHH = ", LDHH)
print("Counts for LDHH = ", LDHH, file = outputFile)
resultdata.update({"LDHH": LDHH})

print("Measuring LDHV")
LDHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LDHV = ", LDHV)
print("Counts for LDHV = ", LDHV, file = outputFile)
resultdata.update({"LDHV": LDHV})

alarm()
instruction = "Please rotate the initial HWP to "+str(rotHWPInizAngle45) + ", then press Enter"
input(instruction)
input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring VVVHT")
VVVHT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVVHT = ", VVVHT)
print("Counts for VVVHT = ", VVVHT, file = outputFile)
resultdata.update({"VVVHT": VVVHT})

VVVV = VVVHT

print("Measuring VVVVT")
VVVVT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVVVT = ", VVVVT)
print("Counts for VVVVT = ", VVVVT, file = outputFile)
resultdata.update({"VVVVT": VVVVT})

alarm()
input("Please block Non1 path, unblock all others, then press Enter")

print("Measuring VAVVT")
VAVVT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VAVVT = ", VAVVT)
print("Counts for VAVVT = ", VAVVT, file = outputFile)
resultdata.update({"VAVVT": VAVVT})

print("Measuring VAVHT")
VAVHT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VAVHT = ", VAVHT)
print("Counts for VAVHT = ", VAVHT, file = outputFile)
resultdata.update({"VAVHT": VAVHT})

print("Measuring VDVHT")
VDVHT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VDVHT = ", VDVHT)
print("Counts for VDVHT = ", VDVHT, file = outputFile)
resultdata.update({"VDVHT": VDVHT})

print("Measuring VDVVT")
VDVVT = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for VDVVT = ", VDVVT)
print("Counts for VDVVT = ", VDVVT, file = outputFile)
resultdata.update({"VDVVT": VDVVT})

alarm()
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring DVVVT")
DVVVT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVVVT = ", DVVVT)
print("Counts for DVVVT = ", DVVVT, file = outputFile)
resultdata.update({"DVVVT": DVVVT})

print("Measuring DVVHT")
DVVHT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVVHT = ", DVVHT)
print("Counts for DVVHT = ", DVVHT, file = outputFile)
resultdata.update({"DVVHT": DVVHT})

print("Measuring LVVHT")
LVVHT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVVHT = ", LVVHT)
print("Counts for LVVHT = ", LVVHT, file = outputFile)
resultdata.update({"LVVHT": LVVHT})

print("Measuring LVVVT")
LVVVT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVVVT = ", LVVVT)
print("Counts for LVVVT = ", LVVVT, file = outputFile)
resultdata.update({"LVVVT": LVVVT})

print("Measuring RVVVT")
RVVVT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVVVT = ", RVVVT)
print("Counts for RVVVT = ", RVVVT, file = outputFile)
resultdata.update({"RVVVT": RVVVT})

print("Measuring RVVHT")
RVVHT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVVHT = ", RVVHT)
print("Counts for RVVHT = ", RVVHT, file = outputFile)
resultdata.update({"RVVHT": RVVHT})

print("Measuring AVVHT")
AVVHT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVVHT = ", AVVHT)
print("Counts for AVVHT = ", AVVHT, file = outputFile)
resultdata.update({"AVVHT": AVVHT})

print("Measuring AVVVT")
AVVVT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVVVT = ", AVVVT)
print("Counts for AVVVT = ", AVVVT, file = outputFile)
resultdata.update({"AVVVT": AVVVT})

alarm()
input("Please unblock all paths, then press Enter")

print("Measuring ALVVT")
ALVVT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALVVT = ", ALVVT)
print("Counts for ALVVT = ", ALVVT, file = outputFile)
resultdata.update({"ALVVT": ALVVT})

ALVH=ALVVT

print("Measuring ALVHT")
ALVHT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALVHT = ", ALVHT)
print("Counts for ALVHT = ", ALVHT, file = outputFile)
resultdata.update({"ALVHT": ALVHT})

print("Measuring ARVHT")
ARVHT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARVHT = ", ARVHT)
print("Counts for ARVHT = ", ARVHT, file = outputFile)
resultdata.update({"ARVHT": ARVHT})

print("Measuring ARVVT")
ARVVT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARVVT = ", ARVVT)
print("Counts for ARVVT = ", ARVVT, file = outputFile)
resultdata.update({"ARVVT": ARVVT})

ARVH=ARVVT

print("Measuring RRVVT")
RRVVT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRVVT = ", RRVVT)
print("Counts for RRVVT = ", RRVVT, file = outputFile)
resultdata.update({"RRVVT": RRVVT})

RRVH=RRVVT

print("Measuring RRVHT")
RRVHT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRVHT = ", RRVHT)
print("Counts for RRVHT = ", RRVHT, file = outputFile)
resultdata.update({"RRVHT": RRVHT})

print("Measuring RDVHT")
RDVHT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RDVHT = ", RDVHT)
print("Counts for RDVHT = ", RDVHT, file = outputFile)
resultdata.update({"RDVHT": RDVHT})

print("Measuring RDVVT")
RDVVT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RDVVT = ", RDVVT)
print("Counts for RDVVT = ", RDVVT, file = outputFile)
resultdata.update({"RDVVT": RDVVT})

print("Measuring LDVVT")
LDVVT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LDVVT = ", LDVVT)
print("Counts for LDVVT = ", LDVVT, file = outputFile)
resultdata.update({"LDVVT": LDVVT})

print("Measuring LDVHT")
LDVHT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LDVHT = ", LDVHT)
print("Counts for LDVHT = ", LDVHT, file = outputFile)
resultdata.update({"LDVHT": LDVHT})

print("Measuring LRVHT")
LRVHT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRVHT = ", LRVHT)
print("Counts for LRVHT = ", LRVHT, file = outputFile)
resultdata.update({"LRVHT": LRVHT})

print("Measuring LRVVT")
LRVVT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRVVT = ", LRVVT)
print("Counts for LRVVT = ", LRVVT, file = outputFile)
resultdata.update({"LRVVT": LRVVT})

LRVH=LRVVT

print("Measuring LLVVT")
LLVVT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LLVVT = ", LLVVT)
print("Counts for LLVVT = ", LLVVT, file = outputFile)
resultdata.update({"LLVVT": LLVVT})

LLVH=LLVVT

print("Measuring LLVHT")
LLVHT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LLVHT = ", LLVHT)
print("Counts for LLVHT = ", LLVHT, file = outputFile)
resultdata.update({"LLVHT": LLVHT})

print("Measuring RLVHT")
RLVHT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLVHT = ", RLVHT)
print("Counts for RLVHT = ", RLVHT, file = outputFile)
resultdata.update({"RLVHT": RLVHT})

print("Measuring RLVVT")
RLVVT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLVVT = ", RLVVT)
print("Counts for RLVVT = ", RLVVT, file = outputFile)
resultdata.update({"RLVVT": RLVVT})

RLVH=RLVVT

print("Measuring RAVVT")
RAVVT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RAVVT = ", RAVVT)
print("Counts for RAVVT = ", RAVVT, file = outputFile)
resultdata.update({"RAVVT": RAVVT})

print("Measuring RAVHT")
RAVHT = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RAVHT = ", RAVHT)
print("Counts for RAVHT = ", RAVHT, file = outputFile)
resultdata.update({"RAVHT": RAVHT})

print("Measuring LAVHT")
LAVHT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LAVHT = ", LAVHT)
print("Counts for LAVHT = ", LAVHT, file = outputFile)
resultdata.update({"LAVHT": LAVHT})

print("Measuring LAVVT")
LAVVT = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LAVVT = ", LAVVT)
print("Counts for LAVVT = ", LAVVT, file = outputFile)
resultdata.update({"LAVVT": LAVVT})

print("Measuring DAVVT")
DAVVT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DAVVT = ", DAVVT)
print("Counts for DAVVT = ", DAVVT, file = outputFile)
resultdata.update({"DAVVT": DAVVT})

print("Measuring DAVHT")
DAVHT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DAVHT = ", DAVHT)
print("Counts for DAVHT = ", DAVHT, file = outputFile)
resultdata.update({"DAVHT": DAVHT})

print("Measuring DLVHT")
DLVHT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DLVHT = ", DLVHT)
print("Counts for DLVHT = ", DLVHT, file = outputFile)
resultdata.update({"DLVHT": DLVHT})

print("Measuring DLVVT")
DLVVT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DLVVT = ", DLVVT)
print("Counts for DLVVT = ", DLVVT, file = outputFile)
resultdata.update({"DLVVT": DLVVT})

DLVH=DLVVT

print("Measuring DRVVT")
DRVVT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRVVT = ", DRVVT)
print("Counts for DRVVT = ", DRVVT, file = outputFile)
resultdata.update({"DRVVT": DRVVT})

DRVH=DRVVT

print("Measuring DRVHT")
DRVHT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRVHT = ", DRVHT)
print("Counts for DRVHT = ", DRVHT, file = outputFile)
resultdata.update({"DRVHT": DRVHT})

print("Measuring DDVHT")
DDVHT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DDVHT = ", DDVHT)
print("Counts for DDVHT = ", DDVHT, file = outputFile)
resultdata.update({"DDVHT": DDVHT})

print("Measuring DDVVT")
DDVVT = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DDVVT = ", DDVVT)
print("Counts for DDVVT = ", DDVVT, file = outputFile)
resultdata.update({"DDVVT": DDVVT})

print("Measuring ADVVT")
ADVVT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ADVVT = ", ADVVT)
print("Counts for ADVVT = ", ADVVT, file = outputFile)
resultdata.update({"ADVVT": ADVVT})

print("Measuring ADVHT")
ADVHT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ADVHT = ", ADVHT)
print("Counts for ADVHT = ", ADVHT, file = outputFile)
resultdata.update({"ADVHT": ADVHT})

print("Measuring AAVHT")
AAVHT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for AAVHT = ", AAVHT)
print("Counts for AAVHT = ", AAVHT, file = outputFile)
resultdata.update({"AAVHT": AAVHT})

print("Measuring AAVVT")
AAVVT = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AAVVT = ", AAVVT)
print("Counts for AAVVT = ", AAVVT, file = outputFile)
resultdata.update({"AAVVT": AAVVT})

alarm()
instruction = "Please set the second strength plate to " + str(strHWP2Angle0) +", then press Enter"
input(instruction)
input("Please block Non1, Int2 paths, unblock all others, then press Enter")

print("Measuring VVA")
VVA = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVA = ", VVA)
print("Counts for VVA = ", VVA, file = outputFile)
resultdata.update({"VVA": VVA})

alarm()
input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring VVD")
VVD = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVD = ", VVD)
print("Counts for VVD = ", VVD, file = outputFile)
resultdata.update({"VVD": VVD})

alarm()
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring DVD")
DVD = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVD = ", DVD)
print("Counts for DVD = ", DVD, file = outputFile)
resultdata.update({"DVD": DVD})

print("Measuring LVD")
LVD = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVD = ", LVD)
print("Counts for LVD = ", LVD, file = outputFile)
resultdata.update({"LVD": LVD})

print("Measuring RVD")
RVD = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVD = ", RVD)
print("Counts for RVD = ", RVD, file = outputFile)
resultdata.update({"RVD": RVD})

print("Measuring AVD")
AVD = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVD = ", AVD)
print("Counts for AVD = ", AVD, file = outputFile)
resultdata.update({"AVD": AVD})

alarm()
input("Please block Int2 path, unblock all others, then press Enter")

print("Measuring AVA")
AVA = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for AVA = ", AVA)
print("Counts for AVA = ", AVA, file = outputFile)
resultdata.update({"AVA": AVA})

print("Measuring RVA")
RVA = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for RVA = ", RVA)
print("Counts for RVA = ", RVA, file = outputFile)
resultdata.update({"RVA": RVA})

print("Measuring LVA")
LVA = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for LVA = ", LVA)
print("Counts for LVA = ", LVA, file = outputFile)
resultdata.update({"LVA": LVA})

print("Measuring DVA")
DVA = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for DVA = ", DVA)
print("Counts for DVA = ", DVA, file = outputFile)
resultdata.update({"DVA": DVA})

alarm()
instruction = "Please rotate the initial HWP to "+str(rotHWPInizAngle0) + ", then press Enter"
input(instruction)

print("Measuring DHA")
DHA = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for DHA = ", DHA)
print("Counts for DHA = ", DHA, file = outputFile)
resultdata.update({"DHA": DHA})

print("Measuring LHA")
LHA = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for LHA = ", LHA)
print("Counts for LHA = ", LHA, file = outputFile)
resultdata.update({"LHA": LHA})

print("Measuring RHA")
RHA = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for RHA = ", RHA)
print("Counts for RHA = ", RHA, file = outputFile)
resultdata.update({"RHA": RHA})

print("Measuring AHA")
AHA = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for AHA = ", AHA)
print("Counts for AHA = ", AHA, file = outputFile)
resultdata.update({"AHA": AHA})

alarm()
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring AHD")
AHD = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for AHD = ", AHD)
print("Counts for AHD = ", AHD, file = outputFile)
resultdata.update({"AHD": AHD})

print("Measuring RHD")
RHD = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for RHD = ", RHD)
print("Counts for RHD = ", RHD, file = outputFile)
resultdata.update({"RHD": RHD})

print("Measuring LHD")
LHD = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for LHD = ", LHD)
print("Counts for LHD = ", LHD, file = outputFile)
resultdata.update({"LHD": LHD})

print("Measuring DHD")
DHD = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for DHD = ", DHD)
print("Counts for DHD = ", DHD, file = outputFile)
resultdata.update({"DHD": DHD})

alarm()
input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring VHD")
VHD = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for VHD = ", VHD)
print("Counts for VHD = ", VHD, file = outputFile)
resultdata.update({"VHD": VHD})

alarm()
input("Please block Non1, Int2 paths, unblock all others, then press Enter")

print("Measuring VHA")
VHA = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage0)
print("Counts for VHA = ", VHA)
print("Counts for VHA = ", VHA, file = outputFile)
resultdata.update({"VHA": VHA})

alarm()
instruction = "Please set first strength plate to maximum strength: "+str(strHWP1Angle0+strSignA*90/2) +" then press Enter"
input(instruction)
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring QSTA")
QSTA = measure(rotQWP1AngleQST315, rotHWP1AngleQST0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTA = ", QSTA    )
print("Counts for QSTA = ", QSTA, file = outputFile)
resultdata.update({"QSTA": QSTA})

print("Measuring QSTH")
QSTH = measure(rotQWP1AngleQST90, rotHWP1AngleQST0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTH = ", QSTH    )
print("Counts for QSTH = ", QSTH, file = outputFile)
resultdata.update({"QSTH": QSTH})

print("Measuring QSTR")
QSTR = measure(rotQWP1AngleQST90, rotHWP1AngleQST225, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTR = ", QSTR    )
print("Counts for QSTR = ", QSTR, file = outputFile)
resultdata.update({"QSTR": QSTR})

print("Measuring QSTV")
QSTV = measure(rotQWP1AngleQST90, rotHWP1AngleQST45, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTV = ", QSTV    )
print("Counts for QSTV = ", QSTV, file = outputFile)
resultdata.update({"QSTV": QSTV})

print("Measuring QSTD")
QSTD = measure(rotQWP1AngleQST45, rotHWP1AngleQST0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTD = ", QSTD    )
print("Counts for QSTD = ", QSTD, file = outputFile)
resultdata.update({"QSTD": QSTD})

print("Measuring QSTL")
QSTL = measure(rotQWP1AngleQST90, rotHWP1AngleQST675, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for QSTL = ", QSTL    )
print("Counts for QSTL = ", QSTL, file = outputFile)
resultdata.update({"QSTL": QSTL})

normconstant= QSTH+QSTV

rhoHHQST=QSTH/normconstant
rhoVVQST=QSTV/normconstant
rerhoHVQST=strSignA*(QSTD/normconstant-0.5)
imrhoHVQST=strSignA*(QSTR/normconstant-0.5)
rerhoVHQST=rerhoHVQST
imrhoVHQST=-imrhoHVQST

rawResultQST=qutip.Qobj([[rhoHHQST , rerhoHVQST+imrhoHVQST*1j],[rerhoVHQST+imrhoVHQST*1j, rhoVVQST]])
correction = qutip.Qobj([[1,0],[0,-1]])
resultQST=correction.dag()*rawResultQST*correction
                        
normconstant *=2

rho11HD=VHD/normconstant
rho10HD=0.5*(DHD-AHD+1.0j*(LHD-RHD))/normconstant
rho11HA=VHA/normconstant
rho10HA=0.5*(DHA-AHA+1.0j*(LHA-RHA))/normconstant
rho11VD=VVD/normconstant
rho10VD=0.5*(DVD-AVD+1.0j*(LVD-RVD))/normconstant
rho11VA=VVA/normconstant
rho10VA=0.5*(DVA-AVA+1.0j*(LVA-RVA))/normconstant

d=2
rhoHHDirac=(d*np.tan(np.radians(strengthA/2))*rho11HA+ rho10HA+rho10HD )/np.sin(np.radians(strengthA))
rhoHVDirac=(rho10HD-rho10HA )/np.sin(np.radians(strengthA))
#Additional minus sign due to trick
rhoVHDirac=-(rho10VD-rho10VA )/np.sin(np.radians(strengthA))
rhoVVDirac=(d*np.tan(np.radians(strengthA/2))*rho11VA+ rho10VA+rho10VD )/np.sin(np.radians(strengthA))
resultDirac=qutip.Qobj([[rhoHHDirac , rhoHVDirac],[rhoVHDirac, rhoVVDirac]])

rhoHHTwoAnc=4*VVHH/normconstant/(np.sin(np.radians(strengthA))**2 * np.sin(np.radians(strengthB))**2)
rhoVVTwoAnc=4*VVVV/normconstant/(np.sin(np.radians(strengthA))**2 * np.sin(np.radians(strengthB))**2)
rerhoHVTwoAnc=(RLHV+LRHV-RRHV-LLHV)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoHVTwoAnc=(DLHV-DRHV+ARHV-ALHV)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
rerhoVHTwoAnc=(RLVH+LRVH-RRVH-LLVH)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoVHTwoAnc=(DLVH-DRVH+ARVH-ALVH)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
resultTwoAnc=qutip.Qobj([[rhoHHTwoAnc , rerhoHVTwoAnc+imrhoHVTwoAnc*1j],[rerhoVHTwoAnc+imrhoVHTwoAnc*1j, rhoVVTwoAnc]])

rerhoHHTekkComplete=0.5*((DDHH-DAHH-ADHH+AAHH)-(LLHH-LRHH-RLHH+RRHH)+2*np.tan(np.radians(strengthB/2))*(DVHH-AVHH)+2*np.tan(np.radians(strengthA/2))*(VDHH-VAHH)+4*np.tan(np.radians(strengthA/2))*np.tan(np.radians(strengthB/2))*VVHH)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoHHTekkComplete=0.5*((LDHH-LAHH-RDHH+RAHH)+(DLHH-DRHH-ALHH+ARHH)+2*np.tan(np.radians(strengthB/2))*(LVHH-RVHH))/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
#additional minus sign are due to tricks
rerhoHVTekkComplete=0.5*((DDHV-DAHV-ADHV+AAHV)-(LLHV-LRHV-RLHV+RRHV)+2*np.tan(np.radians(strengthB/2))*(DVHV-AVHV)+2*np.tan(np.radians(strengthA/2))*(VDHV-VAHV)+4*np.tan(np.radians(strengthA/2))*np.tan(np.radians(strengthB/2))*VVHV)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoHVTekkComplete=0.5*((LDHV-LAHV-RDHV+RAHV)+(DLHV-DRHV-ALHV+ARHV)+2*np.tan(np.radians(strengthB/2))*(LVHV-RVHV))/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
rerhoVHTekkComplete=-0.5*((DDVHT-DAVHT-ADVHT+AAVHT)-(LLVHT-LRVHT-RLVHT+RRVHT)+2*np.tan(np.radians(strengthB/2))*(DVVHT-AVVHT)+2*np.tan(np.radians(strengthA/2))*(VDVHT-VAVHT)+4*np.tan(np.radians(strengthA/2))*np.tan(np.radians(strengthB/2))*VVVHT)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoVHTekkComplete=-0.5*((LDVHT-LAVHT-RDVHT+RAVHT)+(DLVHT-DRVHT-ALVHT+ARVHT)+2*np.tan(np.radians(strengthB/2))*(LVVHT-RVVHT))/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
rerhoVVTekkComplete=0.5*((DDVVT-DAVVT-ADVVT+AAVVT)-(LLVVT-LRVVT-RLVVT+RRVVT)+2*np.tan(np.radians(strengthB/2))*(DVVVT-AVVVT)+2*np.tan(np.radians(strengthA/2))*(VDVVT-VAVVT)+4*np.tan(np.radians(strengthA/2))*np.tan(np.radians(strengthB/2))*VVVVT)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoVVTekkComplete=0.5*((LDVVT-LAVVT-RDVVT+RAVVT)+(DLVVT-DRVVT-ALVVT+ARVVT)+2*np.tan(np.radians(strengthB/2))*(LVVVT-RVVVT))/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
rerhoHHTekk=0.5*((DDHH-DAHH-ADHH+AAHH)-(LLHH-LRHH-RLHH+RRHH))/normconstant
imrhoHHTekk=0.5*((LDHH-LAHH-RDHH+RAHH)+(DLHH-DRHH-ALHH+ARHH))/normconstant
rerhoHVTekk=0.5*((DDHV-DAHV-ADHV+AAHV)-(LLHV-LRHV-RLHV+RRHV))/normconstant
imrhoHVTekk=0.5*((LDHV-LAHV-RDHV+RAHV)+(DLHV-DRHV-ALHV+ARHV))/normconstant
rerhoVHTekk=-0.5*((DDVHT-DAVHT-ADVHT+AAVHT)-(LLVHT-LRVHT-RLVHT+RRVHT))/normconstant
imrhoVHTekk=-0.5*((LDVHT-LAVHT-RDVHT+RAVHT)+(DLVHT-DRVHT-ALVHT+ARVHT))/normconstant
rerhoVVTekk=0.5*((DDVVT-DAVVT-ADVVT+AAVVT)-(LLVVT-LRVVT-RLVVT+RRVVT))/normconstant
imrhoVVTekk=0.5*((LDVVT-LAVVT-RDVVT+RAVVT)+(DLVVT-DRVVT-ALVVT+ARVVT))/normconstant
rerhoHHTekkCorrection=rerhoHHTekkComplete-rerhoHHTekk
imrhoHHTekkCorrection=imrhoHHTekkComplete-imrhoHHTekk
rerhoHVTekkCorrection=rerhoHVTekkComplete-rerhoHVTekk
imrhoHVTekkCorrection=imrhoHVTekkComplete-imrhoHVTekk
rerhoVHTekkCorrection=rerhoVHTekkComplete-rerhoVHTekk
imrhoVHTekkCorrection=imrhoVHTekkComplete-imrhoVHTekk
rerhoVVTekkCorrection=rerhoVVTekkComplete-rerhoVVTekk
imrhoVVTekkCorrection=imrhoVVTekkComplete-imrhoVVTekk

resultTekkComplete=qutip.Qobj([[rerhoHHTekkComplete+imrhoHHTekkComplete*1j , rerhoHVTekkComplete+imrhoHVTekkComplete*1j],[rerhoVHTekkComplete+imrhoVHTekkComplete*1j, rerhoVVTekkComplete+imrhoVVTekkComplete*1j]])
resultTekk=qutip.Qobj([[rerhoHHTekk+imrhoHHTekk*1j , rerhoHVTekk+imrhoHVTekk*1j],[rerhoVHTekk+imrhoVHTekk*1j, rerhoVVTekk+imrhoVVTekk*1j]])
resultTekkCorrection=qutip.Qobj([[rerhoHHTekkCorrection+imrhoHHTekkCorrection*1j , rerhoHVTekkCorrection+imrhoHVTekkCorrection*1j],[rerhoVHTekkCorrection+imrhoVHTekkCorrection*1j, rerhoVVTekkCorrection+imrhoVVTekkCorrection*1j]])

#save qobjs
qutip.qsave([resultQST, resultDirac, resultTwoAnc, resultTekkComplete, resultTekk, resultTekkCorrection], outputfilename[:-4])
    
#output of final results
print("Final result")
print("rawResultQST = ", rawResultQST)
print("resultQST = ", resultQST)
print("resultDirac = ", resultDirac)
print("resultTwoAnc = ", resultTwoAnc)
print("resultTekkComplete = ", resultTekkComplete)
print("resultTekk = ", resultTekk)
print("resultTekkCorrection = ", resultTekkCorrection)

print("Final result", file = outputFile)
print("rawResultQST = ", rawResultQST, file = outputFile)
print("resultQST = ", resultQST, file = outputFile)
print("resultDirac = ", resultDirac, file = outputFile)
print("resultTwoAnc = ", resultTwoAnc, file = outputFile)
print("resultTekkComplete = ", resultTekkComplete, file = outputFile)
print("resultTekk = ", resultTekk, file = outputFile)
print("resultTekkCorrection = ", resultTekkCorrection, file = outputFile)

stoptime=datetime.datetime.now()
resultdata.update({ "StartTime":str(starttime), "StopTime":str(stoptime)})                    

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)
