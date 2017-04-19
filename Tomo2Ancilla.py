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

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

#functions that set apparatus to specific settings
def setangle(rotator, angle, angleErr):
    if abs(rotator.position()-angle)> angleErr:
        rotator.goto(angle, wait=True)

def setvoltage(lcc, voltage, voltageErr):
    if abs(lcc.voltage1 - voltage) > voltageErr:
        lcc.voltage1=voltage

#useful values
allowtime=1.5
angleErr=1e-2
voltageErr = 1e-3

#SPAD configuration and initialization
print("Initializing SPAD")
bufNum =0
delay=0
delay = delay*1e-9
channelA=0
channelB=0
delayarray = np.array([delay, 0.0, 0.0,0.0])
exptime = 1000
exptime = exptime*1e-3
coincWindow = 2*1e-9
ttagBuf = ttag.TTBuffer(bufNum) 

#LCC1 configuration and initialization
print("Initializing LCC1")
port1="/dev/ttyUSB1"
lcc1 = ik.thorlabs.LCC25.open_serial(port1, 115200,timeout=1)
lcc1.mode = lcc1.Mode.voltage1
lcc1.enable = True

#LLC2 configuration and initialization
print("Initializing LCC2")
port2="/dev/ttyUSB2"
lcc2 = ik.thorlabs.LCC25.open_serial(port2, 115200,timeout=1)
lcc2.mode = lcc2.Mode.voltage1
lcc2.enable = True

#ROT1 configuration and initialization
print("Initializing ROT1")
rot1SN = 83825706
rot1 = aptlib.PRM1(serial_number=rot1SN)
rot1.home()

#ROT2 configuration and initialization
print("Initializing ROT2")
rot2SN = 838304445
rot2 = aptlib.PRM1(serial_number=rot2SN)
rot2.home()

#ROTHWP configuration and initialization
print("Initializing ROTHWP")
rotHWPSN= 83815359
rotHWP = aptlib.PRM1(serial_number=rotHWPSN)
rotHWP.home()

print("Finished initialization\n\n")
#calibration values for ROT1
rot1Angle0=43.8
rot1Angle90=43.8
rot1Angle180=133.8
rot1Angle270=133.8

#calibration values for LCC1
lcc1Voltage0=1.5
lcc1Voltage90=10
lcc1Voltage180=3.0
lcc1Voltage270=1.0

#calibration values for ROT2
rot2Angle0=45.7
rot2Angle90=45.7
rot2Angle180=135.7
rot2Angle270=135.7

#calibration values for LCC2
lcc2Voltage0=10
lcc2Voltage90=1.5
lcc2Voltage270=1.6

#calibration values for ROTHWP
rotHWPAngle0=130.2
rotHWPAngle45=85.2

#functions that implements settings
def measure(rot1angle, rot2angle, rotHWPangle, lcc1voltage, lcc2voltage):
    setangle(rot1, rot1angle, angleErr)
    setangle(rot2, rot2angle, angleErr)
    setangle(rotHWP, rotHWPangle, angleErr)
    setvoltage(lcc1, lcc1voltage, voltageErr)
    setvoltage(lcc2, lcc2voltage, voltageErr)
    time.sleep(allowtime)
    time.sleep(exptime)
    return ttagBuf.coincidences(exptime,coincWindow,-delayarray)

#Measurement on diagonal H
print("Measuring HH")
countH = measure(rot1Angle0, rot2Angle0, rotHWPAngle45, lcc1Voltage0, lcc2Voltage0)

#measurement on diagonal V
print("Measuring VV")
countV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, lcc1Voltage0, lcc2Voltage0)

#normalization and extraction of diagonal elements
normconstant= countH+countV
rhoHH=countH/normconstant
rhoVV=countV/normconstant

#measurement of Re(HV)
#measurement of PLL
print("Measuring PLL for Re(HV)")
PLL = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, lcc1Voltage90, lcc2Voltage90)

#measurement of PLR
print("Measuring PLR for Re(HV)")
PLR= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, lcc1Voltage90, lcc2Voltage270)

#measurement of PRR
print("Measuring PRR for Re(HV)")
PRR= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, lcc1Voltage270, lcc2Voltage270)

#measurement of PRL
print("Measuring PRL for Re(HV)")
PRL= measure(rot1Angle270, rot2Angle90, rotHWPAngle0, lcc1Voltage270, lcc2Voltage90)

#extraction of Re(HV)
rerhoHV=(PRL+PLR-PRR-PLL)/normconstant

#measurement of Im(HV)
#measurement of PAL
print("Measuring PAL for Im(HV)")
PAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, lcc1Voltage180, lcc2Voltage90)

#measurement of PAR
print("Measuring PAR for Im(HV)")
PAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, lcc1Voltage180, lcc2Voltage270)

#measurement of PDR
print("Measuring PDR for Im(HV)")
PDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, lcc1Voltage0, lcc2Voltage270)

#measurement of PDL
print("Measuring PDL for Im(HV)")
PDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, lcc1Voltage0, lcc2Voltage90)

#extraction of Im(HV)
imrhoHV=(PDL-PDR+PAR-PAL)/normconstant
        
#measurement of Re(VH)
#measurement of PRL
print("Measuring PRL for Re(VH)")
PRL= measure(rot1Angle90, rot2Angle90, rotHWPAngle45, lcc1Voltage90, lcc2Voltage90)

#measurement of PRR
print("Measuring PRR for Re(VH)")
PRR= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, lcc1Voltage90, lcc2Voltage270)

#measurement of PLR
print("Measuring PLR for Re(VH)")
PLR= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, lcc1Voltage270, lcc2Voltage270)

#measurement of PLL
print("Measuring PLL for Re(VH)")
PLL = measure(rot1Angle270, rot2Angle90, rotHWPAngle45, lcc1Voltage270, lcc2Voltage90)

#extraction of Re(VH)
rerhoVH=(PRL+PLR-PRR-PLL)/normconstant
        
#measurement of Im(VH)
#measurement of PAL
print("Measuring PAL for Im(VH)")
PAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, lcc1Voltage180, lcc2Voltage90)

#measurement of PAR
print("Measuring PAR for Im(VH)")
PAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, lcc1Voltage180, lcc2Voltage270)

#measurement of PDR
print("Measuring PDR for Im(VH)")
PDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, lcc1Voltage0, lcc2Voltage270)

#measurement of PDL
print("Measuring PDL for Im(VH)")
PDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, lcc1Voltage0, lcc2Voltage90)

#extraction of Im(VH)
imrhoVH=(PDL-PDR+PAR-PAL)/normconstant   

print("Finished all measurements\n\n")

#output of final results
print("Final result")
result=Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])