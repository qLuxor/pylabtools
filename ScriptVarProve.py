# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 17:46:52 2017

@author: Giulio Foletto 2
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

outputfilename+="VarProve"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for VarProve", file = outputFile)

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
lcc1.enable = False #due to malfunctioning, change if necessary

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

strengthA=90
strengthB=90
strCoeffA=settings["strCoeffA"]
strCoeffB=settings["strCoeffB"]

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
instruction = "Please rotate LCR1 to " + str(rotLCR1Angle0) + " and LCR2 to " + str(rotLCR2Angle315) + ", then press Enter"
input(instruction)
instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0) +"\tInt2 " +str(strHWP2Angle0+strCoeffB*strengthB/2)  +" then press Enter"
input(instruction)
input("Please block Non1, Non2 paths, unblock all others, then press Enter")

print("Measuring c0")
c0 = measure(rotQWP1Angle0, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c0 = ", c0, "\tNormalized as = ", c0/c0)
print("Counts for c0 = ", c0, "\tNormalized as = ", c0/c0, file = outputFile)
resultdata.update({"c0": c0})

print("Measuring c1")
c1 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c1 = ", c1, "\tNormalized as = ", c1/c0)
print("Counts for c1 = ", c1, "\tNormalized as = ", c1/c0, file = outputFile)
resultdata.update({"c1": c1})

print("Measuring c2")
c2 = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c2 = ", c2, "\tNormalized as = ", c2/c0)
print("Counts for c2 = ", c2, "\tNormalized as = ", c2/c0, file = outputFile)
resultdata.update({"c2": c2})

print("Measuring c3")
c3 = measure(rotQWP1Angle0, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c3 = ", c3, "\tNormalized as = ", c3/c0)
print("Counts for c3 = ", c3, "\tNormalized as = ", c3/c0,file = outputFile)
resultdata.update({"c3": c3})

print("Measuring c4")
c4 = measure(rotQWP1Angle45, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c4 = ", c4, "\tNormalized as = ", c4/c0)
print("Counts for c4 = ", c4, "\tNormalized as = ", c4/c0, file = outputFile)
resultdata.update({"c4": c4})

print("Measuring c5")
c5 = measure(rotQWP1Angle90, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c5 = ", c5, "\tNormalized as = ", c5/c0)
print("Counts for c5 = ", c5, "\tNormalized as = ", c5/c0, file = outputFile)
resultdata.update({"c5": c5})

print("Measuring c6")
c6 = measure(rotQWP1Angle315, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c6 = ", c6, "\tNormalized as = ", c6/c0)
print("Counts for c6 = ", c6, "\tNormalized as = ", c6/c0, file = outputFile)
resultdata.update({"c6": c6})

instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0+strCoeffA*strengthA/2) +"\tInt2 " +str(strHWP2Angle0+strCoeffB*strengthB/2)  +" then press Enter"
input(instruction)

print("Measuring c7")
c7 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c7 = ", c7, "\tNormalized as = ", c7/c0)
print("Counts for c7 = ", c7, "\tNormalized as = ", c7/c0, file = outputFile)
resultdata.update({"c7": c7})

print("Measuring c8")
c8 = measure(rotQWP1Angle0, rotHWP1Angle45, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c8 = ", c8, "\tNormalized as = ", c8/c0)
print("Counts for c8 = ", c8, "\tNormalized as = ", c8/c0, file = outputFile)
resultdata.update({"c8": c8})

print("Measuring c9")
c9 = measure(rotQWP1Angle0, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c9 = ", c9, "\tNormalized as = ", c9/c0)
print("Counts for c9 = ", c9, "\tNormalized as = ", c9/c0, file = outputFile)
resultdata.update({"c9": c9})

print("Measuring c10")
c10 = measure(rotQWP1Angle0, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c10 = ", c10, "\tNormalized as = ", c10/c0)
print("Counts for c10 = ", c10, "\tNormalized as = ", c10/c0, file = outputFile)
resultdata.update({"c10": c10})

print("Measuring c11")
c11 = measure(rotQWP1Angle45, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c11 = ", c11, "\tNormalized as = ", c11/c0)
print("Counts for c11 = ", c11, "\tNormalized as = ", c11/c0, file = outputFile)
resultdata.update({"c11": c11})

print("Measuring c12")
c12 = measure(rotQWP1Angle90, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c12 = ", c12, "\tNormalized as = ", c12/c0)
print("Counts for c12 = ", c12, "\tNormalized as = ", c12/c0, file = outputFile)
resultdata.update({"c12": c12})

print("Measuring c13")
c13 = measure(rotQWP1Angle315, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c13 = ", c13, "\tNormalized as = ", c13/c0)
print("Counts for c13 = ", c13, "\tNormalized as = ", c13/c0, file = outputFile)
resultdata.update({"c13": c13})

print("Measuring c14")
c14 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c14 = ", c14, "\tNormalized as = ", c14/c0)
print("Counts for c14 = ", c14, "\tNormalized as = ", c14/c0, file = outputFile)
resultdata.update({"c14": c14})

print("Measuring c15")
c15 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c15 = ", c15, "\tNormalized as = ", c15/c0)
print("Counts for c15 = ", c15, "\tNormalized as = ", c15/c0, file = outputFile)
resultdata.update({"c15": c15})

print("Measuring c16")
c16 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c16 = ", c16, "\tNormalized as = ", c16/c0)
print("Counts for c16 = ", c16, "\tNormalized as = ", c16/c0, file = outputFile)
resultdata.update({"c16": c16})

print("Measuring c17")
c17 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c17 = ", c17, "\tNormalized as = ", c17/c0)
print("Counts for c17 = ", c17, "\tNormalized as = ", c17/c0, file = outputFile)
resultdata.update({"c17": c17})

print("Measuring c18")
c18 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c18 = ", c18, "\tNormalized as = ", c18/c0)
print("Counts for c18 = ", c18, "\tNormalized as = ", c18/c0, file = outputFile)
resultdata.update({"c18": c18})

print("Measuring c19")
c19 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle315, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c19 = ", c19, "\tNormalized as = ", c19/c0)
print("Counts for c19 = ", c19, "\tNormalized as = ", c19/c0, file = outputFile)
resultdata.update({"c19": c19})

instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0+strCoeffA*strengthA/2) +"\tInt2 " +str(strHWP2Angle0)  +" then press Enter"
input(instruction)

print("Measuring c20")
c20 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c20 = ", c20, "\tNormalized as = ", c20/c0)
print("Counts for c20 = ", c20, "\tNormalized as = ", c20/c0, file = outputFile)
resultdata.update({"c20": c20})           

print("Measuring c21")
c21 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c21 = ", c21, "\tNormalized as = ", c21/c0)
print("Counts for c21 = ", c21, "\tNormalized as = ", c21/c0, file = outputFile)
resultdata.update({"c21": c21})       

print("Measuring c22")
c22 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c22 = ", c22, "\tNormalized as = ", c22/c0)
print("Counts for c22 = ", c22, "\tNormalized as = ", c22/c0, file = outputFile)
resultdata.update({"c22": c22})   
                                                       
print("Measuring c23")
c23 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c23 = ", c23, "\tNormalized as = ", c23/c0)
print("Counts for c23 = ", c23, "\tNormalized as = ", c23/c0, file = outputFile)
resultdata.update({"c23": c23})   

print("Measuring c24")
c24 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c24 = ", c24, "\tNormalized as = ", c24/c0)
print("Counts for c24 = ", c24, "\tNormalized as = ", c24/c0, file = outputFile)
resultdata.update({"c24": c24})   

print("Measuring c25")
c25 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c25 = ", c25, "\tNormalized as = ", c25/c0)
print("Counts for c25 = ", c25, "\tNormalized as = ", c25/c0, file = outputFile)
resultdata.update({"c25": c25}) 

print("Measuring c26")
c26 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle315, rotHWP2Angle0, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c26 = ", c26, "\tNormalized as = ", c26/c0)
print("Counts for c26 = ", c26, "\tNormalized as = ", c26/c0, file = outputFile)
resultdata.update({"c26": c26}) 

instruction = "Please set strength plates to the desired values: Int1 "+str(strHWP1Angle0+strCoeffA*strengthA/2) +"\tInt2 " +str(strHWP2Angle0+strCoeffB*strengthB/2)  +" then press Enter"
input(instruction)
input("Please block Non2 path, unblock all others, then press Enter")

print("Measuring c27")
c27 = measure(rotQWP1Angle315, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c27 = ", c27, "\tNormalized as = ", c27/c0)
print("Counts for c27 = ", c27, "\tNormalized as = ", c27/c0, file = outputFile)
resultdata.update({"c27": c27}) 

print("Measuring c28")
c28 = measure(rotQWP1Angle45, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c28 = ", c28, "\tNormalized as = ", c28/c0)
print("Counts for c28 = ", c28, "\tNormalized as = ", c28/c0, file = outputFile)
resultdata.update({"c28": c28}) 

print("Measuring c29")
c29 = measure(rotQWP1Angle90, rotHWP1Angle225, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c29 = ", c29, "\tNormalized as = ", c29/c0)
print("Counts for c29 = ", c29, "\tNormalized as = ", c29/c0, file = outputFile)
resultdata.update({"c29": c29}) 

print("Measuring c30")
c30 = measure(rotQWP1Angle90, rotHWP1Angle675, rotQWP2Angle45, rotHWP2Angle315, rotHWPFinAngle675, lcc1Voltage180, lcc2Voltage0)
print("Counts for c30 = ", c30, "\tNormalized as = ", c30/c0)
print("Counts for c30 = ", c30, "\tNormalized as = ", c30/c0, file = outputFile)
resultdata.update({"c30": c30}) 

input("Please block Non1 path, unblock all others, then press Enter")

print("Measuring c31")
c31 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle90, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for c31 = ", c31, "\tNormalized as = ", c31/c0)
print("Counts for c31 = ", c31, "\tNormalized as = ", c31/c0, file = outputFile)
resultdata.update({"c31": c31}) 

print("Measuring c32")
c32 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle0, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for c32 = ", c32, "\tNormalized as = ", c32/c0)
print("Counts for c32 = ", c32, "\tNormalized as = ", c32/c0, file = outputFile)
resultdata.update({"c32": c32}) 

print("Measuring c33")
c33 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle675, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for c33 = ", c33, "\tNormalized as = ", c33/c0)
print("Counts for c33 = ", c33, "\tNormalized as = ", c33/c0, file = outputFile)
resultdata.update({"c33": c33}) 

print("Measuring c34")
c34 = measure(rotQWP1Angle0, rotHWP1Angle0, rotQWP2Angle45, rotHWP2Angle225, rotHWPFinAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for c34 = ", c34, "\tNormalized as = ", c34/c0)
print("Counts for c34 = ", c34, "\tNormalized as = ", c34/c0, file = outputFile)
resultdata.update({"c34": c34}) 

listconfig=[]

listconfig.append(c0)
listconfig.append(c1)
listconfig.append(c2)
listconfig.append(c3)
listconfig.append(c4)
listconfig.append(c5)
listconfig.append(c6)
listconfig.append(c7)
listconfig.append(c8)
listconfig.append(c9)
listconfig.append(c10)
listconfig.append(c11)
listconfig.append(c12)
listconfig.append(c13)
listconfig.append(c14)
listconfig.append(c15)
listconfig.append(c16)
listconfig.append(c17)
listconfig.append(c18)
listconfig.append(c19)
listconfig.append(c20)
listconfig.append(c21)
listconfig.append(c22)
listconfig.append(c23)
listconfig.append(c24)
listconfig.append(c25)
listconfig.append(c26)
listconfig.append(c27)
listconfig.append(c28)
listconfig.append(c29)
listconfig.append(c30)
listconfig.append(c31)
listconfig.append(c32)
listconfig.append(c33)
listconfig.append(c34)

for i in range(0, len(listconfig)):
    print(i,"\t", listconfig[i]/listconfig[0])

