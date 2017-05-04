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

if len(sys.argv) >1:
    filename = str(sys.argv[1])
else:
    filename ='settings.json'

with open(filename) as json_settings:
    settings = json.load(json_settings)
    json_settings.close()

outputfilename=settings["outputFileName"] 
outputFile=open(outputfilename, "w")

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
spadExpTime = settings["spadExpTime"]
spadExpTime = spadExpTime*1e-3
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
rotHWPAngle0=settings["rotHWPAngle0"]
rotHWPAngle45=settings["rotHWPAngle45"]
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
    #return coinc[spadChannelA, spadChannelB]
    singleMeasure = np.zeros(pwmAverage)
    for j in range(pwmAverage):
        time.sleep(pwmWait)
        p = max(pwm.read()*1000, 0.)
        singleMeasure[j] = p
    return np.mean(singleMeasure)

input("Please unblock all paths, then press enter")
#measurement on D for normalization
print("Measuring D for normalization")
countDId = measure(rot1Angle0, rot2Angle270, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
print("Counts for D = ", countDId)
print("Counts for D = ", countDId, file = outputFile)

#Measurement on diagonal H
print("Measuring A for normalization")
countAId = measure(rot1Angle0, rot2Angle270, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
print("Counts for A = ", countAId)
print("Counts for A = ", countAId, file = outputFile)

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of diagonal H via scheme
input("Please block V and A paths, unblock H, then press enter")
print("Measuring H")
countH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for H = ", countH)
print("Counts for H = ", countH, file = outputFile)

#measurement of diagonal V via scheme
input("Please block H and A paths, unblock V, then press enter")
print("Measuring V")
countV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
input("Please unblock all paths, then press enter")
print("Counts for V = ", countV)
print("Counts for V = ", countV, file = outputFile)

#normalization and extraction of diagonal elements
normconstant= countDId+countAId
normscheme= countH+countV

#the following 4 factor is due to the scheme, both V and Id are measured with 22.5, so their ratio is not affected
rhoHH=4*countH/normconstant
rhoVV=4*countV/normconstant
rhoHHscheme=4*countH/normscheme
rhoVVscheme=4*countV/normscheme
#the following 4 factor is due to the fact that Id is measured with 22.5
normconstant = 4*normconstant
normscheme = 4* normscheme
print("rhoHH = ", rhoHH)
print("rhoVV = ", rhoVV)

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Re(VH)
#measurement of RL
print("Measuring RL for Re(VH)")
CRL= measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RL for Re(VH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, "\tNormalized to scheme = ", CRL/normscheme)
print("Counts for RL for Re(VH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, "\tNormalized to scheme = ", CRL/normscheme, file = outputFile)

#measurement of RR
print("Measuring RR for Re(VH)")
CRR= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for RR for Re(VH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, "\tNormalized to scheme = ", CRR/normscheme)
print("Counts for RR for Re(VH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, "\tNormalized to scheme = ", CRR/normscheme, file = outputFile)

#measurement of LR
print("Measuring LR for Re(VH)")
CLR= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for LR for Re(VH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, "\tNormalized to scheme = ", CLR/normscheme)
print("Counts for LR for Re(VH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, "\tNormalized to scheme = ", CLR/normscheme, file = outputFile)

#measurement of LL
print("Measuring LL for Re(VH)")
CLL = measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for LL for Re(VH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, "\tNormalized to scheme = ", CLL/normscheme)
print("Counts for LL for Re(VH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, "\tNormalized to scheme = ", CLL/normscheme, file = outputFile)

#extraction of Re(VH)
rerhoVH=(CRL+CLR-CRR-CLL)/normconstant
rerhoVHscheme = (CRL+CLR-CRR-CLL)/normscheme
print("rerhoVH = ", rerhoVH)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
#measurement of Im(VH)
#measurement of AL
print("Measuring AL for Im(VH)")
CAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(VH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, "\tNormalized to scheme = ", CAL/normscheme)
print("Counts for AL for Im(VH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, "\tNormalized to scheme = ", CAL/normscheme, file = outputFile)

#measurement of AR
print("Measuring AR for Im(VH)")
CAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(VH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, "\tNormalized to scheme = ", CAR/normscheme)
print("Counts for AR for Im(VH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, "\tNormalized to scheme = ", CAR/normscheme, file = outputFile)

#measurement of DR
print("Measuring DR for Im(VH)")
CDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(VH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, "\tNormalized to scheme = ", CDR/normscheme)
print("Counts for DR for Im(VH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, "\tNormalized to scheme = ", CDR/normscheme, file = outputFile)

#measurement of DL
print("Measuring DL for Im(VH)")
CDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(VH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, "\tNormalized to scheme = ", CDL/normscheme)
print("Counts for DL for Im(VH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, "\tNormalized to scheme = ", CDL/normscheme, file = outputFile)

#extraction of Im(VH)
imrhoVH=(CDL-CDR+CAR-CAL)/normconstant 
imrhoVHscheme=(CDL-CDR+CAR-CAL)/normscheme 
print("imrhoVH = ", imrhoVH)  

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Re(HV)
#measurement of LL
print("Measuring LL for Re(HV)")
CLL = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LL for Re(HV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, "\tNormalized to scheme = ", CLL/normscheme)
print("Counts for LL for Re(HV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, "\tNormalized to scheme = ", CLL/normscheme, file = outputFile)

#measurement of LR
print("Measuring LR for Re(HV)")
CLR= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for LR for Re(HV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, "\tNormalized to scheme = ", CLR/normscheme)
print("Counts for LR for Re(HV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, "\tNormalized to scheme = ", CLR/normscheme, file = outputFile)

#measurement of RR
print("Measuring RR for Re(HV)")
CRR= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for RR for Re(HV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, "\tNormalized to scheme = ", CRR/normscheme)
print("Counts for RR for Re(HV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, "\tNormalized to scheme = ", CRR/normscheme, file = outputFile)

#measurement of RL
print("Measuring RL for Re(HV)")
CRL= measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for RL for Re(HV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, "\tNormalized to scheme = ", CRL/normscheme)
print("Counts for RL for Re(HV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, "\tNormalized to scheme = ", CRL/normscheme, file = outputFile)

#extraction of Re(HV)
rerhoHV=(CRL+CLR-CRR-CLL)/normconstant
rerhoHVscheme=(CRL+CLR-CRR-CLL)/normscheme
print("rerhoHV = ", rerhoHV)

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Im(HV)
#measurement of AL
print("Measuring AL for Im(HV)")
CAL = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(HV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, "\tNormalized to scheme = ", CAL/normscheme)
print("Counts for AL for Im(HV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, "\tNormalized to scheme = ", CAL/normscheme, file = outputFile)

#measurement of AR
print("Measuring AR for Im(HV)")
CAR= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(HV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, "\tNormalized to scheme = ", CAR/normscheme)
print("Counts for AR for Im(HV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, "\tNormalized to scheme = ", CAR/normscheme, file = outputFile)

#measurement of DR
print("Measuring DR for Im(HV)")
CDR= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(HV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, "\tNormalized to scheme = ", CDR/normscheme)
print("Counts for DR for Im(HV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, "\tNormalized to scheme = ", CDR/normscheme, file = outputFile)

#measurement of DL
print("Measuring DL for Im(HV)")
CDL= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(HV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, "\tNormalized to scheme = ", CDL/normscheme)
print("Counts for DL for Im(HV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, "\tNormalized to scheme = ", CDL/normscheme, file = outputFile)

#extraction of Im(HV)
imrhoHV=(CDL-CDR+CAR-CAL)/normconstant
imrhoHVscheme=(CDL-CDR+CAR-CAL)/normscheme
print("imrhoHV = ", imrhoHV)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

result=Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
resquad=result**2
purity= resquad.tr()

resultscheme=Qobj([[rhoHHscheme , rerhoHVscheme+imrhoHVscheme*1j],[rerhoVHscheme+imrhoVHscheme*1j, rhoVVscheme]])
resquadscheme=resultscheme**2
purityscheme= resquadscheme.tr()

#output of final results
print("Final result")
print("Result = ", result)
print("Resquad = ", resquad)
print("Purity (as trace of resquad) = ", purity)

print("The following results are obtained using the diagonal measurements for normalization", file = outputFile)
print("Corrected normalization constant = {0}".format(normconstant), file = outputFile)
print("rhoHH = {0}".format(rhoHH), file = outputFile)
print("\nrhoVV = {0}".format(rhoVV), file = outputFile)
print("\nrerhoHV = {0}".format(rerhoHV), file = outputFile)
print("\nimrhoHV = {0}".format(imrhoHV), file = outputFile)
print("\nrerhoVH = {0}".format(rerhoVH), file = outputFile)
print("\nimrhoVH = {0}".format(imrhoVH), file = outputFile)
print("\nresult = ", result, file = outputFile)
print("\nresquad = ", resquad, file = outputFile)
print("\npurity = ", purity, file = outputFile)

print("\n\n\n", file = outputFile)

print("The following results are obtained using the scheme measurements for normalization", file = outputFile)
print("Corrected normalization constant = {0}".format(normscheme), file = outputFile)
print("rhoHH = {0}".format(rhoHHscheme), file = outputFile)
print("\nrhoVV = {0}".format(rhoVVscheme), file = outputFile)
print("\nrerhoHV = {0}".format(rerhoHVscheme), file = outputFile)
print("\nimrhoHV = {0}".format(imrhoHVscheme), file = outputFile)
print("\nrerhoVH = {0}".format(rerhoVHscheme), file = outputFile)
print("\nimrhoVH = {0}".format(imrhoVHscheme), file = outputFile)
print("\nresult = ", resultscheme, file = outputFile)
print("\nresquad = ", resquadscheme, file = outputFile)
print("\npurity = ", purityscheme, file = outputFile)