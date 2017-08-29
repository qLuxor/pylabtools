# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 17:48:04 2017

@author: Giulio Foletto 2
"""

import sys
sys.path.append('..')
sys.path.append('../..')
import time
from ThorCon import ThorCon
import numpy as np
import instruments as ik
import qutip
import json

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

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

outputfilename+="DiracRedundant"
outputfilename+=".txt"
    
outputFile=open(outputfilename, "w")
print("Results for DiracRedundant protocol", file = outputFile)

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
rot1 = ThorCon(serial_number=rot1SN)
if home:
    rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = settings["rot2SN"]
rot2 = ThorCon(serial_number=rot2SN)
if home:
    rot2.home()

#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= settings["rotHWPSN"]
rotHWP = ThorCon(serial_number=rotHWPSN)
if home:
    rotHWP.home() #beware of bug in rotator

#ROTQWP configuration and initialization
print("Initializing ROTQWP")
rotQWPSN= settings["rotQWPSN"]
rotQWP = ThorCon(serial_number=rotQWPSN)
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
lcc2Voltage270=settings["lcc2Voltage270"]

#calibration values for ROTHWP
rotHWPAngle225=settings["rotHWPAngle225"]
rotHWPAngle675=settings["rotHWPAngle675"]

#calibration values for ROTQWP
rotQWPAngle0=settings["rotQWPAngle0"]
rotQWPAngle45=settings["rotQWPAngle45"]

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
        result= np.mean(singleMeasure)
    return result

resultdata={}
input("Please unblock all paths, then press Enter")
#measurement on D for normalization
print("Measuring D for normalization")
countDId = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CDRaw": countDId, "CD": 4*countDId})
print("Counts for D = ", countDId)
print("Counts for D = ", countDId, file = outputFile)

#Measurement on A for normalization
print("Measuring A for normalization")
countAId = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CARaw": countAId, "CA": 4*countAId})
print("Counts for A = ", countAId)
print("Counts for A = ", countAId, file = outputFile)

normconstant=4*(countDId+countAId)
resultdata.update({"NormConstant": normconstant})

#Measurement on srhoHD
input("Please block A path, unblock all others, then press Enter")
print("Measuring D for HD")
CDHD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CDHDRaw": CDHD})
print("Counts for D for HD = ", CDHD)
print("Counts for D for HD = ", CDHD, file = outputFile)
print("Measuring D for VD")
CDVD = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CDVDRaw": CDVD})
print("Counts for D for VD = ", CDVD)
print("Counts for D for VD = ", CDVD, file = outputFile)
print("Measuring A for HD")
CAHD = measure(rot1Angle180, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
resultdata.update({"CAHDRaw": CAHD})
print("Counts for A for HD = ", CAHD)
print("Counts for A for HD = ", CAHD, file = outputFile)
print("Measuring A for VD")
CAVD = measure(rot1Angle180, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
resultdata.update({"CAVDRaw": CAVD})
print("Counts for A for VD = ", CAVD)
print("Counts for A for VD = ", CAVD, file = outputFile)
print("Measuring L for HD")
CLHD = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
resultdata.update({"CLHDRaw": CLHD})
print("Counts for L for HD = ", CLHD)
print("Counts for L for HD = ", CLHD, file = outputFile)
print("Measuring R for VD")
CRVD = measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
resultdata.update({"CRVDRaw": CRVD})
print("Counts for R for VD = ", CRVD)
print("Counts for R for VD = ", CRVD, file = outputFile)
print("Measuring R for HD")
CRHD = measure(rot1Angle270, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)
resultdata.update({"CRHDRaw": CRHD})
print("Counts for R for HD = ", CRHD)
print("Counts for R for HD = ", CRHD, file = outputFile)
print("Measuring L for VD")
CLVD = measure(rot1Angle270, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)
resultdata.update({"CLVDRaw": CLVD})
print("Counts for L for VD = ", CLVD)
print("Counts for L for VD = ", CLVD, file = outputFile)

#to compensate for normconstant
CDHD = 2*CDHD
CAHD = 2*CAHD
CLHD = 2*CLHD
CRHD = 2*CRHD
CDVD = 2*CDVD
CAVD = 2*CAVD
CLVD = 2*CLVD
CRVD = 2*CRVD
resultdata.update({"CDHD": CDHD})
resultdata.update({"CAHD": CAHD})
resultdata.update({"CLHD": CLHD})
resultdata.update({"CRHD": CRHD})
resultdata.update({"CDVD": CDVD})
resultdata.update({"CAVD": CAVD})
resultdata.update({"CLVD": CLVD})
resultdata.update({"CRVD": CRVD})

#useful values
rho10HD = 0.5* (CDHD-CAHD+1.0j*(CLHD-CRHD))/normconstant
rho10VD = 0.5* (CDVD-CAVD+1.0j*(CLVD-CRVD))/normconstant

input("Please block H and A paths, unblock all others, then press Enter")
print("Measuring V for VD")
CVVD=measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CVVDRaw": CVVD})
print("Counts for V for VD = ", CVVD)
print("Counts for V for VD = ", CVVD, file = outputFile)

input("Please block V and A paths, unblock all others, then press Enter")
print("Measuring V for HD")
CVHD=measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CVHDRaw": CVHD})
print("Counts for V for HD = ", CVHD)
print("Counts for V for HD = ", CVHD, file = outputFile)

input("Please block V and D paths, unblock all others, then press Enter")
print("Measuring V for HA")
CVHA=measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CVHARaw": CVHA})
print("Counts for V for HA = ", CVHA)
print("Counts for V for HA = ", CVHA, file = outputFile)

input("Please block H and D paths, unblock all others, then press Enter")
print("Measuring V for VA")
CVVA=measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CVVARaw": CVVA})
print("Counts for V for VA = ", CVVA)
print("Counts for V for VA = ", CVVA, file = outputFile)


CVVD = 4*CVVD
CVHD = 4*CVHD
CVVA = 4*CVVA
CVHA = 4*CVHA
resultdata.update({"CVVD": CVVD})
resultdata.update({"CVHD": CVHD})
resultdata.update({"CVVA": CVVA})
resultdata.update({"CVHA": CVHA})

#useful values
rho11VD = CVVD/normconstant
rho11HD = CVHD/normconstant

#Measurement on srhoHA
input("Please block D path, unblock all others, then press Enter")
print("Measuring D for HA")
CDHA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CDHARaw": CDHA})
print("Counts for D for HA = ", CDHA)
print("Counts for D for HA = ", CDHA, file = outputFile)
print("Measuring D for VA")
CDVA = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CDVARaw": CDVA})
print("Counts for D for VA = ", CDVA)
print("Counts for D for VA = ", CDVA, file = outputFile)
print("Measuring A for HA")
CAHA = measure(rot1Angle180, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
resultdata.update({"CAHARaw": CAHA})
print("Counts for A for HA = ", CAHA)
print("Counts for A for HA = ", CAHA, file = outputFile)
print("Measuring A for VA")
CAVA = measure(rot1Angle180, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
resultdata.update({"CAVARaw": CAVA})
print("Counts for A for VA = ", CAVA)
print("Counts for A for VA = ", CAVA, file = outputFile)
print("Measuring L for HA")
CLHA = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
resultdata.update({"CLHARaw": CLHA})
print("Counts for L for HA = ", CLHA)
print("Counts for L for HA = ", CLHA, file = outputFile)
print("Measuring R for HA")
CRVA = measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
resultdata.update({"CRVARaw": CRVA})
print("Counts for R for VA = ", CRVA)
print("Counts for R for VA = ", CRVA, file = outputFile)
print("Measuring R for HA")
CRHA = measure(rot1Angle270, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)
resultdata.update({"CRHARaw": CRHA})
print("Counts for R for HA = ", CRHA)
print("Counts for R for HA = ", CRHA, file = outputFile)
print("Measuring L for VA")
CLVA = measure(rot1Angle270, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)
resultdata.update({"CLVARaw": CLVA})
print("Counts for L for VA = ", CLVA)
print("Counts for L for VA = ", CLVA, file = outputFile)

#to compensate for normconstant
CDHA=2*CDHA
CAHA=2*CAHA
CLHA=2*CLHA
CRHA=2*CRHA
CDVA=2*CDVA
CAVA=2*CAVA
CLVA=2*CLVA
CRVA=2*CRVA
resultdata.update({"CDHA": CDHA})
resultdata.update({"CAHA": CAHA})
resultdata.update({"CLHA": CLHA})
resultdata.update({"CRHA": CRHA})
resultdata.update({"CDVA": CDVA})
resultdata.update({"CAVA": CAVA})
resultdata.update({"CLVA": CLVA})
resultdata.update({"CRVA": CRVA})

#useful values
rho10HA = 0.5* (CDHA-CAHA+1.0j*(CLHA-CRHA))/normconstant
rho10VA = 0.5* (CDVA-CAVA+1.0j*(CLVA-CRVA))/normconstant

d=2
rhoHH=(d*rho11HD+ rho10HA+rho10HD )
rhoHV=(rho10HD-rho10HA )
rhoVH=(rho10VD-rho10VA )
rhoVV=(d*rho11VD+ rho10VA+rho10VD )

result=qutip.Qobj([[rhoHH , rhoHV],[rhoVH, rhoVV]])
resquad=result**2
purity= resquad.tr()

#save qobjs
qutip.qsave([result, resquad], outputfilename[:-4])

jsonfilename=outputfilename[:-4]+".json"
with open(jsonfilename, 'w') as outfile:
    json.dump(resultdata, outfile)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

#output of final results
print("Final result")
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

print("rhoHH = {0}".format(rhoHH), file = outputFile)
print("\nrhoHV = {0}".format(rhoHV), file = outputFile)
print("\nrhoVH = {0}".format(rhoVH), file = outputFile)
print("\nrhoVV = {0}".format(rhoVV), file = outputFile)
print("\nresult = ", result, file = outputFile)
print("\nresquad = ", resquad, file = outputFile)
print("\npurity = ", purity, file = outputFile)
