# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 22:24:00 2017

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

outputfilename+="VarTwoAnc"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for VarTwoAnc protocols", file = outputFile)

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

#calibration values for rotHWP1
rotHWP1Angle0=settings["rotHWP1Angle0"]
rotHWP1Angle45=settings["rotHWP1Angle45"]
rotHWP1Angle225=settings["rotHWP1Angle225"]
rotHWP1Angle675=settings["rotHWP1Angle675"]

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

input("Please unblock all paths, then press Enter")

print("Measuring LRHV")
LRHV = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRHV = ", LRHV)
print("Counts for LRHV = ", LRHV, file = outputFile)
resultdata.update({"LRHV": LRHV})

print("Measuring RRHV")
RRHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRHV = ", RRHV)
print("Counts for RRHV = ", RRHV, file = outputFile)
resultdata.update({"RRHV": RRHV})

print("Measuring RLHV")
RLHV = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLHV = ", RLHV)
print("Counts for RLHV = ", RLHV, file = outputFile)
resultdata.update({"RLHV": RLHV})

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

print("Measuring DRHV")
DRHV = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRHV = ", DRHV)
print("Counts for DRHV = ", DRHV, file = outputFile)
resultdata.update({"DRHV": DRHV})

print("Measuring ARHV")
ARHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARHV = ", ARHV)
print("Counts for ARHV = ", ARHV, file = outputFile)
resultdata.update({"ARHV": ARHV})

print("Measuring ALHV")
ALHV = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALHV = ", ALHV)
print("Counts for ALHV = ", ALHV, file = outputFile)
resultdata.update({"ALHV": ALHV})

instruction = "Please rotate the initial HWP to "+str(rotHWPInizAngle45) + ", then press Enter"
input(instruction)

print("Measuring ALVH")
ALVH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ALVH = ", ALVH)
print("Counts for ALVH = ", ALVH, file = outputFile)
resultdata.update({"ALVH": ALVH})

print("Measuring ARVH")
ARVH = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for ARVH = ", ARVH)
print("Counts for ARVH = ", ARVH, file = outputFile)
resultdata.update({"ARVH": ARVH})

print("Measuring RRVH")
RRVH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RRVH = ", RRVH)
print("Counts for RRVH = ", RRVH, file = outputFile)
resultdata.update({"RRVH": RRVH})

print("Measuring LRVH")
LRVH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LRVH = ", LRVH)
print("Counts for LRVH = ", LRVH, file = outputFile)
resultdata.update({"LRVH": LRVH})

print("Measuring LLVH")
LLVH = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for LLVH = ", LLVH)
print("Counts for LLVH = ", LLVH, file = outputFile)
resultdata.update({"LLVH": LLVH})

print("Measuring RLVH")
RLVH = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for RLVH = ", RLVH)
print("Counts for RLVH = ", RLVH, file = outputFile)
resultdata.update({"RLVH": RLVH})

print("Measuring DLVH")
DLVH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DLVH = ", DLVH)
print("Counts for DLVH = ", DLVH, file = outputFile)
resultdata.update({"DLVH": DLVH})

print("Measuring DRVH")
DRVH = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for DRVH = ", DRVH)
print("Counts for DRVH = ", DRVH, file = outputFile)
resultdata.update({"DRVH": DRVH})

input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring VVVV")
VVVV = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle45, lcc1Voltage180, lcc2Voltage0)
print("Counts for VVVV = ", VVVV)
print("Counts for VVVV = ", VVVV, file = outputFile)
resultdata.update({"VVVV": VVVV})

normconstant=4*(VVHH+VVVV)/(np.sin(np.radians(strengthA))**2 * np.sin(np.radians(strengthB))**2)

rhoHHTwoAnc=4*VVHH/normconstant/(np.sin(np.radians(strengthA))**2 * np.sin(np.radians(strengthB))**2)
rhoVVTwoAnc=4*VVVV/normconstant/(np.sin(np.radians(strengthA))**2 * np.sin(np.radians(strengthB))**2)
rerhoHVTwoAnc=(RLHV+LRHV-RRHV-LLHV)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoHVTwoAnc=(DLHV-DRHV+ARHV-ALHV)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
rerhoVHTwoAnc=(RLVH+LRVH-RRVH-LLVH)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
imrhoVHTwoAnc=(DLVH-DRVH+ARVH-ALVH)/normconstant/(np.sin(np.radians(strengthA)) * np.sin(np.radians(strengthB)))
resultTwoAnc=qutip.Qobj([[rhoHHTwoAnc , rerhoHVTwoAnc+imrhoHVTwoAnc*1j],[rerhoVHTwoAnc+imrhoVHTwoAnc*1j, rhoVVTwoAnc]])

qutip.qsave([resultTwoAnc], outputfilename[:-4])

#output of final results
print("Final result")
print("Result = ", resultTwoAnc)

print("The following results are obtained using the diagonal measurements for normalization", file = outputFile)
print("Corrected normalization constant = {0}".format(normconstant), file = outputFile)
print("rhoHH = {0}".format(rhoHHTwoAnc), file = outputFile)
print("\nrhoVV = {0}".format(rhoVVTwoAnc), file = outputFile)
print("\nrerhoHV = {0}".format(rerhoHVTwoAnc), file = outputFile)
print("\nimrhoHV = {0}".format(imrhoHVTwoAnc), file = outputFile)
print("\nrerhoVH = {0}".format(rerhoVHTwoAnc), file = outputFile)
print("\nimrhoVH = {0}".format(imrhoVHTwoAnc), file = outputFile)
print("\nresult = ", resultTwoAnc, file = outputFile)

print("\n\n\n", file = outputFile)