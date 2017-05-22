# -*- coding: utf-8 -*-
"""
Created on Fri May 19 21:29:12 2017

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

outputfilename+="TekkCorrection"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for TekkCorrection protocol", file = outputFile)

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
rot1Angle90=settings["rot1Angle90"]
rot1Angle180=settings["rot1Angle180"]
rot1Angle270=settings["rot1Angle270"]

#calibration values for LCC1
lcc1Voltage0=settings["lcc1Voltage0"]
lcc1Voltage90=settings["lcc1Voltage90"]
lcc1Voltage180=settings["lcc1Voltage180"]
lcc1Voltage270=settings["lcc1Voltage270"]

#calibration values for ROT2
rot2Angle0=settings["rot2Angle0"]
rot2Angle90=settings["rot2Angle90"]
rot2Angle180=settings["rot2Angle180"]
rot2Angle270=settings["rot2Angle270"]

#calibration values for LCC2
lcc2Voltage0=settings["lcc2Voltage0"]
lcc2Voltage90=settings["lcc2Voltage90"]
lcc2Voltage180=settings["lcc2Voltage180"]
lcc2Voltage270=settings["lcc2Voltage270"]

#calibration values for ROTHWP
rotHWPAngle0=settings["rotHWPAngle0"]
rotHWPAngle45=settings["rotHWPAngle45"]
rotHWPAngle225=settings["rotHWPAngle225"]
rotHWPAngle675=settings["rotHWPAngle675"]

#calibration values for ROTQWP
rotQWPAngle0=settings["rotQWPAngle0"]
rotQWPAngle45=settings["rotQWPAngle45"]
rotQWPAngle90=settings["rotQWPAngle90"]

#functions that implements settings
def measure(rot1angle, rot2angle, rotHWPangle, rotQWPangle, lcc1voltage, lcc2voltage):
    setangle(rot1, rot1angle, angleErr)
    setangle(rot2, rot2angle, angleErr)
    setangle(rotHWP, rotHWPangle, angleErr)
    setangle(rotQWP, rotQWPangle, angleErr)
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
input("Please unblock all paths, then press enter")
#measurement on D for normalization
print("Measuring D for normalization")
countDId = measure(rot1Angle0, rot2Angle270, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
resultdata.update({"CDRaw": countDId, "CD": 4*countDId})
print("Counts for D = ", countDId)
print("Counts for D = ", countDId, file = outputFile)

#Measurement on A for normalization
print("Measuring A for normalization")
countAId = measure(rot1Angle0, rot2Angle270, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
resultdata.update({"CARaw": countAId, "CA": 4*countAId})
print("Counts for A = ", countAId)
print("Counts for A = ", countAId, file = outputFile)

normconstant= 4*(countDId+countAId)
resultdata.update({"NormConstant": normconstant})

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of DV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(HH)")
CDVHH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(HH) = ", CDVHH, "\tNormalized to diagonal = ", 2*CDVHH/normconstant)
print("Counts for DV for Re(HH) = ", CDVHH, "\tNormalized to diagonal = ", 2*CDVHH/normconstant, file = outputFile)
resultdata.update({"CDVHHRaw": CDVHH})
CDVHH *=2
resultdata.update({"CDVHH": CDVHH})

#measurement of DV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(VH)")
CDVVH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(VH) = ", CDVVH, "\tNormalized to diagonal = ", 2*CDVVH/normconstant)
print("Counts for DV for Re(VH) = ", CDVVH, "\tNormalized to diagonal = ", 2*CDVVH/normconstant, file = outputFile)
resultdata.update({"CDVVHRaw": CDVVH})
CDVVH *=2
resultdata.update({"CDVVH": CDVVH})

#measurement of RV
print("Measuring RV for Im(HH)")
CRVHH= measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RV for Im(HH) = ", CRVHH, "\tNormalized to diagonal = ", 2*CRVHH/normconstant)
print("Counts for RV for Im(HH) = ", CRVHH, "\tNormalized to diagonal = ", 2*CRVHH/normconstant, file = outputFile)
resultdata.update({"CRVHHRaw": CRVHH})
CRVHH *=2
resultdata.update({"CRVHH": CRVHH})

#measurement of LV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(VH)")
CLVVH= measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LV for Im(VH) = ", CLVVH, "\tNormalized to diagonal = ", 2*CLVVH/normconstant)
print("Counts for LV for Im(VH) = ", CLVVH, "\tNormalized to diagonal = ", 2*CLVVH/normconstant, file = outputFile)
resultdata.update({"CLVVHRaw": CLVVH})
CLVVH *=2
resultdata.update({"CLVVH": CLVVH})

#measurement of AV
print("Measuring AV for Re(HH)")
CAVHH= measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(HH) = ", CAVHH, "\tNormalized to diagonal = ", 2*CAVHH/normconstant)
print("Counts for AV for Re(HH) = ", CAVHH, "\tNormalized to diagonal = ", 2*CAVHH/normconstant, file = outputFile)
resultdata.update({"CAVHHRaw": CAVHH})
CAVHH *=2
resultdata.update({"CAVHH": CAVHH})

#measurement of AV
print("Measuring AV for Re(VH)")
CAVVH= measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(VH) = ", CAVVH, "\tNormalized to diagonal = ", 2*CAVVH/normconstant)
print("Counts for AV for Re(VH) = ", CAVVH, "\tNormalized to diagonal = ", 2*CAVVH/normconstant, file = outputFile)
resultdata.update({"CAVVHRaw": CAVVH})
CAVVH *=2
resultdata.update({"CAVVH": CAVVH})

#measurement of LV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(HH)")
CLVHH= measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LV for Im(HH) = ", CLVHH, "\tNormalized to diagonal = ", 2*CLVHH/normconstant)
print("Counts for LV for Im(HH) = ", CLVHH, "\tNormalized to diagonal = ", 2*CLVHH/normconstant, file = outputFile)
resultdata.update({"CLVHHRaw": CLVHH})
CLVHH *=2
resultdata.update({"CLVHH": CLVHH})

#measurement of RV
print("Measuring RV for Im(VH)")
CRVVH= measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RV for Im(VH) = ", CRVVH, "\tNormalized to diagonal = ", 2*CRVVH/normconstant)
print("Counts for RV for Im(VH) = ", CRVVH, "\tNormalized to diagonal = ", 2*CRVVH/normconstant, file = outputFile)
resultdata.update({"CRVVHRaw": CRVVH})
CRVVH *=2
resultdata.update({"CRVVH": CRVVH})

#measurement of LV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(HV)")
CLVHV= measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LV for Im(HV) = ", CLVHV, "\tNormalized to diagonal = ", 2*CLVHV/normconstant)
print("Counts for LV for Im(HV) = ", CLVHV, "\tNormalized to diagonal = ", 2*CLVHV/normconstant, file = outputFile)
resultdata.update({"CLVHVRaw": CLVHV})
CLVHV *=2
resultdata.update({"CLVHV": CLVHV})

#measurement of RV
print("Measuring RV for Im(VV)")
CRVVV= measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RV for Im(VV) = ", CRVVV, "\tNormalized to diagonal = ", 2*CRVVV/normconstant)
print("Counts for RV for Im(VV) = ", CRVVV, "\tNormalized to diagonal = ", 2*CRVVV/normconstant, file = outputFile)
resultdata.update({"CRVVVRaw": CRVVV})
CRVVV *=2
resultdata.update({"CRVVV": CRVVV})

#measurement of AV
print("Measuring AV for Re(HV)")
CAVHV= measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(HV) = ", CAVHV, "\tNormalized to diagonal = ", 2*CAVHV/normconstant)
print("Counts for AV for Re(HV) = ", CAVHV, "\tNormalized to diagonal = ", 2*CAVHV/normconstant, file = outputFile)
resultdata.update({"CAVHVRaw": CAVHV})
CAVHV *=2
resultdata.update({"CAVHV": CAVHV})

#measurement of AV
print("Measuring AV for Re(VV)")
CAVVV= measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(VV) = ", CAVVV, "\tNormalized to diagonal = ", 2*CAVVV/normconstant)
print("Counts for AV for Re(VV) = ", CAVVV, "\tNormalized to diagonal = ", 2*CAVVV/normconstant, file = outputFile)
resultdata.update({"CAVVVRaw": CAVVV})
CAVVV *=2
resultdata.update({"CAVVV": CAVVV})

#measurement of DV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(HV)")
CDVHV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(HV) = ", CDVHV, "\tNormalized to diagonal = ", 2*CDVHV/normconstant)
print("Counts for DV for Re(HV) = ", CDVHV, "\tNormalized to diagonal = ", 2*CDVHV/normconstant, file = outputFile)
resultdata.update({"CDVHVRaw": CDVHV})
CDVHV *=2
resultdata.update({"CDVHV": CDVHV})

#measurement of DV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(VV)")
CDVVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(VV) = ", CDVVV, "\tNormalized to diagonal = ", 2*CDVVV/normconstant)
print("Counts for DV for Re(VV) = ", CDVVV, "\tNormalized to diagonal = ", 2*CDVVV/normconstant, file = outputFile)
resultdata.update({"CDVVVRaw": CDVVV})
CDVVV *=2
resultdata.update({"CDVVV": CDVVV})

#measurement of RV
print("Measuring RV for Im(HV)")
CRVHV= measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RV for Im(HV) = ", CRVHV, "\tNormalized to diagonal = ", 2*CRVHV/normconstant)
print("Counts for RV for Im(HV) = ", CRVHV, "\tNormalized to diagonal = ", 2*CRVHV/normconstant, file = outputFile)
resultdata.update({"CLVHVRaw": CLVHV})
CLVHV *=2
resultdata.update({"CLVHV": CLVHV})

#measurement of LV
#input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(VV)")
CLVVV= measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LV for Im(VV) = ", CLVVV, "\tNormalized to diagonal = ", 2*CLVVV/normconstant)
print("Counts for LV for Im(VV) = ", CLVVV, "\tNormalized to diagonal = ", 2*CLVVV/normconstant, file = outputFile)
resultdata.update({"CLVVVRaw": CLVVV})
CLVVV *=2
resultdata.update({"CLVVV": CLVVV})


#measurement of VV
input("Please block V, A paths, unblock H, D, then press enter")
print("Measuring VV for Re(HV)")
CVVHV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(HV) = ", CVVHV, "\tNormalized to diagonal = ", 4*CVVHV/normconstant)
print("Counts for VV for Re(HV) = ", CVVHV, "\tNormalized to diagonal = ", 4*CVVHV/normconstant, file = outputFile)
resultdata.update({"CVVHVRaw": CVVHV})
CVVHV *=4
resultdata.update({"CVVHV": CVVHV})

#measurement of VV
#input("Please block V, A paths, unblock H, D, then press enter")
print("Measuring VV for Re(HH)")
CVVHH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(HH) = ", CVVHH, "\tNormalized to diagonal = ", 4*CVVHH/normconstant)
print("Counts for VV for Re(HH) = ", CVVHH, "\tNormalized to diagonal = ", 4*CVVHH/normconstant, file = outputFile)
resultdata.update({"CVVHHRaw": CVVHH})
CVVHH *=4
resultdata.update({"CVVHH": CVVHH})


#measurement of VV
input("Please block H, A paths, unblock V, D, then press enter")
print("Measuring VV for Re(VH)")
CVVVH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(VH) = ", CVVVH, "\tNormalized to diagonal = ", 4*CVVVH/normconstant)
print("Counts for VV for Re(VH) = ", CVVVH, "\tNormalized to diagonal = ", 4*CVVVH/normconstant, file = outputFile)
resultdata.update({"CVVVHRaw": CVVVH})
CVVVH *=4
resultdata.update({"CVVVH": CVVVH})

#measurement of VV
#input("Please block H, A paths, unblock V, D, then press enter")
print("Measuring VV for Re(VV)")
CVVVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(VV) = ", CVVVV, "\tNormalized to diagonal = ", CVVVV/normconstant)
print("Counts for VV for Re(VV) = ", CVVVV, "\tNormalized to diagonal = ", CVVVV/normconstant, file = outputFile)
resultdata.update({"CVVVVRaw": CVVVV})
CVVVV *=4
resultdata.update({"CVVVV": CVVVV})


#measurement of VD
input("Please block H path, unblock V, A, D, then press enter")
print("Measuring VD for Re(VV)")
CVDVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(VV) = ", CVDVV, "\tNormalized to diagonal = ", 2*CVDVV/normconstant)
print("Counts for VD for Re(VV) = ", CVDVV, "\tNormalized to diagonal = ", 2*CVDVV/normconstant, file = outputFile)
resultdata.update({"CVDVVRaw": CVDVV})
CVDVV *=2
resultdata.update({"CVDVV": CVDVV})

#measurement of VA
print("Measuring VA for Re(VV)")
CVAVV= measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(VV) = ", CVAVV, "\tNormalized to diagonal = ", 2*CVAVV/normconstant)
print("Counts for AV for Re(VV) = ", CVAVV, "\tNormalized to diagonal = ", 2*CVAVV/normconstant, file = outputFile)
resultdata.update({"CVAVVRaw": CVAVV})
CVAVV *=2
resultdata.update({"CVAVV": CVAVV})

#measurement of VA
print("Measuring VA for Re(VH)")
CVAVH= measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(VH) = ", CVAVH, "\tNormalized to diagonal = ", 2*CVAVH/normconstant)
print("Counts for AV for Re(VH) = ", CVAVH, "\tNormalized to diagonal = ", 2*CVAVH/normconstant, file = outputFile)
resultdata.update({"CVAVHRaw": CVAVH})
CVAVH *=2
resultdata.update({"CVAVH": CVAVH})

#measurement of VD
#input("Please block H path, unblock V, A, D, then press enter")
print("Measuring VD for Re(VH)")
CVDVH=measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(VH) = ", CVDVH, "\tNormalized to diagonal = ", 2*CVDVH/normconstant)
print("Counts for VD for Re(VH) = ", CVDVH, "\tNormalized to diagonal = ", 2*CVDVH/normconstant, file = outputFile)
resultdata.update({"CVDVHRaw": CVDVH})
CVDVH *=2
resultdata.update({"CVDVH": CVDVH})


#measurement of VD
input("Please block V path, unblock H, A, D, then press enter")
print("Measuring VD for Re(HH)")
CVDHH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(HH) = ", CVDHH, "\tNormalized to diagonal = ", 2*CVDHH/normconstant)
print("Counts for VD for Re(HH) = ", CVDHH, "\tNormalized to diagonal = ", 2*CVDHH/normconstant, file = outputFile)
resultdata.update({"CVDHHRaw": CVDHH})
CVDHH *=2
resultdata.update({"CVDHH": CVDHH})

#measurement of VA
print("Measuring VA for Re(HH)")
CVAHH= measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(HH) = ", CVAHH, "\tNormalized to diagonal = ", 2*CVAHH/normconstant)
print("Counts for AV for Re(HH) = ", CVAHH, "\tNormalized to diagonal = ", 2*CVAHH/normconstant, file = outputFile)
resultdata.update({"CVAHHRaw": CVAHH})
CVAHH *=2
resultdata.update({"CVAHH": CVAHH})

#measurement of VA
print("Measuring VA for Re(HV)")
CVAHV= measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(HV) = ", CVAHV, "\tNormalized to diagonal = ", 2*CVAHV/normconstant)
print("Counts for AV for Re(HV) = ", CVAHV, "\tNormalized to diagonal = ", 2*CVAHV/normconstant, file = outputFile)
resultdata.update({"CVAHVRaw": CVAHV})
CVAHV *=2
resultdata.update({"CVAHV": CVAHV})

#measurement of VD
#input("Please block V path, unblock H, A, D, then press enter")
print("Measuring VD for Re(HV)")
CVDHV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(HV) = ", CVDHV, "\tNormalized to diagonal = ", 2*CVDHV/normconstant)
print("Counts for VD for Re(HV) = ", CVDHV, "\tNormalized to diagonal = ", 2*CVDHV/normconstant, file = outputFile)
resultdata.update({"CVDHVRaw": CVDHV})
CVDHV *=2
resultdata.update({"CVDHV": CVDHV})


#extraction of result
rerhoHH=((CDVHH-CAVHH)+(CVDHH-CVAHH)+2*CVVHH)/normconstant
imrhoHH=(CLVHH-CRVHH)/normconstant
rerhoHV=((CDVHV-CAVHV)+(CVDHV-CVAHV)+2*CVVHV)/normconstant
imrhoHV=(CLVHV-CRVHV)/normconstant
rerhoVH=((CDVVH-CAVVH)+(CVDVH-CVAVH)+2*CVVVH)/normconstant
imrhoVH=(CLVVH-CRVVH)/normconstant
rerhoVV=((CDVVV-CAVVV)+(CVDVV-CVAVV)+2*CVVVV)/normconstant
imrhoVV=(CLVVV-CRVVV)/normconstant

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

result=qutip.Qobj([[rerhoHH+imrhoHH*1j , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rerhoVV+imrhoVV*1j]])
resquad=result**2
purity= resquad.tr()

#save qobjs
qutip.qsave([result, resquad], outputfilename[:-4])

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)

#output of final results
print("Final result")
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

print("The following results are obtained using the diagonal measurements for normalization", file = outputFile)
print("Corrected normalization constant = {0}".format(normconstant), file = outputFile)
print("rerhoHH = {0}".format(rerhoHH), file = outputFile)
print("imrhoHH = {0}".format(imrhoHH), file = outputFile)
print("\nrerhoHV = {0}".format(rerhoHV), file = outputFile)
print("\nimrhoHV = {0}".format(imrhoHV), file = outputFile)
print("\nrerhoVH = {0}".format(rerhoVH), file = outputFile)
print("\nimrhoVH = {0}".format(imrhoVH), file = outputFile)
print("\nrerhoVV = {0}".format(rerhoVV), file = outputFile)
print("\nimrhoVV = {0}".format(imrhoVV), file = outputFile)
print("\nresult = ", result, file = outputFile)
print("\nresquad = ", resquad, file = outputFile)
print("\npurity = ", purity, file = outputFile)