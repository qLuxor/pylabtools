# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 21:07:23 2017

@author: Giulio Foletto
"""

#necessary imports
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

if len(sys.argv) >0:
    filename = str(sys.argv[1])
else:
    filename ='settings.json'

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()

#useful values
allowtime=settings["allowtime"]
angleErr=settings["angleErr"]
voltageErr = settings["voltageErr"]

#pwm configuration and initialization
pwm = pm100d()
pwmAverage=settings["pwmAverage"]
pwmWait=settings["pwmWait"]

#SPAD configuration and initialization
print("Initializing SPAD")
bufNum =settings["bufNum"]
delay=settings["delay"]
delay = delay*1e-9
channelA=settings["channelA"]
channelB=settings["channelB"]
delayarray = np.array([delay, 0.0, 0.0,0.0])
exptime = settings["exptime"]
exptime = exptime*1e-3
coincWindow = 2*1e-9
ttagBuf = ttag.TTBuffer(bufNum) 

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
rotHWPAngle0=settings["rotHWPAngle0"]
rotHWPAngle45=settings["rotHWPAngle45"]

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
    time.sleep(allowtime)
    #time.sleep(exptime)
    #coinc ttagBuf.coincidences(exptime,coincWindow,-delayarray)
    #return coinc[channelA, channelB]
    singleMeasure = np.zeros(pwmAverage)
    for j in range(pwmAverage):
        time.sleep(pwmWait)
        p = max(pwm.read()*1000, 0.)
        singleMeasure[j] = p
    return np.mean(singleMeasure)

#measurement of diagonal H via scheme
input("Please block V path, unblock H, then press enter")
countH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#measurement of diagonal V via scheme
input("Please block H path, unblock V, then press enter")
countV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)
input("Please unblock all paths, then press enter")

#measurement on diagonal V
print("Measuring VV")
countVId = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#Measurement on diagonal H
print("Measuring HH")
countHId = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle45, lcc1Voltage0, lcc2Voltage0)

#normalization and extraction of diagonal elements
normconstant= countHId+countVId
#the following 4 factor is due to the scheme, both V and Id are measured with 22.5, so their ratio is not affected
rhoHH=4*countH/normconstant
rhoVV=4*countV/normconstant
#the following 4 factor is due to the fact that Id is measured with 22.5
normconstant = 4*normconstant
print("rhoHH = ", rhoHH)
print("rhoVV = ", rhoVV)

#measurement of Re(VH)
#measurement of PRL
print("Measuring PRL for Re(VH)")
PRL= measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)

#measurement of PRR
print("Measuring PRR for Re(VH)")
PRR= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)

#measurement of PLR
print("Measuring PLR for Re(VH)")
PLR= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)

#measurement of PLL
print("Measuring PLL for Re(VH)")
PLL = measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)

#extraction of Re(VH)
rerhoVH=(PRL+PLR-PRR-PLL)/normconstant
print("rerhoVH = ", rerhoVH)
        
#measurement of Im(VH)
#measurement of PAL
print("Measuring PAL for Im(VH)")
PAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)

#measurement of PAR
print("Measuring PAR for Im(VH)")
PAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)

#measurement of PDR
print("Measuring PDR for Im(VH)")
PDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)

#measurement of PDL
print("Measuring PDL for Im(VH)")
PDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)

#extraction of Im(VH)
imrhoVH=(PDL-PDR+PAR-PAL)/normconstant 
print("imrhoVH = ", imrhoVH)  

#measurement of Re(HV)
#measurement of PLL
print("Measuring PLL for Re(HV)")
PLL = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)

#measurement of PLR
print("Measuring PLR for Re(HV)")
PLR= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)

#measurement of PRR
print("Measuring PRR for Re(HV)")
PRR= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)

#measurement of PRL
print("Measuring PRL for Re(HV)")
PRL= measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)

#extraction of Re(HV)
rerhoHV=(PRL+PLR-PRR-PLL)/normconstant
print("rerhoHV = ", rerhoHV)

#measurement of Im(HV)
#measurement of PAL
print("Measuring PAL for Im(HV)")
PAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)

#measurement of PAR
print("Measuring PAR for Im(HV)")
PAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)

#measurement of PDR
print("Measuring PDR for Im(HV)")
PDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)

#measurement of PDL
print("Measuring PDL for Im(HV)")
PDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)

#extraction of Im(HV)
imrhoHV=(PDL-PDR+PAR-PAL)/normconstant
print("imrhoHV = ", imrhoHV)
        
print("Finished all measurements\n\n")

#output of final results
print("Final result")
result=Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
resquad=result**2
purity= resquad.tr()
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

outputfilename=settings["outputfilename"]
with open(outputfilename, "w") as text_file:
    text_file.write("rhoHH = {0}".format(rhoHH))
    text_file.write("\nrhoVV = {0}".format(rhoVV))
    text_file.write("\nrerhoHV = {0}".format(rerhoHV))
    text_file.write("\nimrhoHV = {0}".format(imrhoHV))
    text_file.write("\nrerhoVH = {0}".format(rerhoVH))
    text_file.write("\nimrhoVH = {0}".format(imrhoVH))
    text_file.write("\nresult = ", result)
    text_file.write("\nresquad = ", resquad)
    text_file.write("\npurity = ", purity)