# -*- coding: utf-8 -*-
"""
Created on Sun May 28 22:48:25 2017

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

outputfilename+="All"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for All protocols", file = outputFile)

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
input("Please block H, D paths, unblock all others, then press Enter")
print("Measuring VVA")
VVA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVA = ", VVA)
print("Counts for VVA = ", VVA, file = outputFile)
resultdata.update({"VVARaw": VVA})
VVA*=4
resultdata.update({"VVA": VVA})

input("Please block V, D paths, unblock all others, then press Enter")
print("Measuring VHA")
VHA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for VHA = ", VHA)
print("Counts for VHA = ", VHA, file = outputFile)
resultdata.update({"VHARaw": VHA})
VHA*=4
resultdata.update({"VHA": VHA})

input("Please block V, A paths, unblock all others, then press Enter")
print("Measuring VHD")
VHD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for VHD = ", VHD)
print("Counts for VHD = ", VHD, file = outputFile)
resultdata.update({"VHDRaw": VHD})
VHD*=4
resultdata.update({"VHD": VHD})

print("Measuring VVHV")
VVHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVHV = ", VVHV)
print("Counts for VVHV = ", VVHV, file = outputFile)
resultdata.update({"VVHVRaw": VVHV})
VVHV*=4
resultdata.update({"VVHV": VVHV})

print("Measuring VVHH")
VVHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVHH = ", VVHH)
print("Counts for VVHH = ", VVHH, file = outputFile)
resultdata.update({"VVHHRaw": VVHH})
VVHH*=4
resultdata.update({"VVHH": VVHH})

input("Please block V path, unblock all others, then press Enter")
print("Measuring VDHH")
VDHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VDHH = ", VDHH)
print("Counts for VDHH = ", VDHH, file = outputFile)
resultdata.update({"VDHH": VDHH})
VDHH*=2
resultdata.update({"VDHH": VDHH})

print("Measuring VAHV")
VAHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VAHV = ", VAHV)
print("Counts for VAHV = ", VAHV, file = outputFile)
resultdata.update({"VAHV": VAHV})
VAHV*=2
resultdata.update({"VAHV": VAHV})

print("Measuring VAHH")
VAHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VAHH = ", VAHH)
print("Counts for VAHH = ", VAHH, file = outputFile)
resultdata.update({"VAHH": VAHH})
VAHH*=2
resultdata.update({"VAHH": VAHH})

print("Measuring VDHV")
VDHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VDHV = ", VDHV)
print("Counts for VDHV = ", VDHV, file = outputFile)
resultdata.update({"VDHV": VDHV})
VDHV*=2
resultdata.update({"VDHV": VDHV})

input("Please block H, A paths, unblock all others, then press Enter")
print("Measuring VVD")
VVD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVD = ", VVD)
print("Counts for VVD = ", VVD, file = outputFile)
resultdata.update({"VVDRaw": VVD})
VVD*=4
resultdata.update({"VVD": VVD})

print("Measuring VVVH")
VVVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVVH = ", VVVH)
print("Counts for VVVH = ", VVVH, file = outputFile)
resultdata.update({"VVVHRaw": VVVH})
VVVH*=4
resultdata.update({"VVVH": VVVH})

print("Measuring VVVV")
VVVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VVVV = ", VVVV)
print("Counts for VVVV = ", VVVV, file = outputFile)
resultdata.update({"VVVVRaw": VVVV})
VVVV*=4
resultdata.update({"VVVV": VVVV})

input("Please block H path, unblock all others, then press Enter")
print("Measuring VDVV")
VDVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VDVV = ", VDVV)
print("Counts for VDVV = ", VDVV, file = outputFile)
resultdata.update({"VDVVRaw": VDVV})
VDVV*=2
resultdata.update({"VDVV": VDVV})

print("Measuring VAVH")
VAVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VAVH = ", VAVH)
print("Counts for VAVH = ", VAVH, file = outputFile)
resultdata.update({"VAVHRaw": VAVH})
VAVH*=2
resultdata.update({"VAVH": VAVH})

print("Measuring VAVV")
VAVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VAVV = ", VAVV)
print("Counts for VAVV = ", VAVV, file = outputFile)
resultdata.update({"VAVVRaw": VAVV})
VAVV*=2
resultdata.update({"VAVV": VAVV})

print("Measuring VDVH")
VDVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VDVH = ", VDVH)
print("Counts for VDVH = ", VDVH, file = outputFile)
resultdata.update({"VDVHRaw": VDVH})
VDVH*=2
resultdata.update({"VDVH": VDVH})

input("Please block D path, unblock all others, then press Enter")
print("Measuring AVHV")
AVHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVHV = ", AVHV)
print("Counts for AVHV = ", AVHV, file = outputFile)
resultdata.update({"AVHVRaw": AVHV})
AVHV*=2
resultdata.update({"AVHV": AVHV})

print("Measuring AVVV")
AVVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVVV = ", AVVV)
print("Counts for AVVV = ", AVVV, file = outputFile)
resultdata.update({"AVVVRaw": AVVV})
AVVV*=2
resultdata.update({"AVVV": AVVV})

print("Measuring RVHV")
RVHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVHV = ", RVHV)
print("Counts for RVHV = ", RVHV, file = outputFile)
resultdata.update({"RVHVRaw": RVHV})
RVHV*=2
resultdata.update({"RVHV": RVHV})

print("Measuring LVVV")
LVVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVVV = ", LVVV)
print("Counts for LVVV = ", LVVV, file = outputFile)
resultdata.update({"LVVVRaw": LVVV})
LVVV*=2
resultdata.update({"LVVV": LVVV})

print("Measuring RVHH")
RVHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVHH = ", RVHH)
print("Counts for RVHH = ", RVHH, file = outputFile)
resultdata.update({"RVHHRaw": RVHH})
RVHH*=2
resultdata.update({"RVHH": RVHH})

print("Measuring LVVH")
LVVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVVH = ", LVVH)
print("Counts for LVVH = ", LVVH, file = outputFile)
resultdata.update({"LVVHRaw": LVVH})
LVVH*=2
resultdata.update({"LVVH": LVVH})

print("Measuring AVHH")
AVHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVHH = ", AVHH)
print("Counts for AVHH = ", AVHH, file = outputFile)
resultdata.update({"AVHHRaw": AVHH})
AVHH*=2
resultdata.update({"AVHH": AVHH})

print("Measuring AVVH")
AVVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVVH = ", AVVH)
print("Counts for AVVH = ", AVVH, file = outputFile)
resultdata.update({"AVVHRaw": AVVH})
AVVH*=2
resultdata.update({"AVVH": AVVH})

print("Measuring AHD")
AHD = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for AHD = ", AHD)
print("Counts for AHD = ", AHD, file = outputFile)
resultdata.update({"AHDRaw": AHD})
AHD*=2
resultdata.update({"AHD": AHD})

print("Measuring AVD")
AVD = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVD = ", AVD)
print("Counts for AVD = ", AVD, file = outputFile)
resultdata.update({"AVDRaw": AVD})
AVD*=2
resultdata.update({"AVD": AVD})

print("Measuring DHA")
DHA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for DHA = ", DHA)
print("Counts for DHA = ", DHA, file = outputFile)
resultdata.update({"DHARaw": DHA})
DHA*=2
resultdata.update({"DHA": DHA})

print("Measuring DVA")
DVA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVA = ", DVA)
print("Counts for DVA = ", DVA, file = outputFile)
resultdata.update({"DVARaw": DVA})
DVA*=2
resultdata.update({"DVA": DVA})

print("Measuring RHD")
RHD = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for RHD = ", RHD)
print("Counts for RHD = ", RHD, file = outputFile)
resultdata.update({"RHDRaw": RHD})
RHD*=2
resultdata.update({"RHD": RHD})

print("Measuring LVD")
LVD = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVD = ", LVD)
print("Counts for LVD = ", LVD, file = outputFile)
resultdata.update({"LVDRaw": LVD})
LVD*=2
resultdata.update({"LVD": LVD})

print("Measuring LHA")
LHA = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for LHA = ", LHA)
print("Counts for LHA = ", LHA, file = outputFile)
resultdata.update({"LHARaw": LHA})
LHA*=2
resultdata.update({"LHA": LHA})

print("Measuring RVA")
RVA = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVA = ", RVA)
print("Counts for RVA = ", RVA, file = outputFile)
resultdata.update({"RVARaw": RVA})
RVA*=2
resultdata.update({"RVA": RVA})

input("Please block A path, unblock all others, then press Enter")
print("Measuring RHA")
RHA = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for RHA = ", RHA)
print("Counts for RHA = ", RHA, file = outputFile)
resultdata.update({"RHARaw": RHA})
RHA*=2
resultdata.update({"RHA": RHA})

print("Measuring LVA")
LVA = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVA = ", LVA)
print("Counts for LVA = ", LVA, file = outputFile)
resultdata.update({"LVARaw": LVA})
LVA*=2
resultdata.update({"LVA": LVA})

print("Measuring LHD")
LHD = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for LHD = ", LHD)
print("Counts for LHD = ", LHD, file = outputFile)
resultdata.update({"LHDRaw": LHD})
LHD*=2
resultdata.update({"LHD": LHD})

print("Measuring RVD")
RVD = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVD = ", RVD)
print("Counts for RVD = ", RVD, file = outputFile)
resultdata.update({"RVDRaw": RVD})
RVD*=2
resultdata.update({"RVD": RVD})

print("Measuring AHA")
AHA = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for AHA = ", AHA)
print("Counts for AHA = ", AHA, file = outputFile)
resultdata.update({"AHARaw": AHA})
AHA*=2
resultdata.update({"AHA": AHA})

print("Measuring AVA")
AVA = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for AVA = ", AVA)
print("Counts for AVA = ", AVA, file = outputFile)
resultdata.update({"AVARaw": AVA})
AVA*=2
resultdata.update({"AVA": AVA})

print("Measuring DHD")
DHD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for DHD = ", DHD)
print("Counts for DHD = ", DHD, file = outputFile)
resultdata.update({"DHDRaw": DHD})
DHD*=2
resultdata.update({"DHD": DHD})

print("Measuring DVD")
DVD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVD = ", DVD)
print("Counts for DVD = ", DVD, file = outputFile)
resultdata.update({"DVDRaw": DVD})
DVD*=2
resultdata.update({"DVD": DVD})

print("Measuring DVHH")
DVHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVHH = ", DVHH)
print("Counts for DVHH = ", DVHH, file = outputFile)
resultdata.update({"DVHHRaw": DVHH})
DVHH*=2
resultdata.update({"DVHH": DVHH})

print("Measuring DVVH")
DVVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVVH = ", DVVH)
print("Counts for DVVH = ", DVVH, file = outputFile)
resultdata.update({"DVVHRaw": DVVH})
DVVH*=2
resultdata.update({"DVVH": DVVH})

print("Measuring LVHH")
LVHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVHH = ", LVHH)
print("Counts for LVHH = ", LVHH, file = outputFile)
resultdata.update({"LVHHRaw": LVHH})
LVHH*=2
resultdata.update({"LVHH": LVHH})

print("Measuring RVVH")
RVVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVVH = ", RVVH)
print("Counts for RVVH = ", RVVH, file = outputFile)
resultdata.update({"RVVHRaw": RVVH})
RVVH*=2
resultdata.update({"RVVH": RVVH})

print("Measuring LVHV")
LVHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LVHV = ", LVHV)
print("Counts for LVHV = ", LVHV, file = outputFile)
resultdata.update({"LVHVRaw": LVHV})
LVHV*=2
resultdata.update({"LVHV": LVHV})

print("Measuring RVVV")
RVVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RVVV = ", RVVV)
print("Counts for RVVV = ", RVVV, file = outputFile)
resultdata.update({"RVVVRaw": RVVV})
RVVV*=2
resultdata.update({"RVVV": RVVV})

print("Measuring DVHV")
DVHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVHV = ", DVHV)
print("Counts for DVHV = ", DVHV, file = outputFile)
resultdata.update({"DVHVRaw": DVHV})
DVHV*=2
resultdata.update({"DVHV": DVHV})

print("Measuring DVVV")
DVVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DVVV = ", DVVV)
print("Counts for DVVV = ", DVVV, file = outputFile)
resultdata.update({"DVVVRaw": DVVV})
DVVV*=2
resultdata.update({"DVVV": DVVV})

input("Please unblock all paths, then press Enter")
print("Measuring QSTH")
QSTH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for QSTH = ", QSTH)
print("Counts for QSTH = ", QSTH, file = outputFile)
resultdata.update({"QSTHRaw": QSTH})
QSTH*=4
resultdata.update({"QSTH": QSTH})

print("Measuring QSTV")
QSTV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for QSTV = ", QSTV)
print("Counts for QSTV = ", QSTV, file = outputFile)
resultdata.update({"QSTVRaw": QSTV})
QSTV*=4
resultdata.update({"QSTV": QSTV})

print("Measuring QSTR")
QSTR = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for QSTR = ", QSTR)
print("Counts for QSTR = ", QSTR, file = outputFile)
resultdata.update({"QSTRRaw": QSTR})
QSTR*=4
resultdata.update({"QSTR": QSTR})

print("Measuring QSTD")
QSTD = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Counts for QSTD = ", QSTD)
print("Counts for QSTD = ", QSTD, file = outputFile)
resultdata.update({"QSTDRaw": QSTD})
QSTD*=4
resultdata.update({"QSTD": QSTD})

print("Measuring AAHH")
AAHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AAHH = ", AAHH)
print("Counts for AAHH = ", AAHH, file = outputFile)
resultdata.update({"AAHH": AAHH})

print("Measuring AAVH")
AAVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AAVH = ", AAVH)
print("Counts for AAVH = ", AAVH, file = outputFile)
resultdata.update({"AAVH": AAVH})

print("Measuring ADHV")
ADHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for ADHV = ", ADHV)
print("Counts for ADHV = ", ADHV, file = outputFile)
resultdata.update({"ADHV": ADHV})

print("Measuring ADVV")
ADVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for ADVV = ", ADVV)
print("Counts for ADVV = ", ADVV, file = outputFile)
resultdata.update({"ADVV": ADVV})

print("Measuring DDHV")
DDHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DDHV = ", DDHV)
print("Counts for DDHV = ", DDHV, file = outputFile)
resultdata.update({"DDHV": DDHV})

print("Measuring DDVV")
DDVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DDVV = ", DDVV)
print("Counts for DDVV = ", DDVV, file = outputFile)
resultdata.update({"DDVV": DDVV})

print("Measuring DAHH")
DAHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DAHH = ", DAHH)
print("Counts for DAHH = ", DAHH, file = outputFile)
resultdata.update({"DAHH": DAHH})

print("Measuring DAVH")
DAVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DAVH = ", DAVH)
print("Counts for DAVH = ", DAVH, file = outputFile)
resultdata.update({"DAVH": DAVH})

print("Measuring LAHH")
LAHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LAHH = ", LAHH)
print("Counts for LAHH = ", LAHH, file = outputFile)
resultdata.update({"LAHH": LAHH})

print("Measuring RAVH")
RAVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RAVH = ", RAVH)
print("Counts for RAVH = ", RAVH, file = outputFile)
resultdata.update({"RAVH": RAVH})

print("Measuring LDHV")
LDHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LDHV = ", LDHV)
print("Counts for LDHV = ", LDHV, file = outputFile)
resultdata.update({"LDHV": LDHV})

print("Measuring RDVV")
RDVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RDVV = ", RDVV)
print("Counts for RDVV = ", RDVV, file = outputFile)
resultdata.update({"RDVV": RDVV})

print("Measuring RAHH")
RAHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RAHH = ", RAHH)
print("Counts for RAHH = ", RAHH, file = outputFile)
resultdata.update({"RAHH": RAHH})

print("Measuring LAVH")
LAVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LAVH = ", LAVH)
print("Counts for LAVH = ", LAVH, file = outputFile)
resultdata.update({"LAVH": LAVH})

print("Measuring RDHV")
RDHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RDHV = ", RDHV)
print("Counts for RDHV = ", RDHV, file = outputFile)
resultdata.update({"RDHV": RDHV})

print("Measuring LDVV")
LDVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LDVV = ", LDVV)
print("Counts for LDVV = ", LDVV, file = outputFile)
resultdata.update({"LDVV": LDVV})

print("Measuring RLHH")
RLHH = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RLHH = ", RLHH)
print("Counts for RLHH = ", RLHH, file = outputFile)
resultdata.update({"RLHH": RLHH})

print("Measuring LLVH")
LLVH = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LLVH = ", LLVH)
print("Counts for LLVH = ", LLVH, file = outputFile)
resultdata.update({"LLVH": LLVH})

print("Measuring RRHV")
RRHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RRHV = ", RRHV)
print("Counts for RRHV = ", RRHV, file = outputFile)
resultdata.update({"RRHV": RRHV})

print("Measuring LRVV")
LRVV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LRVV = ", LRVV)
print("Counts for LRVV = ", LRVV, file = outputFile)
resultdata.update({"LRVV": LRVV})

print("Measuring LRHH")
LRHH = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LRHH = ", LRHH)
print("Counts for LRHH = ", LRHH, file = outputFile)
resultdata.update({"LRHH": LRHH})

print("Measuring RRVH")
RRVH = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RRVH = ", RRVH)
print("Counts for RRVH = ", RRVH, file = outputFile)
resultdata.update({"RRVH": RRVH})

print("Measuring LLHV")
LLHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LLHV = ", LLHV)
print("Counts for LLHV = ", LLHV, file = outputFile)
resultdata.update({"LLHV": LLHV})

print("Measuring RLVV")
RLVV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RLVV = ", RLVV)
print("Counts for RLVV = ", RLVV, file = outputFile)
resultdata.update({"RLVV": RLVV})

print("Measuring ALHH")
ALHH = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ALHH = ", ALHH)
print("Counts for ALHH = ", ALHH, file = outputFile)
resultdata.update({"ALHH": ALHH})

print("Measuring ALVH")
ALVH = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ALVH = ", ALVH)
print("Counts for ALVH = ", ALVH, file = outputFile)
resultdata.update({"ALVH": ALVH})

print("Measuring ARHV")
ARHV = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ARHV = ", ARHV)
print("Counts for ARHV = ", ARHV, file = outputFile)
resultdata.update({"ARHV": ARHV})

print("Measuring ARVV")
ARVV = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ARVV = ", ARVV)
print("Counts for ARVV = ", ARVV, file = outputFile)
resultdata.update({"ARVV": ARVV})

print("Measuring DRHH")
DRHH = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DRHH = ", DRHH)
print("Counts for DRHH = ", DRHH, file = outputFile)
resultdata.update({"DRHH": DRHH})

print("Measuring DRVH")
DRVH = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DRVH = ", DRVH)
print("Counts for DRVH = ", DRVH, file = outputFile)
resultdata.update({"DRVH": DRVH})

print("Measuring DLHV")
DLHV = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DLHV = ", DLHV)
print("Counts for DLHV = ", DLHV, file = outputFile)
resultdata.update({"DLHV": DLHV})

print("Measuring DLVV")
DLVV = measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DLVV = ", DLVV)
print("Counts for DLVV = ", DLVV, file = outputFile)
resultdata.update({"DLVV": DLVV})

print("Measuring RRHH")
RRHH = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RRHH = ", RRHH)
print("Counts for RRHH = ", RRHH, file = outputFile)
resultdata.update({"RRHH": RRHH})

print("Measuring LRVH")
LRVH = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LRVH = ", LRVH)
print("Counts for LRVH = ", LRVH, file = outputFile)
resultdata.update({"LRVH": LRVH})

print("Measuring RLHV")
RLHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RLHV = ", RLHV)
print("Counts for RLHV = ", RLHV, file = outputFile)
resultdata.update({"RLHV": RLHV})

print("Measuring LLVV")
LLVV = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LLVV = ", LLVV)
print("Counts for LLVV = ", LLVV, file = outputFile)
resultdata.update({"LLVV": LLVV})

print("Measuring LLHH")
LLHH = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LLHH = ", LLHH)
print("Counts for LLHH = ", LLHH, file = outputFile)
resultdata.update({"LLHH": LLHH})

print("Measuring RLVH")
RLVH = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RLVH = ", RLVH)
print("Counts for RLVH = ", RLVH, file = outputFile)
resultdata.update({"RLVH": RLVH})

print("Measuring LRHV")
LRHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LRHV = ", LRHV)
print("Counts for LRHV = ", LRHV, file = outputFile)
resultdata.update({"LRHV": LRHV})

print("Measuring RRVV")
RRVV = measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RRVV = ", RRVV)
print("Counts for RRVV = ", RRVV, file = outputFile)
resultdata.update({"RRVV": RRVV})

print("Measuring DRHV")
DRHV = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DRHV = ", DRHV)
print("Counts for DRHV = ", DRHV, file = outputFile)
resultdata.update({"DRHV": DRHV})

print("Measuring DRVV")
DRVV = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DRVV = ", DRVV)
print("Counts for DRVV = ", DRVV, file = outputFile)
resultdata.update({"DRVV": DRVV})

print("Measuring ARHH")
ARHH = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ARHH = ", ARHH)
print("Counts for ARHH = ", ARHH, file = outputFile)
resultdata.update({"ARHH": ARHH})

print("Measuring ARVH")
ARVH = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ARVH = ", ARVH)
print("Counts for ARVH = ", ARVH, file = outputFile)
resultdata.update({"ARVH": ARVH})

print("Measuring ALHV")
ALHV = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ALHV = ", ALHV)
print("Counts for ALHV = ", ALHV, file = outputFile)
resultdata.update({"ALHV": ALHV})

print("Measuring ALVV")
ALVV = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for ALVV = ", ALVV)
print("Counts for ALVV = ", ALVV, file = outputFile)
resultdata.update({"ALVV": ALVV})

print("Measuring DLHH")
DLHH = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DLHH = ", DLHH)
print("Counts for DLHH = ", DLHH, file = outputFile)
resultdata.update({"DLHH": DLHH})

print("Measuring DLVH")
DLVH = measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DLVH = ", DLVH)
print("Counts for DLVH = ", DLVH, file = outputFile)
resultdata.update({"DLVH": DLVH})

print("Measuring AAHV")
AAHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AAHV = ", AAHV)
print("Counts for AAHV = ", AAHV, file = outputFile)
resultdata.update({"AAHV": AAHV})

print("Measuring AAVV")
AAVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for AAVV = ", AAVV)
print("Counts for AAVV = ", AAVV, file = outputFile)
resultdata.update({"AAVV": AAVV})

print("Measuring ADHH")
ADHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for ADHH = ", ADHH)
print("Counts for ADHH = ", ADHH, file = outputFile)
resultdata.update({"ADHH": ADHH})

print("Measuring ADVH")
ADVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for ADVH = ", ADVH)
print("Counts for ADVH = ", ADVH, file = outputFile)
resultdata.update({"ADVH": ADVH})

print("Measuring DDHH")
DDHH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DDHH = ", DDHH)
print("Counts for DDHH = ", DDHH, file = outputFile)
resultdata.update({"DDHH": DDHH})

print("Measuring DDVH")
DDVH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DDVH = ", DDVH)
print("Counts for DDVH = ", DDVH, file = outputFile)
resultdata.update({"DDVH": DDVH})

print("Measuring DAHV")
DAHV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DAHV = ", DAHV)
print("Counts for DAHV = ", DAHV, file = outputFile)
resultdata.update({"DAHV": DAHV})

print("Measuring DAVV")
DAVV = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DAVV = ", DAVV)
print("Counts for DAVV = ", DAVV, file = outputFile)
resultdata.update({"DAVV": DAVV})

print("Measuring RAHV")
RAHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RAHV = ", RAHV)
print("Counts for RAHV = ", RAHV, file = outputFile)
resultdata.update({"RAHV": RAHV})

print("Measuring LAVV")
LAVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LAVV = ", LAVV)
print("Counts for LAVV = ", LAVV, file = outputFile)
resultdata.update({"LAVV": LAVV})

print("Measuring RDHH")
RDHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RDHH = ", RDHH)
print("Counts for RDHH = ", RDHH, file = outputFile)
resultdata.update({"RDHH": RDHH})

print("Measuring LDVH")
LDVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LDVH = ", LDVH)
print("Counts for LDVH = ", LDVH, file = outputFile)
resultdata.update({"LDVH": LDVH})

print("Measuring LAHV")
LAHV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LAHV = ", LAHV)
print("Counts for LAHV = ", LAHV, file = outputFile)
resultdata.update({"LAHV": LAHV})

print("Measuring RAVV")
RAVV = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RAVV = ", RAVV)
print("Counts for RAVV = ", RAVV, file = outputFile)
resultdata.update({"RAVV": RAVV})

print("Measuring LDHH")
LDHH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LDHH = ", LDHH)
print("Counts for LDHH = ", LDHH, file = outputFile)
resultdata.update({"LDHH": LDHH})

print("Measuring RDVH")
RDVH = measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RDVH = ", RDVH)
print("Counts for RDVH = ", RDVH, file = outputFile)
resultdata.update({"RDVH": RDVH})

normconstant=QSTH+QSTV

rhoHHQST=QSTH/normconstant
rhoVVQST=QSTV/normconstant
rerhoHVQST=QSTD/normconstant-0.5
imrhoHVQST=QSTR/normconstant-0.5
rerhoVHQST=rerhoHVQST
imrhoVHQST=-imrhoHVQST

rawresultQST=qutip.Qobj([[rhoHHQST , rerhoHVQST+imrhoHVQST*1j],[rerhoVHQST+imrhoVHQST*1j, rhoVVQST]])
resultQST=qutip.Qobj([[rhoVVQST , -rerhoHVQST+imrhoHVQST*1j],[-rerhoVHQST+imrhoVHQST*1j, rhoHHQST]])

rho11HD=VHD/normconstant
rho10HD=0.5*(DHD-AHD+1.0j*(LHD-RHD))/normconstant
rho11HA=VHA/normconstant
rho10HA=0.5*(DHA-AHA+1.0j*(LHA-RHA))/normconstant
rho11VD=VVD/normconstant
rho10VD=0.5*(DVD-AVD+1.0j*(LVD-RVD))/normconstant
rho11VA=VVA/normconstant
rho10VA=0.5*(DVA-AVA+1.0j*(LVA-RVA))/normconstant

d=2
rhoHHDirac=d*rho11HA+rho10HA+rho10HD
rhoHVDirac=rho10HD-rho10HA
rhoVHDirac=rho10VD-rho10VA
rhoVVDirac=d*rho11VA+rho10VA+rho10VD
resultDirac=qutip.Qobj([[rhoHHDirac , rhoHVDirac],[rhoVHDirac, rhoVVDirac]])

rhoHHTwoAnc=4*VVHH/normconstant
rhoVVTwoAnc=4*VVVV/normconstant
rerhoHVTwoAnc=(RLHV+LRHV-RRHV-LLHV)/normconstant
imrhoHVTwoAnc=(DLHV-DRHV+ARHV-ALHV)/normconstant
rerhoVHTwoAnc=(RLVH+LRVH-RRVH-LLVH)/normconstant
imrhoVHTwoAnc=(DLVH-DRVH+ARVH-ALVH)/normconstant
resultTwoAnc=qutip.Qobj([[rhoHHTwoAnc , rerhoHVTwoAnc+imrhoHVTwoAnc*1j],[rerhoVHTwoAnc+imrhoVHTwoAnc*1j, rhoVVTwoAnc]])

rerhoHHTekkComplete=0.5*((DDHH-DAHH-ADHH+AAHH)-(LLHH-LRHH-RLHH+RRHH)+2*(DVHH-AVHH)+2*(VDHH-VAHH)+4*VVHH)/normconstant
imrhoHHTekkComplete=0.5*((LDHH-LAHH-RDHH+RAHH)+(DLHH-DRHH-ALHH+ARHH)+2*(LVHH-RVHH))/normconstant
rerhoHVTekkComplete=0.5*((DDHV-DAHV-ADHV+AAHV)-(LLHV-LRHV-RLHV+RRHV)+2*(DVHV-AVHV)+2*(VDHV-VAHV)+4*VVHV)/normconstant
imrhoHVTekkComplete=0.5*((LDHV-LAHV-RDHV+RAHV)+(DLHV-DRHV-ALHV+ARHV)+2*(LVHV-RVHV))/normconstant
rerhoVHTekkComplete=0.5*((DDVH-DAVH-ADVH+AAVH)-(LLVH-LRVH-RLVH+RRVH)+2*(DVVH-AVVH)+2*(VDVH-VAVH)+4*VVVH)/normconstant
imrhoVHTekkComplete=0.5*((LDVH-LAVH-RDVH+RAVH)+(DLVH-DRVH-ALVH+ARVH)+2*(LVVH-RVVH))/normconstant
rerhoVVTekkComplete=0.5*((DDVV-DAVV-ADVV+AAVV)-(LLVV-LRVV-RLVV+RRVV)+2*(DVVV-AVVV)+2*(VDVV-VAVV)+4*VVVV)/normconstant
imrhoVVTekkComplete=0.5*((LDVV-LAVV-RDVV+RAVV)+(DLVV-DRVV-ALVV+ARVV)+2*(LVVV-RVVV))/normconstant
rerhoHHTekk=0.5*((DDHH-DAHH-ADHH+AAHH)-(LLHH-LRHH-RLHH+RRHH))/normconstant
imrhoHHTekk=0.5*((LDHH-LAHH-RDHH+RAHH)+(DLHH-DRHH-ALHH+ARHH))/normconstant
rerhoHVTekk=0.5*((DDHV-DAHV-ADHV+AAHV)-(LLHV-LRHV-RLHV+RRHV))/normconstant
imrhoHVTekk=0.5*((LDHV-LAHV-RDHV+RAHV)+(DLHV-DRHV-ALHV+ARHV))/normconstant
rerhoVHTekk=0.5*((DDVH-DAVH-ADVH+AAVH)-(LLVH-LRVH-RLVH+RRVH))/normconstant
imrhoVHTekk=0.5*((LDVH-LAVH-RDVH+RAVH)+(DLVH-DRVH-ALVH+ARVH))/normconstant
rerhoVVTekk=0.5*((DDVV-DAVV-ADVV+AAVV)-(LLVV-LRVV-RLVV+RRVV))/normconstant
imrhoVVTekk=0.5*((LDVV-LAVV-RDVV+RAVV)+(DLVV-DRVV-ALVV+ARVV))/normconstant
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

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)
    
#output of final results
print("Final result")
print("resultQST = ", resultQST)
print("resultDirac = ", resultDirac)
print("resultTwoAnc = ", resultTwoAnc)
print("resultTekkComplete = ", resultTekkComplete)
print("resultTekk = ", resultTekk)
print("resultTekkCorrection = ", resultTekkCorrection)

print("Final result", file = outputFile)
print("resultQST = ", resultQST, file = outputFile)
print("resultDirac = ", resultDirac, file = outputFile)
print("resultTwoAnc = ", resultTwoAnc, file = outputFile)
print("resultTekkComplete = ", resultTekkComplete, file = outputFile)
print("resultTekk = ", resultTekk, file = outputFile)
print("resultTekkCorrection = ", resultTekkCorrection, file = outputFile)