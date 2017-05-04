# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 18:07:57 2017

@author: Giulio Foletto 2
"""

import sys
sys.path.append('..')
import time
import aptlib
import numpy as np
import instruments as ik
from qutip import *
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

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()

#useful values
allowTime=settings["allowTime"]
angleErr=settings["angleErr"]
voltageErr = settings["voltageErr"]

#pwm configuration and initialization
pwm = pm100d()
pwmAverage=settings["pwmAverage"]
pwmWait=settings["pwmWait"]

#SPAD configuration and initialization
print("Initializing SPAD")
spadBufNum =settings["spadBufNum"]
spadDelay=settings["spadDelay"]
spadDelay = spadDelay*1e-9
spadChannelA=settings["spadChannelA"]
spadChannelB=settings["spadChannelB"]
delayarray = np.array([spadDelay, 0.0, 0.0,0.0])
exptime = settings["exptime"]
exptime = exptime*1e-3
coincWindow = 2*1e-9
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
rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = settings["rot2SN"]
rot2 = aptlib.PRM1(serial_number=rot2SN)
rot2.home()

#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= settings["rotHWPSN"]
rotHWP = aptlib.PRM1(serial_number=rotHWPSN)
#rotHWP.home() #commented out due to bug in rotator

#ROTQWP configuration and initialization
print("Initializing ROTQWP")
rotQWPSN= settings["rotQWPSN"]
rotQWP = aptlib.PRM1(serial_number=rotQWPSN)
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
    #time.sleep(spadExpTime)
    #coinc ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
    #return coinc[spadChannelB, spadChannelA]
    singleMeasure = np.zeros(pwmAverage)
    for j in range(pwmAverage):
        time.sleep(pwmWait)
        p = max(pwm.read()*1000, 0.)
        singleMeasure[j] = p
    return np.mean(singleMeasure)

#measurement on D for normalization
print("Measuring D for normalization")
countDId = measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#Measurement on A for normalization
print("Measuring A for normalization")
countAId = measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#Measurement on srhoHD
input("Please block deflected (A) ray in second int. Then press Enter")
print("Measuring PD for HD")
HDPD = 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Measuring PA for HD")
HDPA = 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
print("Measuring PL for HD")
HDPL = 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Measuring PR for HD")
HDPR = 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)

#For simplicity measurements are not repeated
VDPD=HDPD
VDPA=HDPA
VDPL=HDPR
VDPR=HDPL

#useful values
rho10HD = 0.5* (HDPD-HDPA+1.0j*(HDPL-HDPR))
rho10VD = 0.5* (VDPD-VDPA+1.0j*(VDPL-VDPR))

input("Please block deflected (H) ray in first int. Then press Enter")
print("Measuring PV for VD")
VDPV=measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

input("Please block transmitted (V) ray in first int. Then press Enter")
print("Measuring PV for HD")
HDPV=measure(rot1Angle0, rot2Angle0, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#useful values
rho11VD = VDPV
rho11HD = HDPV

#Measurement on srhoHA
input("Please unblock all rays, then block transmitted (D) ray in second int. Then press Enter")
print("Measuring PD for HA")
HAPD = 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
print("Measuring PA for HA")
HAPA = 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage180, lcc2Voltage0)
print("Measuring PL for HA")
HAPL = 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage90, lcc2Voltage0)
print("Measuring PR for HA")
HAPR = 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle225, rotQWPAngle45, lcc1Voltage270, lcc2Voltage0)

#For simplicity measurements are not repeated
VAPD=HAPD
VAPA=HAPA
VAPL=HAPR
VAPR=HAPL

#useful values
rho10HA = 0.5* (HAPD-HAPA+1.0j*(HAPL-HAPR))
rho10VA = 0.5* (VAPD-VAPA+1.0j*(VAPL-VAPR))

d=2
rhoHH=(d*rho11HD+ rho10HA+rho10HD )
rhoHV=(rho10HD-rho10HA )
rhoVH=(rho10VD-rho10VA )
rhoVV=(d*rho11VD+ rho10VA+rho10VD )

#output of final results
print("Final result")
result=Qobj([[rhoHH , rhoHV],[rhoVH, rhoVV]])
resquad=result**2
purity= resquad.tr()
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

outputfilename=settings["outputFileName"]
with open(outputfilename, "w") as text_file:
    text_file.write("rhoHH = {0}".format(rhoHH))
    text_file.write("\nrhoHV = {0}".format(rhoHV))
    text_file.write("\nrhoVH = {0}".format(rhoVH))
    text_file.write("\nrhoVV = {0}".format(rhoVV))
    text_file.write("\nresult = ", result)
    text_file.write("\nresquad = ", resquad)
    text_file.write("\npurity = ", purity)