# -*- coding: utf-8 -*-
"""
Created on Tue May  9 10:15:16 2017

@author: Giulio Foletto
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

outputfilename+="TekkComplete"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for TekkComplete protocol", file = outputFile)

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



#measurement of Re(HH)
input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(HH)")
CDDHH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(HH) = ", CDDHH, "\tNormalized to diagonal = ", CDDHH/normconstant)
print("Counts for DD for Re(HH) = ", CDDHH, "\tNormalized to diagonal = ", CDDHH/normconstant, file = outputFile)
resultdata.update({"CDDHH": CDDHH})

#measurement of RL
print("Measuring RL for Re(HH)")
CRLHH= measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for RL for Re(HH) = ", CRLHH, "\tNormalized to diagonal = ", CRLHH/normconstant)
print("Counts for RL for Re(HH) = ", CRLHH, "\tNormalized to diagonal = ", CRLHH/normconstant, file = outputFile)
resultdata.update({"CRLHH": CRLHH})

#measurement of RR
print("Measuring RR for Re(HH)")
CRRHH= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for RR for Re(HH) = ", CRRHH, "\tNormalized to diagonal = ", CRRHH/normconstant)
print("Counts for RR for Re(HH) = ", CRRHH, "\tNormalized to diagonal = ", CRRHH/normconstant, file = outputFile)
resultdata.update({"CRRHH": CRRHH})

#measurement of AD
print("Measuring AD for Re(HH)")
CADHH= measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(HH) = ", CADHH, "\tNormalized to diagonal = ", CADHH/normconstant)
print("Counts for AD for Re(HH) = ", CADHH, "\tNormalized to diagonal = ", CADHH/normconstant, file = outputFile)
resultdata.update({"CADHH": CADHH})

#measurement of LR
print("Measuring LR for Re(HH)")
CLRHH= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for LR for Re(HH) = ", CLRHH, "\tNormalized to diagonal = ", CLRHH/normconstant)
print("Counts for LR for Re(HH) = ", CLRHH, "\tNormalized to diagonal = ", CLRHH/normconstant, file = outputFile)
resultdata.update({"CLRHH": CLRHH})

#measurement of LL
print("Measuring LL for Re(HH)")
CLLHH = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LL for Re(HH) = ", CLLHH, "\tNormalized to diagonal = ", CLLHH/normconstant)
print("Counts for LL for Re(HH) = ", CLLHH, "\tNormalized to diagonal = ", CLLHH/normconstant, file = outputFile)
resultdata.update({"CLLHH": CLLHH})

#measurement of AA
print("Measuring AA for Re(HH)")
CAAHH= measure(rot1Angle180, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(HH) = ", CAAHH, "\tNormalized to diagonal = ", CAAHH/normconstant)
print("Counts for AA for Re(HH) = ", CAAHH, "\tNormalized to diagonal = ", CAAHH/normconstant, file = outputFile)
resultdata.update({"CAAHH": CAAHH})

#measurement of DA
print("Measuring DA for Re(HH)")
CDAHH= measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(HH) = ", CDAHH, "\tNormalized to diagonal = ", CDAHH/normconstant)
print("Counts for DA for Re(HH) = ", CDAHH, "\tNormalized to diagonal = ", CDAHH/normconstant, file = outputFile)
resultdata.update({"CDAHH": CDAHH})


#measurement of Im(HH)
#measurement of RA
print("Measuring RA for Im(HH)")
CRAHH= measure(rot1Angle270, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for RA for Im(HH) = ", CRAHH, "\tNormalized to diagonal = ", CRAHH/normconstant)
print("Counts for RA for Im(HH) = ", CRAHH, "\tNormalized to diagonal = ", CRAHH/normconstant, file = outputFile)
resultdata.update({"CRAHH": CRAHH})

#measurement of LA
print("Measuring LA for Im(HH)")
CLAHH= measure(rot1Angle90, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for LA for Im(HH) = ", CLAHH, "\tNormalized to diagonal = ", CLAHH/normconstant)
print("Counts for LA for Im(HH) = ", CLAHH, "\tNormalized to diagonal = ", CLAHH/normconstant, file = outputFile)
resultdata.update({"CLAHH": CLAHH})

#input("Please unblock all paths, then press enter")
#measurement of LD
print("Measuring LD for Im(HH)")
CLDHH= measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LD for Im(HH) = ", CLDHH, "\tNormalized to diagonal = ", CLDHH/normconstant)
print("Counts for LD for Im(HH) = ", CLDHH, "\tNormalized to diagonal = ", CLDHH/normconstant, file = outputFile)
resultdata.update({"CLDHH": CLDHH})

#measurement of AR
print("Measuring AR for Im(HH)")
CARHH= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(HH) = ", CARHH, "\tNormalized to diagonal = ", CARHH/normconstant)
print("Counts for AR for Im(HH) = ", CARHH, "\tNormalized to diagonal = ", CARHH/normconstant, file = outputFile)
resultdata.update({"CARHH": CARHH})

#measurement of AL
print("Measuring AL for Im(HH)")
CALHH = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(HH) = ", CALHH, "\tNormalized to diagonal = ", CALHH/normconstant)
print("Counts for AL for Im(HH) = ", CALHH, "\tNormalized to diagonal = ", CALHH/normconstant, file = outputFile)
resultdata.update({"CALHH": CALHH})

#measurement of DL
print("Measuring DL for Im(HH)")
CDLHH= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(HH) = ", CDLHH, "\tNormalized to diagonal = ", CDLHH/normconstant)
print("Counts for DL for Im(HH) = ", CDLHH, "\tNormalized to diagonal = ", CDLHH/normconstant, file = outputFile)
resultdata.update({"CDLHH": CDLHH})

#measurement of DR
print("Measuring DR for Im(HH)")
CDRHH= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(HH) = ", CDRHH, "\tNormalized to diagonal = ", CDRHH/normconstant)
print("Counts for DR for Im(HH) = ", CDRHH, "\tNormalized to diagonal = ", CDRHH/normconstant, file = outputFile)
resultdata.update({"CDRHH": CDRHH})

#measurement of RD
print("Measuring RD for Im(HH)")
CRDHH= measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RD for Im(HH) = ", CRDHH, "\tNormalized to diagonal = ", CRDHH/normconstant)
print("Counts for RD for Im(HH) = ", CRDHH, "\tNormalized to diagonal = ", CRDHH/normconstant, file = outputFile)
resultdata.update({"CRDHH": CRDHH})


#measurement of Re(HV)
#input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(HV)")
CDDHV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(HV) = ", CDDHV, "\tNormalized to diagonal = ", CDDHV/normconstant)
print("Counts for DD for Re(HV) = ", CDDHV, "\tNormalized to diagonal = ", CDDHV/normconstant, file = outputFile)
resultdata.update({"CDDHV": CDDHV})

#measurement of RL
print("Measuring RL for Re(HV)")
CRLHV= measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for RL for Re(HV) = ", CRLHV, "\tNormalized to diagonal = ", CRLHV/normconstant)
print("Counts for RL for Re(HV) = ", CRLHV, "\tNormalized to diagonal = ", CRLHV/normconstant, file = outputFile)
resultdata.update({"CRLHV": CRLHV})

#measurement of RR
print("Measuring RR for Re(HV)")
CRRHV= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for RR for Re(HV) = ", CRRHV, "\tNormalized to diagonal = ", CRRHV/normconstant)
print("Counts for RR for Re(HV) = ", CRRHV, "\tNormalized to diagonal = ", CRRHV/normconstant, file = outputFile)
resultdata.update({"CRRHV": CRRHV})

#measurement of AD
print("Measuring AD for Re(HV)")
CADHV= measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(HV) = ", CADHV, "\tNormalized to diagonal = ", CADHV/normconstant)
print("Counts for AD for Re(HV) = ", CADHV, "\tNormalized to diagonal = ", CADHV/normconstant, file = outputFile)
resultdata.update({"CADHV": CADHV})

#measurement of LR
print("Measuring LR for Re(HV)")
CLRHV= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for LR for Re(HV) = ", CLRHV, "\tNormalized to diagonal = ", CLRHV/normconstant)
print("Counts for LR for Re(HV) = ", CLRHV, "\tNormalized to diagonal = ", CLRHV/normconstant, file = outputFile)
resultdata.update({"CLRHV": CLRHV})

#measurement of LL
print("Measuring LL for Re(HV)")
CLLHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LL for Re(HV) = ", CLLHV, "\tNormalized to diagonal = ", CLLHV/normconstant)
print("Counts for LL for Re(HV) = ", CLLHV, "\tNormalized to diagonal = ", CLLHV/normconstant, file = outputFile)
resultdata.update({"CLLHV": CLLHV})

#measurement of AA
print("Measuring AA for Re(HV)")
CAAHV= measure(rot1Angle180, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(HV) = ", CAAHV, "\tNormalized to diagonal = ", CAAHV/normconstant)
print("Counts for AA for Re(HV) = ", CAAHV, "\tNormalized to diagonal = ", CAAHV/normconstant, file = outputFile)
resultdata.update({"CAAHV": CAAHV})

#measurement of DA
print("Measuring DA for Re(HV)")
CDAHV= measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(HV) = ", CDAHV, "\tNormalized to diagonal = ", CDAHV/normconstant)
print("Counts for DA for Re(HV) = ", CDAHV, "\tNormalized to diagonal = ", CDAHV/normconstant, file = outputFile)
resultdata.update({"CDAHV": CDAHV})

                
#measurement of Im(HV)
#input("Please unblock all paths, then press enter")
#measurement of RA
print("Measuring RA for Im(HV)")
CRAHV= measure(rot1Angle270, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for RA for Im(HV) = ", CRAHV, "\tNormalized to diagonal = ", CRAHV/normconstant)
print("Counts for RA for Im(HV) = ", CRAHV, "\tNormalized to diagonal = ", CRAHV/normconstant, file = outputFile)
resultdata.update({"CRAHV": CRAHV})

#measurement of LA
print("Measuring LA for Im(HV)")
CLAHV= measure(rot1Angle90, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for LA for Im(HV) = ", CLAHV, "\tNormalized to diagonal = ", CLAHV/normconstant)
print("Counts for LA for Im(HV) = ", CLAHV, "\tNormalized to diagonal = ", CLAHV/normconstant, file = outputFile)
resultdata.update({"CLAHV": CLAHV})

#measurement of LD
print("Measuring LD for Im(HV)")
CLDHV= measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LD for Im(HV) = ", CLDHV, "\tNormalized to diagonal = ", CLDHV/normconstant)
print("Counts for LD for Im(HV) = ", CLDHV, "\tNormalized to diagonal = ", CLDHV/normconstant, file = outputFile)
resultdata.update({"CLDHV": CLDHV})

#measurement of AR
print("Measuring AR for Im(HV)")
CARHV= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(HV) = ", CARHV, "\tNormalized to diagonal = ", CARHV/normconstant)
print("Counts for AR for Im(HV) = ", CARHV, "\tNormalized to diagonal = ", CARHV/normconstant, file = outputFile)
resultdata.update({"CARHV": CARHV})

#measurement of AL
print("Measuring AL for Im(HV)")
CALHV = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(HV) = ", CALHV, "\tNormalized to diagonal = ", CALHV/normconstant)
print("Counts for AL for Im(HV) = ", CALHV, "\tNormalized to diagonal = ", CALHV/normconstant, file = outputFile)
resultdata.update({"CALHV": CALHV})

#measurement of DL
print("Measuring DL for Im(HV)")
CDLHV= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(HV) = ", CDLHV, "\tNormalized to diagonal = ", CDLHV/normconstant)
print("Counts for DL for Im(HV) = ", CDLHV, "\tNormalized to diagonal = ", CDLHV/normconstant, file = outputFile)
resultdata.update({"CDLHV": CDLHV})

#measurement of DR
print("Measuring DR for Im(HV)")
CDRHV= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(HV) = ", CDRHV, "\tNormalized to diagonal = ", CDRHV/normconstant)
print("Counts for DR for Im(HV) = ", CDRHV, "\tNormalized to diagonal = ", CDRHV/normconstant, file = outputFile)
resultdata.update({"CDRHV": CDRHV})

#measurement of RD
print("Measuring RD for Im(HV)")
CRDHV= measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RD for Im(HV) = ", CRDHV, "\tNormalized to diagonal = ", CRDHV/normconstant)
print("Counts for RD for Im(HV) = ", CRDHV, "\tNormalized to diagonal = ", CRDHV/normconstant, file = outputFile)
resultdata.update({"CRDHV": CRDHV})

            
#measurement of Re(VH)
#input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(VH)")
CDDVH= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(VH) = ", CDDVH, "\tNormalized to diagonal = ", CDDVH/normconstant)
print("Counts for DD for Re(VH) = ", CDDVH, "\tNormalized to diagonal = ", CDDVH/normconstant, file = outputFile)
resultdata.update({"CDDVH": CDDVH})

#measurement of RL
print("Measuring RL for Re(VH)")
CRLVH= measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RL for Re(VH) = ", CRLVH, "\tNormalized to diagonal = ", CRLVH/normconstant)
print("Counts for RL for Re(VH) = ", CRLVH, "\tNormalized to diagonal = ", CRLVH/normconstant, file = outputFile)
resultdata.update({"CRLVH": CRLVH})

#measurement of RR
print("Measuring RR for Re(VH)")
CRRVH= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for RR for Re(VH) = ", CRRVH, "\tNormalized to diagonal = ", CRRVH/normconstant)
print("Counts for RR for Re(VH) = ", CRRVH, "\tNormalized to diagonal = ", CRRVH/normconstant, file = outputFile)
resultdata.update({"CRRVH": CRRVH})

#measurement of AD
print("Measuring AD for Re(VH)")
CADVH= measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(VH) = ", CADVH, "\tNormalized to diagonal = ", CADVH/normconstant)
print("Counts for AD for Re(VH) = ", CADVH, "\tNormalized to diagonal = ", CADVH/normconstant, file = outputFile)
resultdata.update({"CADVH": CADVH})

#measurement of LR
print("Measuring LR for Re(VH)")
CLRVH= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for LR for Re(VH) = ", CLRVH, "\tNormalized to diagonal = ", CLRVH/normconstant)
print("Counts for LR for Re(VH) = ", CLRVH, "\tNormalized to diagonal = ", CLRVH/normconstant, file = outputFile)
resultdata.update({"CLRVH": CLRVH})

#measurement of LL
print("Measuring LL for Re(VH)")
CLLVH = measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for LL for Re(VH) = ", CLLVH, "\tNormalized to diagonal = ", CLLVH/normconstant)
print("Counts for LL for Re(VH) = ", CLLVH, "\tNormalized to diagonal = ", CLLVH/normconstant, file = outputFile)
resultdata.update({"CLLVH": CLLVH})

#measurement of AA
print("Measuring AA for Re(VH)")
CAAVH= measure(rot1Angle180, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(VH) = ", CAAVH, "\tNormalized to diagonal = ", CAAVH/normconstant)
print("Counts for AA for Re(VH) = ", CAAVH, "\tNormalized to diagonal = ", CAAVH/normconstant, file = outputFile)
resultdata.update({"CAAVH": CAAVH})

#measurement of DA
print("Measuring DA for Re(VH)")
CDAVH= measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(VH) = ", CDAVH, "\tNormalized to diagonal = ", CDAVH/normconstant)
print("Counts for DA for Re(VH) = ", CDAVH, "\tNormalized to diagonal = ", CDAVH/normconstant, file = outputFile)
resultdata.update({"CDAVH": CDAVH})


#measurement of Im(VH)
#input("Please unblock all paths, then press enter")
#measurement of RA
print("Measuring RA for Im(VH)")
CRAVH= measure(rot1Angle90, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for RA for Im(VH) = ", CRAVH, "\tNormalized to diagonal = ", CRAVH/normconstant)
print("Counts for RA for Im(VH) = ", CRAVH, "\tNormalized to diagonal = ", CRAVH/normconstant, file = outputFile)
resultdata.update({"CRAVH": CRAVH})

#measurement of LA
print("Measuring LA for Im(VH)")
CLAVH= measure(rot1Angle270, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for LA for Im(VH) = ", CLAVH, "\tNormalized to diagonal = ", CLAVH/normconstant)
print("Counts for LA for Im(VH) = ", CLAVH, "\tNormalized to diagonal = ", CLAVH/normconstant, file = outputFile)
resultdata.update({"CLAVH": CLAVH})

#measurement of LD
print("Measuring LD for Im(VH)")
CLDVH= measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LD for Im(VH) = ", CLDVH, "\tNormalized to diagonal = ", CLDVH/normconstant)
print("Counts for LD for Im(VH) = ", CLDVH, "\tNormalized to diagonal = ", CLDVH/normconstant, file = outputFile)
resultdata.update({"CLDVH": CLDVH})

#measurement of AR
print("Measuring AR for Im(VH)")
CARVH= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(VH) = ", CARVH, "\tNormalized to diagonal = ", CARVH/normconstant)
print("Counts for AR for Im(VH) = ", CARVH, "\tNormalized to diagonal = ", CARVH/normconstant, file = outputFile)
resultdata.update({"CARVH": CARVH})

#measurement of AL
print("Measuring AL for Im(VH)")
CALVH = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(VH) = ", CALVH, "\tNormalized to diagonal = ", CALVH/normconstant)
print("Counts for AL for Im(VH) = ", CALVH, "\tNormalized to diagonal = ", CALVH/normconstant, file = outputFile)
resultdata.update({"CALVH": CALVH})

#measurement of DL
print("Measuring DL for Im(VH)")
CDLVH= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(VH) = ", CDLVH, "\tNormalized to diagonal = ", CDLVH/normconstant)
print("Counts for DL for Im(VH) = ", CDLVH, "\tNormalized to diagonal = ", CDLVH/normconstant, file = outputFile)
resultdata.update({"CDLVH": CDLVH})

#measurement of DR
print("Measuring DR for Im(VH)")
CDRVH= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(VH) = ", CDRVH, "\tNormalized to diagonal = ", CDRVH/normconstant)
print("Counts for DR for Im(VH) = ", CDRVH, "\tNormalized to diagonal = ", CDRVH/normconstant, file = outputFile)
resultdata.update({"CDRVH": CDRVH})

#measurement of RD
print("Measuring RD for Im(VH)")
CRDVH= measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RD for Im(VH) = ", CRDVH, "\tNormalized to diagonal = ", CRDVH/normconstant)
print("Counts for RD for Im(VH) = ", CRDVH, "\tNormalized to diagonal = ", CRDVH/normconstant, file = outputFile)
resultdata.update({"CRDVH": CRDVH})

            
#measurement of Re(VV)
#input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(VV)")
CDDVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(VV) = ", CDDVV, "\tNormalized to diagonal = ", CDDVV/normconstant)
print("Counts for DD for Re(VV) = ", CDDVV, "\tNormalized to diagonal = ", CDDVV/normconstant, file = outputFile)
resultdata.update({"CDDVV": CDDVV})

#measurement of RL
print("Measuring RL for Re(VV)")
CRLVV= measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RL for Re(VV) = ", CRLVV, "\tNormalized to diagonal = ", CRLVV/normconstant)
print("Counts for RL for Re(VV) = ", CRLVV, "\tNormalized to diagonal = ", CRLVV/normconstant, file = outputFile)
resultdata.update({"CRLVV": CRLVV})

#measurement of RR
print("Measuring RR for Re(VV)")
CRRVV= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for RR for Re(VV) = ", CRRVV, "\tNormalized to diagonal = ", CRRVV/normconstant)
print("Counts for RR for Re(VV) = ", CRRVV, "\tNormalized to diagonal = ", CRRVV/normconstant, file = outputFile)
resultdata.update({"CRRVV": CRRVV})

#measurement of AD
print("Measuring AD for Re(VV)")
CADVV= measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(VV) = ", CADVV, "\tNormalized to diagonal = ", CADVV/normconstant)
print("Counts for AD for Re(VV) = ", CADVV, "\tNormalized to diagonal = ", CADVV/normconstant, file = outputFile)
resultdata.update({"CADVV": CADVV})

#measurement of LR
print("Measuring LR for Re(VV)")
CLRVV= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for LR for Re(VV) = ", CLRVV, "\tNormalized to diagonal = ", CLRVV/normconstant)
print("Counts for LR for Re(VV) = ", CLRVV, "\tNormalized to diagonal = ", CLRVV/normconstant, file = outputFile)
resultdata.update({"CLRVV": CLRVV})

#measurement of LL
print("Measuring LL for Re(VV)")
CLLVV = measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for LL for Re(VV) = ", CLLVV, "\tNormalized to diagonal = ", CLLVV/normconstant)
print("Counts for LL for Re(VV) = ", CLLVV, "\tNormalized to diagonal = ", CLLVV/normconstant, file = outputFile)
resultdata.update({"CLLVV": CLLVV})

#measurement of AA
print("Measuring AA for Re(VV)")
CAAVV= measure(rot1Angle180, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(VV) = ", CAAVV, "\tNormalized to diagonal = ", CAAVV/normconstant)
print("Counts for AA for Re(VV) = ", CAAVV, "\tNormalized to diagonal = ", CAAVV/normconstant, file = outputFile)
resultdata.update({"CAAVV": CAAVV})

#measurement of DA
print("Measuring DA for Re(VV)")
CDAVV= measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(VV) = ", CDAVV, "\tNormalized to diagonal = ", CDAVV/normconstant)
print("Counts for DA for Re(VV) = ", CDAVV, "\tNormalized to diagonal = ", CDAVV/normconstant, file = outputFile)
resultdata.update({"CDAVV": CDAVV})


#measurement of Im(VV)
#input("Please unblock all paths, then press enter")
#measurement of RA
print("Measuring RA for Im(VV)")
CRAVV= measure(rot1Angle90, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for RA for Im(VV) = ", CRAVV, "\tNormalized to diagonal = ", CRAVV/normconstant)
print("Counts for RA for Im(VV) = ", CRAVV, "\tNormalized to diagonal = ", CRAVV/normconstant, file = outputFile)
resultdata.update({"CRAVV": CRAVV})

#measurement of LA
print("Measuring LA for Im(VV)")
CLAVV= measure(rot1Angle270, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for LA for Im(VV) = ", CLAVV, "\tNormalized to diagonal = ", CLAVV/normconstant)
print("Counts for LA for Im(VV) = ", CLAVV, "\tNormalized to diagonal = ", CLAVV/normconstant, file = outputFile)
resultdata.update({"CLAVV": CLAVV})

#measurement of LD
print("Measuring LD for Im(VV)")
CLDVV= measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LD for Im(VV) = ", CLDVV, "\tNormalized to diagonal = ", CLDVV/normconstant)
print("Counts for LD for Im(VV) = ", CLDVV, "\tNormalized to diagonal = ", CLDVV/normconstant, file = outputFile)
resultdata.update({"CLDVV": CLDVV})

#measurement of AR
print("Measuring AR for Im(VV)")
CARVV= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(VV) = ", CARVV, "\tNormalized to diagonal = ", CARVV/normconstant)
print("Counts for AR for Im(VV) = ", CARVV, "\tNormalized to diagonal = ", CARVV/normconstant, file = outputFile)
resultdata.update({"CARVV": CARVV})

#measurement of AL
print("Measuring AL for Im(VV)")
CALVV = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(VV) = ", CALVV, "\tNormalized to diagonal = ", CALVV/normconstant)
print("Counts for AL for Im(VV) = ", CALVV, "\tNormalized to diagonal = ", CALVV/normconstant, file = outputFile)
resultdata.update({"CALVV": CALVV})

#measurement of DL
print("Measuring DL for Im(VV)")
CDLVV= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(VV) = ", CDLVV, "\tNormalized to diagonal = ", CDLVV/normconstant)
print("Counts for DL for Im(VV) = ", CDLVV, "\tNormalized to diagonal = ", CDLVV/normconstant, file = outputFile)
resultdata.update({"CDLVV": CDLVV})

#measurement of DR
print("Measuring DR for Im(VV)")
CDRVV= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(VV) = ", CDRVV, "\tNormalized to diagonal = ", CDRVV/normconstant)
print("Counts for DR for Im(VV) = ", CDRVV, "\tNormalized to diagonal = ", CDRVV/normconstant, file = outputFile)
resultdata.update({"CDRVV": CDRVV})

#measurement of RD
print("Measuring RD for Im(VV)")
CRDVV= measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RD for Im(VV) = ", CRDVV, "\tNormalized to diagonal = ", CRDVV/normconstant)
print("Counts for RD for Im(VV) = ", CRDVV, "\tNormalized to diagonal = ", CRDVV/normconstant, file = outputFile)
resultdata.update({"CRDVV": CRDVV})

            
print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

#extraction of result
rerhoHH=0.5*((CDDHH-CDAHH-CADHH+CAAHH)-(CLLHH-CLRHH-CRLHH+CRRHH)+2*(CDVHH-CAVHH)+2*(CVDHH-CVAHH)+4*CVVHH)/normconstant
rerhoHHTekk= 0.5*((CDDHH-CDAHH-CADHH+CAAHH)-(CLLHH-CLRHH-CRLHH+CRRHH))/normconstant
rerhoHHCorrection = rerhoHH-rerhoHHTekk

imrhoHH=0.5*((CLDHH-CLAHH-CRDHH+CRAHH)+(CDLHH-CDRHH-CALHH+CARHH)+2*(CLVHH-CRVHH))/normconstant
imrhoHHTekk=0.5*((CLDHH-CLAHH-CRDHH+CRAHH)+(CDLHH-CDRHH-CALHH+CARHH))/normconstant
imrhoHHCorrection=imrhoHH-imrhoHHTekk 

rerhoHV=0.5*((CDDHV-CDAHV-CADHV+CAAHV)-(CLLHV-CLRHV-CRLHV+CRRHV)+2*(CDVHV-CAVHV)+2*(CVDHV-CVAHV)+4*CVVHV)/normconstant
rerhoHVTekk=0.5*((CDDHV-CDAHV-CADHV+CAAHV)-(CLLHV-CLRHV-CRLHV+CRRHV))/normconstant
rerhoHVCorrection=rerhoHV-rerhoHVTekk

imrhoHV=0.5*((CLDHV-CLAHV-CRDHV+CRAHV)+(CDLHV-CDRHV-CALHV+CARHV)+2*(CLVHV-CRVHV))/normconstant
imrhoHVTekk=0.5*((CLDHV-CLAHV-CRDHV+CRAHV)+(CDLHV-CDRHV-CALHV+CARHV))/normconstant    
imrhoHVCorrection = imrhoHV-imrhoHVTekk

rerhoVH=0.5*((CDDVH-CDAVH-CADVH+CAAVH)-(CLLVH-CLRVH-CRLVH+CRRVH)+2*(CDVVH-CAVVH)+2*(CVDVH-CVAVH)+4*CVVVH)/normconstant
rerhoVHTekk=0.5*((CDDVH-CDAVH-CADVH+CAAVH)-(CLLVH-CLRVH-CRLVH+CRRVH))/normconstant
rerhoVHCorrection = rerhoVH-rerhoVHTekk

imrhoVH=0.5*((CLDVH-CLAVH-CRDVH+CRAVH)+(CDLVH-CDRVH-CALVH+CARVH)+2*(CLVVH-CRVVH))/normconstant
imrhoVHTekk=0.5*((CLDVH-CLAVH-CRDVH+CRAVH)+(CDLVH-CDRVH-CALVH+CARVH))/normconstant           
imrhoVHCorrection=imrhoVH-imrhoVHTekk

rerhoVV=0.5*((CDDVV-CDAVV-CADVV+CAAVV)-(CLLVV-CLRVV-CRLVV+CRRVV)+2*(CDVVV-CAVVV)+2*(CVDVV-CVAVV)+4*CVVVV)/normconstant
rerhoVVTekk=0.5*((CDDVV-CDAVV-CADVV+CAAVV)-(CLLVV-CLRVV-CRLVV+CRRVV))/normconstant
rerhoVVCorrection = rerhoVV-rerhoVVTekk

imrhoVV=0.5*((CLDVV-CLAVV-CRDVV+CRAVV)+(CDLVV-CDRVV-CALVV+CARVV)+2*(CLVVV-CRVVV))/normconstant
imrhoVVTekk=0.5*((CLDVV-CLAVV-CRDVV+CRAVV)+(CDLVV-CDRVV-CALVV+CARVV))/normconstant  
imrhoVVCorrection = imrhoVV-imrhoVVTekk

result=qutip.Qobj([[rerhoHH+imrhoHH*1j , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rerhoVV+imrhoVV*1j]])
resquad=result**2
purity= resquad.tr()
resultTekk=qutip.Qobj([[rerhoHHTekk+imrhoHHTekk*1j , rerhoHVTekk+imrhoHVTekk*1j],[rerhoVHTekk+imrhoVHTekk*1j, rerhoVVTekk+imrhoVVTekk*1j]])
resquadTekk=result**2
purityTekk= resquad.tr()
resultCorrection=qutip.Qobj([[rerhoHHCorrection+imrhoHHCorrection*1j , rerhoHVCorrection+imrhoHVCorrection*1j],[rerhoVHCorrection+imrhoVHCorrection*1j, rerhoVVCorrection+imrhoVVCorrection*1j]])

#save qobjs
qutip.qsave([result, resquad, resultTekk, resquadTekk, resultCorrection], outputfilename[:-4])

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)

#output of final results
print("Final result")
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)
print("ResultTekk = ", resultTekk)
print("ResquadTekk = ", resquadTekk)
print("Purity (as trace of resquad) = ", purityTekk)
print("Correction = ", resultCorrection)

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