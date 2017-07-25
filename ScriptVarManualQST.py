# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 21:49:44 2017

@author: Giulio Foletto
"""

#necessary imports
import sys
sys.path.append('..')
import time
import datetime
from ThorCon import ThorCon
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

outputfilename+="VarManualQST"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for VarManualQST protocol", file = outputFile)

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
lcc2.enable = True

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
if home:
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
if home:
    rotHWPFin.home()
    
print("Finished initialization\n\n")
#calibration values for LCC1
lcc1Voltage180=settings["lcc1Voltage180"]

#calibration values for LCC2
lcc2Voltage90=settings["lcc2Voltage90"]

#calibration values for rotLCC
rotLCR1Angle0=settings["rotLCR1Angle0"]
rotLCR2Angle0=settings["rotLCR2Angle0"]
rotLCR2Angle315=settings["rotLCR2Angle315"]

#calibration values for rotQWP1
rotQWP1Angle0=settings["rotQWP1Angle0"]

#calibration values for rotHWP1
rotHWP1Angle45=settings["rotHWP1Angle45"]

#calibration values for rotQWP2
rotQWP2Angle45=settings["rotQWP2Angle45"]

#calibration values for rotHWP2
rotHWP2Angle0=settings["rotHWP2Angle0"]

#calibration values for rotHWPFin
rotHWPFinAngle0=settings["rotHWPFinAngle0"]
rotHWPFinAngle45=settings["rotHWPFinAngle45"]
rotHWPFinAngle225=settings["rotHWPFinAngle225"]

#calibration values for rotHWPFin
rotHWPInizAngle0=settings["rotHWPInizAngle0"]

#calibration values for strPlates
strHWP1Angle0=settings["strHWP1Angle0"]
strHWP2Angle0=settings["strHWP2Angle0"]
strQWP1Angle0=settings["strQWP1Angle0"]
strQWP2Angle0=settings["strQWP2Angle0"]

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

instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0) +"\tInt2 " +str(strHWP2Angle0)  +" then press Enter"
input(instruction)
instruction = "Please rotate LCR1 to " + str(rotLCR1Angle0) + " and LCR2 to " + str(rotLCR2Angle0) + ", then press Enter"
input(instruction)
instruction = "Please rotate the initial HWP to "+str(rotHWPInizAngle0) + ", then press Enter"
input(instruction)
input("Please unblock all paths, then press Enter")

print("Measuring QSTH")
QSTH = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for QSTH = ", QSTH    )
print("Counts for QSTH = ", QSTH, file = outputFile)
resultdata.update({"QSTH": QSTH})

print("Measuring QSTV")
QSTV = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage90)
print("Counts for QSTV = ", QSTV    )
print("Counts for QSTV = ", QSTV, file = outputFile)
resultdata.update({"QSTV": QSTV})

print("Measuring QSTR")
QSTR = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage90)
print("Counts for QSTR = ", QSTR)
print("Counts for QSTR = ", QSTR, file = outputFile)
resultdata.update({"QSTR": QSTR})

instruction = "Please rotate LCR2 to " + str(rotLCR2Angle315) + ", then press Enter"
input(instruction)

print("Measuring QSTD")
QSTD = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle225, lcc1Voltage180, lcc2Voltage90)
print("Counts for QSTD = ", QSTD)
print("Counts for QSTD = ", QSTD, file = outputFile)
resultdata.update({"QSTD": QSTD})

normconstant= QSTH+QSTV

rhoHHQST=QSTH/normconstant
rhoVVQST=QSTV/normconstant
rerhoHVQST=QSTD/normconstant-0.5
imrhoHVQST=QSTR/normconstant-0.5
rerhoVHQST=rerhoHVQST
imrhoVHQST=-imrhoHVQST

resultQST=qutip.Qobj([[rhoHHQST , rerhoHVQST+imrhoHVQST*1j],[rerhoVHQST+imrhoVHQST*1j, rhoVVQST]])

#save qobjs
qutip.qsave([resultQST], outputfilename[:-4])

#output of final results
print("Final result")
print("Result = ", resultQST)

stoptime=datetime.datetime.now()
resultdata.update({ "StartTime":str(starttime), "StopTime":str(stoptime)})                    

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)