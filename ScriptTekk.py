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

outputfilename+="Tekk"
outputfilename+=".txt"

outputFile=open(outputfilename, "w")
print("Results for TwoAnc protocol", file = outputFile)

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
coincWindow = 2*1e-9
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
        coinc= ttagBuf.coincidences(spadExpTime,coincWindow,-delayarray)
        result= coinc[spadChannelA, spadChannelB]
    elif sensor == "pwm" or sensor == "PWM":
        singleMeasure = np.zeros(pwmAverage)
        for j in range(pwmAverage):
            time.sleep(pwmWait)
            p = max(pwm.read()*1000, 0.)
            singleMeasure[j] = p
        result = np.mean(singleMeasure)
    return result

input("Please unblock all paths, then press enter")
#measurement on D for normalization
print("Measuring D for normalization")
countDId = measure(rot1Angle0, rot2Angle270, rotHWPAngle675, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
print("Counts for D = ", countDId)
print("Counts for D = ", countDId, file = outputFile)

#Measurement on A for normalization
print("Measuring A for normalization")
countAId = measure(rot1Angle0, rot2Angle270, rotHWPAngle225, rotQWPAngle45, lcc1Voltage0, lcc2Voltage270)
print("Counts for A = ", countAId)
print("Counts for A = ", countAId, file = outputFile)

normconstant= countDId+countAId

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Re(HH)
#measurement of DD
print("Measuring DD for Re(HH)")
CDD= 0.25*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(HH) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant)
print("Counts for DD for Re(HH) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant, file = outputFile)

#measurement of DA
print("Measuring DA for Re(HH)")
CDA= 0.25*measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(HH) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant)
print("Counts for DA for Re(HH) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant, file = outputFile)

#measurement of AD
print("Measuring AD for Re(HH)")
CAD= 0.25*measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(HH) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant)
print("Counts for AD for Re(HH) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant, file = outputFile)

#measurement of AA
print("Measuring AA for Re(HH)")
CAA= 0.25*measure(rot1Angle180, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(HH) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant)
print("Counts for AA for Re(HH) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant, file = outputFile)

#measurement of RL
print("Measuring RL for Re(HH)")
CRL= 0.25*measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for RL for Re(HH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant)
print("Counts for RL for Re(HH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, file = outputFile)

#measurement of RR
print("Measuring RR for Re(HH)")
CRR= 0.25*measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for RR for Re(HH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant)
print("Counts for RR for Re(HH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, file = outputFile)

#measurement of LR
print("Measuring LR for Re(HH)")
CLR= 0.25*measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for LR for Re(HH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant)
print("Counts for LR for Re(HH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, file = outputFile)

#measurement of LL
print("Measuring LL for Re(HH)")
CLL = 0.25*measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LL for Re(HH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant)
print("Counts for LL for Re(HH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, file = outputFile)

#measurement of DV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(HH)")
CDV= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(HH) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant)
print("Counts for DV for Re(HH) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant, file = outputFile)

#measurement of AV
print("Measuring AV for Re(HH)")
CAV= 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(HH) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant)
print("Counts for AV for Re(HH) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant, file = outputFile)

#measurement of VD
input("Please block V path, unblock H, A, D, then press enter")
print("Measuring VD for Re(HH)")
CVD= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(HH) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant)
print("Counts for VD for Re(HH) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant, file = outputFile)

#measurement of VA
print("Measuring VA for Re(HH)")
CVA= 0.5*measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(HH) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant)
print("Counts for AV for Re(HH) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant, file = outputFile)

#measurement of VV
input("Please block V, A pathS, unblock H, D, then press enter")
print("Measuring VV for Re(HH)")
CVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(HH) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant)
print("Counts for VV for Re(HH) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant, file = outputFile)

#extraction of result
rerhoHH=0.5*((CDD-CDA-CAD+CAA)-(CLL-CLR-CRL+CRR)+2*(CDV-CAV)+2*(CVD-CVA)+4*CVV)/normconstant


#measurement of Im(HH)
input("Please unblock all paths, then press enter")
#measurement of LD
print("Measuring LD for Im(HH)")
CLD= 0.25*measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LD for Im(HH) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant)
print("Counts for LD for Im(HH) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant, file = outputFile)

#measurement of LA
print("Measuring LA for Im(HH)")
CLA= 0.25*measure(rot1Angle90, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for LA for Im(HH) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant)
print("Counts for LA for Im(HH) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant, file = outputFile)

#measurement of RD
print("Measuring RD for Im(HH)")
CRD= 0.25*measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RD for Im(HH) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant)
print("Counts for RD for Im(HH) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant, file = outputFile)

#measurement of RA
print("Measuring RA for Im(HH)")
CRA= 0.25*measure(rot1Angle270, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for RA for Im(HH) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant)
print("Counts for RA for Im(HH) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant, file = outputFile)

#measurement of DL
print("Measuring DL for Im(HH)")
CDL= 0.25*measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(HH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant)
print("Counts for DL for Im(HH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, file = outputFile)

#measurement of DR
print("Measuring DR for Im(HH)")
CDR= 0.25*measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(HH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant)
print("Counts for DR for Im(HH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, file = outputFile)

#measurement of AR
print("Measuring AR for Im(HH)")
CAR= 0.25*measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(HH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant)
print("Counts for AR for Im(HH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, file = outputFile)

#measurement of AL
print("Measuring AL for Im(HH)")
CAL = 0.25*measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(HH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant)
print("Counts for AL for Im(HH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, file = outputFile)

#measurement of LV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(HH)")
CLV= 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LV for Im(HH) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant)
print("Counts for LV for Im(HH) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant, file = outputFile)

#measurement of RV
print("Measuring RV for Im(HH)")
CRV= 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RV for Im(HH) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant)
print("Counts for RV for Im(HH) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant, file = outputFile)

#extraction of result
imrhoHH=0.5*((CLD-CLA-CRD+CRA)+(CDL-CDR-CAL+CAR)+2*(CLV-CRV))/normconstant
            

#measurement of Re(HV)
input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(HV)")
CDD= 0.25*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(HV) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant)
print("Counts for DD for Re(HV) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant, file = outputFile)

#measurement of DA
print("Measuring DA for Re(HV)")
CDA= 0.25*measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(HV) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant)
print("Counts for DA for Re(HV) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant, file = outputFile)

#measurement of AD
print("Measuring AD for Re(HV)")
CAD= 0.25*measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(HV) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant)
print("Counts for AD for Re(HV) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant, file = outputFile)

#measurement of AA
print("Measuring AA for Re(HV)")
CAA= 0.25*measure(rot1Angle180, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(HV) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant)
print("Counts for AA for Re(HV) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant, file = outputFile)

#measurement of RL
print("Measuring RL for Re(HV)")
CRL= 0.25*measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for RL for Re(HV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant)
print("Counts for RL for Re(HV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, file = outputFile)

#measurement of RR
print("Measuring RR for Re(HV)")
CRR= 0.25*measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for RR for Re(HV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant)
print("Counts for RR for Re(HV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, file = outputFile)

#measurement of LR
print("Measuring LR for Re(HV)")
CLR= 0.25*measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for LR for Re(HV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant)
print("Counts for LR for Re(HV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, file = outputFile)

#measurement of LL
print("Measuring LL for Re(HV)")
CLL = 0.25*measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for LL for Re(HV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant)
print("Counts for LL for Re(HV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, file = outputFile)

#measurement of DV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(HV)")
CDV= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(HV) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant)
print("Counts for DV for Re(HV) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant, file = outputFile)

#measurement of AV
print("Measuring AV for Re(HV)")
CAV= 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(HV) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant)
print("Counts for AV for Re(HV) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant, file = outputFile)

#measurement of VD
input("Please block V path, unblock H, A, D, then press enter")
print("Measuring VD for Re(HV)")
CVD= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(HV) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant)
print("Counts for VD for Re(HV) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant, file = outputFile)

#measurement of VA
print("Measuring VA for Re(HV)")
CVA= 0.5*measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(HV) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant)
print("Counts for AV for Re(HV) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant, file = outputFile)

#measurement of VV
input("Please block V, A paths, unblock H, D, then press enter")
print("Measuring VV for Re(HV)")
CVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(HV) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant)
print("Counts for VV for Re(HV) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant, file = outputFile)

#extraction of result
rerhoHV=0.5*((CDD-CDA-CAD+CAA)-(CLL-CLR-CRL+CRR)+2*(CDV-CAV)+2*(CVD-CVA)+4*CVV)/normconstant


#measurement of Im(HV)
input("Please unblock all paths, then press enter")
#measurement of LD
print("Measuring LD for Im(HV)")
CLD= 0.25*measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LD for Im(HV) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant)
print("Counts for LD for Im(HV) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant, file = outputFile)

#measurement of LA
print("Measuring LA for Im(HV)")
CLA= 0.25*measure(rot1Angle90, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for LA for Im(HV) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant)
print("Counts for LA for Im(HV) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant, file = outputFile)

#measurement of RD
print("Measuring RD for Im(HV)")
CRD= 0.25*measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RD for Im(HV) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant)
print("Counts for RD for Im(HV) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant, file = outputFile)

#measurement of RA
print("Measuring RA for Im(HV)")
CRA= 0.25*measure(rot1Angle270, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for RA for Im(HV) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant)
print("Counts for RA for Im(HV) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant, file = outputFile)

#measurement of DL
print("Measuring DL for Im(HV)")
CDL= 0.25*measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(HV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant)
print("Counts for DL for Im(HV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, file = outputFile)

#measurement of DR
print("Measuring DR for Im(HV)")
CDR= 0.25*measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(HV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant)
print("Counts for DR for Im(HV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, file = outputFile)

#measurement of AR
print("Measuring AR for Im(HV)")
CAR= 0.25*measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(HV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant)
print("Counts for AR for Im(HV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, file = outputFile)

#measurement of AL
print("Measuring AL for Im(HV)")
CAL = 0.25*measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(HV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant)
print("Counts for AL for Im(HV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, file = outputFile)

#measurement of LV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(HV)")
CLV= 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for LV for Im(HV) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant)
print("Counts for LV for Im(HV) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant, file = outputFile)

#measurement of RV
print("Measuring RV for Im(HV)")
CRV= 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for RV for Im(HV) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant)
print("Counts for RV for Im(HV) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant, file = outputFile)

#extraction of result
imrhoHV=0.5*((CLD-CLA-CRD+CRA)+(CDL-CDR-CAL+CAR)+2*(CLV-CRV))/normconstant
    
            
#measurement of Re(VH)
input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(VH)")
CDD= 0.25*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(VH) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant)
print("Counts for DD for Re(VH) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant, file = outputFile)

#measurement of DA
print("Measuring DA for Re(VH)")
CDA= 0.25*measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(VH) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant)
print("Counts for DA for Re(VH) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant, file = outputFile)

#measurement of AD
print("Measuring AD for Re(VH)")
CAD= 0.25*measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(VH) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant)
print("Counts for AD for Re(VH) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant, file = outputFile)

#measurement of AA
print("Measuring AA for Re(VH)")
CAA= 0.25*measure(rot1Angle180, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(VH) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant)
print("Counts for AA for Re(VH) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant, file = outputFile)

#measurement of RL
print("Measuring RL for Re(VH)")
CRL= 0.25*measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RL for Re(VH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant)
print("Counts for RL for Re(VH) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, file = outputFile)

#measurement of RR
print("Measuring RR for Re(VH)")
CRR= 0.25*measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for RR for Re(VH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant)
print("Counts for RR for Re(VH) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, file = outputFile)

#measurement of LR
print("Measuring LR for Re(VH)")
CLR= 0.25*measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for LR for Re(VH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant)
print("Counts for LR for Re(VH) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, file = outputFile)

#measurement of LL
print("Measuring LL for Re(VH)")
CLL = 0.25*measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for LL for Re(VH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant)
print("Counts for LL for Re(VH) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, file = outputFile)

#measurement of DV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(VH)")
CDV= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(VH) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant)
print("Counts for DV for Re(VH) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant, file = outputFile)

#measurement of AV
print("Measuring AV for Re(VH)")
CAV= 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(VH) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant)
print("Counts for AV for Re(VH) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant, file = outputFile)

#measurement of VD
input("Please block H path, unblock V, A, D, then press enter")
print("Measuring VD for Re(VH)")
CVD= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(VH) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant)
print("Counts for VD for Re(VH) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant, file = outputFile)

#measurement of VA
print("Measuring VA for Re(VH)")
CVA= 0.5*measure(rot1Angle0, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(VH) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant)
print("Counts for AV for Re(VH) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant, file = outputFile)

#measurement of VV
input("Please block H, A paths, unblock V, D, then press enter")
print("Measuring VV for Re(VH)")
CVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(VH) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant)
print("Counts for VV for Re(VH) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant, file = outputFile)

#extraction of result
rerhoVH=0.5*((CDD-CDA-CAD+CAA)-(CLL-CLR-CRL+CRR)+2*(CDV-CAV)+2*(CVD-CVA)+4*CVV)/normconstant


#measurement of Im(VH)
input("Please unblock all paths, then press enter")
#measurement of LD
print("Measuring LD for Im(VH)")
CLD= 0.25*measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LD for Im(VH) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant)
print("Counts for LD for Im(VH) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant, file = outputFile)

#measurement of LA
print("Measuring LA for Im(VH)")
CLA= 0.25*measure(rot1Angle270, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for LA for Im(VH) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant)
print("Counts for LA for Im(VH) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant, file = outputFile)

#measurement of RD
print("Measuring RD for Im(VH)")
CRD= 0.25*measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RD for Im(VH) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant)
print("Counts for RD for Im(VH) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant, file = outputFile)

#measurement of RA
print("Measuring RA for Im(VH)")
CRA= 0.25*measure(rot1Angle90, rot2Angle180, rotHWPAngle45, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for RA for Im(VH) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant)
print("Counts for RA for Im(VH) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant, file = outputFile)

#measurement of DL
print("Measuring DL for Im(VH)")
CDL= 0.25*measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(VH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant)
print("Counts for DL for Im(VH) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, file = outputFile)

#measurement of DR
print("Measuring DR for Im(VH)")
CDR= 0.25*measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(VH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant)
print("Counts for DR for Im(VH) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, file = outputFile)

#measurement of AR
print("Measuring AR for Im(VH)")
CAR= 0.25*measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(VH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant)
print("Counts for AR for Im(VH) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, file = outputFile)

#measurement of AL
print("Measuring AL for Im(VH)")
CAL = 0.25*measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(VH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant)
print("Counts for AL for Im(VH) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, file = outputFile)

#measurement of LV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(VH)")
CLV= 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LV for Im(VH) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant)
print("Counts for LV for Im(VH) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant, file = outputFile)

#measurement of RV
print("Measuring RV for Im(VH)")
CRV= 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RV for Im(VH) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant)
print("Counts for RV for Im(VH) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant, file = outputFile)

#extraction of result
imrhoVH=0.5*((CLD-CLA-CRD+CRA)+(CDL-CDR-CAL+CAR)+2*(CLV-CRV))/normconstant
            
            
#measurement of Re(VV)
input("Please unblock all paths, then press enter")
#measurement of DD
print("Measuring DD for Re(VV)")
CDD= 0.25*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DD for Re(VV) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant)
print("Counts for DD for Re(VV) = ", CDD, "\tNormalized to diagonal = ", CDD/normconstant, file = outputFile)

#measurement of DA
print("Measuring DA for Re(VV)")
CDA= 0.25*measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for DA for Re(VV) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant)
print("Counts for DA for Re(VV) = ", CDA, "\tNormalized to diagonal = ", CDA/normconstant, file = outputFile)

#measurement of AD
print("Measuring AD for Re(VV)")
CAD= 0.25*measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AD for Re(VV) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant)
print("Counts for AD for Re(VV) = ", CAD, "\tNormalized to diagonal = ", CAD/normconstant, file = outputFile)

#measurement of AA
print("Measuring AA for Re(VV)")
CAA= 0.25*measure(rot1Angle180, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage180, lcc2Voltage180)
print("Counts for AA for Re(VV) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant)
print("Counts for AA for Re(VV) = ", CAA, "\tNormalized to diagonal = ", CAA/normconstant, file = outputFile)

#measurement of RL
print("Measuring RL for Re(VV)")
CRL= 0.25*measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
print("Counts for RL for Re(VV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant)
print("Counts for RL for Re(VV) = ", CRL, "\tNormalized to diagonal = ", CRL/normconstant, file = outputFile)

#measurement of RR
print("Measuring RR for Re(VV)")
CRR= 0.25*measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
print("Counts for RR for Re(VV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant)
print("Counts for RR for Re(VV) = ", CRR, "\tNormalized to diagonal = ", CRR/normconstant, file = outputFile)

#measurement of LR
print("Measuring LR for Re(VV)")
CLR= 0.25*measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
print("Counts for LR for Re(VV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant)
print("Counts for LR for Re(VV) = ", CLR, "\tNormalized to diagonal = ", CLR/normconstant, file = outputFile)

#measurement of LL
print("Measuring LL for Re(VV)")
CLL = 0.25*measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
print("Counts for LL for Re(VV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant)
print("Counts for LL for Re(VV) = ", CLL, "\tNormalized to diagonal = ", CLL/normconstant, file = outputFile)

#measurement of DV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring DV for Re(VV)")
CDV= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for DV for Re(VV) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant)
print("Counts for DV for Re(VV) = ", CDV, "\tNormalized to diagonal = ", CDV/normconstant, file = outputFile)

#measurement of AV
print("Measuring AV for Re(VV)")
CAV= 0.5*measure(rot1Angle180, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage0)
print("Counts for AV for Re(VV) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant)
print("Counts for AV for Re(VV) = ", CAV, "\tNormalized to diagonal = ", CAV/normconstant, file = outputFile)

#measurement of VD
input("Please block H path, unblock V, A, D, then press enter")
print("Measuring VD for Re(VV)")
CVD= 0.5*measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VD for Re(VV) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant)
print("Counts for VD for Re(VV) = ", CVD, "\tNormalized to diagonal = ", CVD/normconstant, file = outputFile)

#measurement of VA
print("Measuring VA for Re(VV)")
CVA= 0.5*measure(rot1Angle0, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage0, lcc2Voltage180)
print("Counts for AV for Re(VV) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant)
print("Counts for AV for Re(VV) = ", CVA, "\tNormalized to diagonal = ", CVA/normconstant, file = outputFile)

#measurement of VV
input("Please block H, A paths, unblock V, D, then press enter")
print("Measuring VV for Re(VV)")
CVV= measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
print("Counts for VV for Re(VV) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant)
print("Counts for VV for Re(VV) = ", CVV, "\tNormalized to diagonal = ", CVV/normconstant, file = outputFile)

#extraction of result
rerhoVV=0.5*((CDD-CDA-CAD+CAA)-(CLL-CLR-CRL+CRR)+2*(CDV-CAV)+2*(CVD-CVA)+4*CVV)/normconstant


#measurement of Im(VV)
input("Please unblock all paths, then press enter")
#measurement of LD
print("Measuring LD for Im(VV)")
CLD= 0.25*measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LD for Im(VV) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant)
print("Counts for LD for Im(VV) = ", CLD, "\tNormalized to diagonal = ", CLD/normconstant, file = outputFile)

#measurement of LA
print("Measuring LA for Im(VV)")
CLA= 0.25*measure(rot1Angle270, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage270, lcc2Voltage180)
print("Counts for LA for Im(VV) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant)
print("Counts for LA for Im(VV) = ", CLA, "\tNormalized to diagonal = ", CLA/normconstant, file = outputFile)

#measurement of RD
print("Measuring RD for Im(VV)")
CRD= 0.25*measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RD for Im(VV) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant)
print("Counts for RD for Im(VV) = ", CRD, "\tNormalized to diagonal = ", CRD/normconstant, file = outputFile)

#measurement of RA
print("Measuring RA for Im(VV)")
CRA= 0.25*measure(rot1Angle90, rot2Angle180, rotHWPAngle0, rotQWPAngle90, lcc1Voltage90, lcc2Voltage180)
print("Counts for RA for Im(VV) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant)
print("Counts for RA for Im(VV) = ", CRA, "\tNormalized to diagonal = ", CRA/normconstant, file = outputFile)

#measurement of DL
print("Measuring DL for Im(VV)")
CDL= 0.25*measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
print("Counts for DL for Im(VV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant)
print("Counts for DL for Im(VV) = ", CDL, "\tNormalized to diagonal = ", CDL/normconstant, file = outputFile)

#measurement of DR
print("Measuring DR for Im(VV)")
CDR= 0.25*measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
print("Counts for DR for Im(VV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant)
print("Counts for DR for Im(VV) = ", CDR, "\tNormalized to diagonal = ", CDR/normconstant, file = outputFile)

#measurement of AR
print("Measuring AR for Im(VV)")
CAR= 0.25*measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
print("Counts for AR for Im(VV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant)
print("Counts for AR for Im(VV) = ", CAR, "\tNormalized to diagonal = ", CAR/normconstant, file = outputFile)

#measurement of AL
print("Measuring AL for Im(VV)")
CAL = 0.25*measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
print("Counts for AL for Im(VV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant)
print("Counts for AL for Im(VV) = ", CAL, "\tNormalized to diagonal = ", CAL/normconstant, file = outputFile)

#measurement of LV
input("Please block A path, unblock H, V, D, then press enter")
print("Measuring LV for Im(VV)")
CLV= 0.5*measure(rot1Angle270, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage0)
print("Counts for LV for Im(VV) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant)
print("Counts for LV for Im(VV) = ", CLV, "\tNormalized to diagonal = ", CLV/normconstant, file = outputFile)

#measurement of RV
print("Measuring RV for Im(VV)")
CRV= 0.5*measure(rot1Angle90, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage0)
print("Counts for RV for Im(VV) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant)
print("Counts for RV for Im(VV) = ", CRV, "\tNormalized to diagonal = ", CRV/normconstant, file = outputFile)

#extraction of result
imrhoVV=0.5*((CLD-CLA-CRD+CRA)+(CDL-CDR-CAL+CAR)+2*(CLV-CRV))/normconstant
            
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