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

outputfilename+="TwoAnc"
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

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of diagonal H via scheme
input("Please block V and A paths, unblock H, then press enter")
print("Measuring H")
countH = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CHRaw": countH, "CH": 16*countH})
print("Counts for H = ", countH)
print("Counts for H = ", countH, file = outputFile)

#measurement of diagonal V via scheme
input("Please block H and A paths, unblock V, then press enter")
print("Measuring V")
countV = measure(rot1Angle0, rot2Angle0, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage0)
resultdata.update({"CVRaw": countV, "CV": 16*countV})
input("Please unblock all paths, then press enter")
print("Counts for V = ", countV)
print("Counts for V = ", countV, file = outputFile)

#normalization and extraction of diagonal elements
normconstant= countDId+countAId
#the following 4 factor is due to the scheme, counts are 4 times too small
normscheme= 4*(countH+countV)

#the following 4 factor is due to the scheme, both V and Id are measured with 22.5, so their ratio is not affected
rhoHH=4*countH/normconstant
rhoVV=4*countV/normconstant
#the following 4 factor is circular with the one above, but it is coherent with the scheme
rhoHHscheme=4*countH/normscheme
rhoVVscheme=4*countV/normscheme
#the following 4 factor is due to the fact that Id and V are measured with 22.5
normconstant = 4*normconstant
normscheme = 4* normscheme
resultdata.update({"NormConstant": normconstant, "NormScheme": normscheme})
print("rhoHH = ", rhoHH)
print("rhoVV = ", rhoVV)

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Re(VH)
#measurement of RL
print("Measuring RL for Re(VH)")
CRLVH= measure(rot1Angle90, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
resultdata.update({"CRLVH": CRLVH})
print("Counts for RL for Re(VH) = ", CRLVH, "\tNormalized to diagonal = ", CRLVH/normconstant, "\tNormalized to scheme = ", CRLVH/normscheme)
print("Counts for RL for Re(VH) = ", CRLVH, "\tNormalized to diagonal = ", CRLVH/normconstant, "\tNormalized to scheme = ", CRLVH/normscheme, file = outputFile)

#measurement of RR
print("Measuring RR for Re(VH)")
CRRVH= measure(rot1Angle90, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
resultdata.update({"CRRVH": CRRVH})
print("Counts for RR for Re(VH) = ", CRRVH, "\tNormalized to diagonal = ", CRRVH/normconstant, "\tNormalized to scheme = ", CRRVH/normscheme)
print("Counts for RR for Re(VH) = ", CRRVH, "\tNormalized to diagonal = ", CRRVH/normconstant, "\tNormalized to scheme = ", CRRVH/normscheme, file = outputFile)

#measurement of LR
print("Measuring LR for Re(VH)")
CLRVH= measure(rot1Angle270, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
resultdata.update({"CLRVH": CLRVH})
print("Counts for LR for Re(VH) = ", CLRVH, "\tNormalized to diagonal = ", CLRVH/normconstant, "\tNormalized to scheme = ", CLRVH/normscheme)
print("Counts for LR for Re(VH) = ", CLRVH, "\tNormalized to diagonal = ", CLRVH/normconstant, "\tNormalized to scheme = ", CLRVH/normscheme, file = outputFile)

#measurement of LL
print("Measuring LL for Re(VH)")
CLLVH = measure(rot1Angle270, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
resultdata.update({"CLLVH": CLLVH})
print("Counts for LL for Re(VH) = ", CLLVH, "\tNormalized to diagonal = ", CLLVH/normconstant, "\tNormalized to scheme = ", CLLVH/normscheme)
print("Counts for LL for Re(VH) = ", CLLVH, "\tNormalized to diagonal = ", CLLVH/normconstant, "\tNormalized to scheme = ", CLLVH/normscheme, file = outputFile)

#extraction of Re(VH)
rerhoVH=(CRLVH+CLRVH-CRRVH-CLLVH)/normconstant
rerhoVHscheme = (CRLVH+CLRVH-CRRVH-CLLVH)/normscheme
print("rerhoVH = ", rerhoVH)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
#measurement of Im(VH)
#measurement of AL
print("Measuring AL for Im(VH)")
CALVH = measure(rot1Angle180, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
resultdata.update({"CALVH": CALVH})
print("Counts for AL for Im(VH) = ", CALVH, "\tNormalized to diagonal = ", CALVH/normconstant, "\tNormalized to scheme = ", CALVH/normscheme)
print("Counts for AL for Im(VH) = ", CALVH, "\tNormalized to diagonal = ", CALVH/normconstant, "\tNormalized to scheme = ", CALVH/normscheme, file = outputFile)

#measurement of AR
print("Measuring AR for Im(VH)")
CARVH= measure(rot1Angle180, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
resultdata.update({"CARVH": CARVH})
print("Counts for AR for Im(VH) = ", CARVH, "\tNormalized to diagonal = ", CARVH/normconstant, "\tNormalized to scheme = ", CARVH/normscheme)
print("Counts for AR for Im(VH) = ", CARVH, "\tNormalized to diagonal = ", CARVH/normconstant, "\tNormalized to scheme = ", CARVH/normscheme, file = outputFile)

#measurement of DR
print("Measuring DR for Im(VH)")
CDRVH= measure(rot1Angle0, rot2Angle270, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
resultdata.update({"CDRVH": CDRVH})
print("Counts for DR for Im(VH) = ", CDRVH, "\tNormalized to diagonal = ", CDRVH/normconstant, "\tNormalized to scheme = ", CDRVH/normscheme)
print("Counts for DR for Im(VH) = ", CDRVH, "\tNormalized to diagonal = ", CDRVH/normconstant, "\tNormalized to scheme = ", CDRVH/normscheme, file = outputFile)

#measurement of DL
print("Measuring DL for Im(VH)")
CDLVH= measure(rot1Angle0, rot2Angle90, rotHWPAngle45, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
resultdata.update({"CDLVH": CDLVH})
print("Counts for DL for Im(VH) = ", CDLVH, "\tNormalized to diagonal = ", CDLVH/normconstant, "\tNormalized to scheme = ", CDLVH/normscheme)
print("Counts for DL for Im(VH) = ", CDLVH, "\tNormalized to diagonal = ", CDLVH/normconstant, "\tNormalized to scheme = ", CDLVH/normscheme, file = outputFile)

#extraction of Im(VH)
imrhoVH=(CDLVH-CDRVH+CARVH-CALVH)/normconstant 
imrhoVHscheme=(CDLVH-CDRVH+CARVH-CALVH)/normscheme 
print("imrhoVH = ", imrhoVH)  

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Re(HV)
#measurement of LL
print("Measuring LL for Re(HV)")
CLLHV = measure(rot1Angle90, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage90)
resultdata.update({"CLLHV": CLLHV})
print("Counts for LL for Re(HV) = ", CLLHV, "\tNormalized to diagonal = ", CLLHV/normconstant, "\tNormalized to scheme = ", CLLHV/normscheme)
print("Counts for LL for Re(HV) = ", CLLHV, "\tNormalized to diagonal = ", CLLHV/normconstant, "\tNormalized to scheme = ", CLLHV/normscheme, file = outputFile)

#measurement of LR
print("Measuring LR for Re(HV)")
CLRHV= measure(rot1Angle90, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage90, lcc2Voltage270)
resultdata.update({"CLRHV": CLRHV})
print("Counts for LR for Re(HV) = ", CLRHV, "\tNormalized to diagonal = ", CLRHV/normconstant, "\tNormalized to scheme = ", CLRHV/normscheme)
print("Counts for LR for Re(HV) = ", CLRHV, "\tNormalized to diagonal = ", CLRHV/normconstant, "\tNormalized to scheme = ", CLRHV/normscheme, file = outputFile)

#measurement of RR
print("Measuring RR for Re(HV)")
CRRHV= measure(rot1Angle270, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage270)
resultdata.update({"CRRHV": CRRHV})
print("Counts for RR for Re(HV) = ", CRRHV, "\tNormalized to diagonal = ", CRRHV/normconstant, "\tNormalized to scheme = ", CRRHV/normscheme)
print("Counts for RR for Re(HV) = ", CRRHV, "\tNormalized to diagonal = ", CRRHV/normconstant, "\tNormalized to scheme = ", CRRHV/normscheme, file = outputFile)

#measurement of RL
print("Measuring RL for Re(HV)")
CRLHV= measure(rot1Angle270, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage270, lcc2Voltage90)
resultdata.update({"CRLHV": CRLHV})
print("Counts for RL for Re(HV) = ", CRLHV, "\tNormalized to diagonal = ", CRLHV/normconstant, "\tNormalized to scheme = ", CRLHV/normscheme)
print("Counts for RL for Re(HV) = ", CRLHV, "\tNormalized to diagonal = ", CRLHV/normconstant, "\tNormalized to scheme = ", CRLHV/normscheme, file = outputFile)

#extraction of Re(HV)
rerhoHV=(CRLHV+CLRHV-CRRHV-CLLHV)/normconstant
rerhoHVscheme=(CRLHV+CLRHV-CRRHV-CLLHV)/normscheme
print("rerhoHV = ", rerhoHV)

print("\n\n\n")
print("\n\n\n", file = outputFile)

#measurement of Im(HV)
#measurement of AL
print("Measuring AL for Im(HV)")
CALHV = measure(rot1Angle180, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage90)
resultdata.update({"CALHV": CALHV})
print("Counts for AL for Im(HV) = ", CALHV, "\tNormalized to diagonal = ", CALHV/normconstant, "\tNormalized to scheme = ", CALHV/normscheme)
print("Counts for AL for Im(HV) = ", CALHV, "\tNormalized to diagonal = ", CALHV/normconstant, "\tNormalized to scheme = ", CALHV/normscheme, file = outputFile)

#measurement of AR
print("Measuring AR for Im(HV)")
CARHV= measure(rot1Angle180, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage180, lcc2Voltage270)
resultdata.update({"CARHV": CARHV})
print("Counts for AR for Im(HV) = ", CARHV, "\tNormalized to diagonal = ", CARHV/normconstant, "\tNormalized to scheme = ", CARHV/normscheme)
print("Counts for AR for Im(HV) = ", CARHV, "\tNormalized to diagonal = ", CARHV/normconstant, "\tNormalized to scheme = ", CARHV/normscheme, file = outputFile)

#measurement of DR
print("Measuring DR for Im(HV)")
CDRHV= measure(rot1Angle0, rot2Angle270, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage270)
resultdata.update({"CDRHV": CDRHV})
print("Counts for DR for Im(HV) = ", CDRHV, "\tNormalized to diagonal = ", CDRHV/normconstant, "\tNormalized to scheme = ", CDRHV/normscheme)
print("Counts for DR for Im(HV) = ", CDRHV, "\tNormalized to diagonal = ", CDRHV/normconstant, "\tNormalized to scheme = ", CDRHV/normscheme, file = outputFile)

#measurement of DL
print("Measuring DL for Im(HV)")
CDLHV= measure(rot1Angle0, rot2Angle90, rotHWPAngle0, rotQWPAngle0, lcc1Voltage0, lcc2Voltage90)
resultdata.update({"CDLHV": CDLHV})
print("Counts for DL for Im(HV) = ", CDLHV, "\tNormalized to diagonal = ", CDLHV/normconstant, "\tNormalized to scheme = ", CDLHV/normscheme)
print("Counts for DL for Im(HV) = ", CDLHV, "\tNormalized to diagonal = ", CDLHV/normconstant, "\tNormalized to scheme = ", CDLHV/normscheme, file = outputFile)

#extraction of Im(HV)
imrhoHV=(CDLHV-CDRHV+CARHV-CALHV)/normconstant
imrhoHVscheme=(CDLHV-CDRHV+CARHV-CALHV)/normscheme
print("imrhoHV = ", imrhoHV)

print("\n\n\n")
print("\n\n\n", file = outputFile)
        
print("Finished all measurements\n\n")

print("\n\n\n")
print("\n\n\n", file = outputFile)

result=qutip.Qobj([[rhoHH , rerhoHV+imrhoHV*1j],[rerhoVH+imrhoVH*1j, rhoVV]])
resquad=result**2
purity= resquad.tr()

resultscheme=qutip.Qobj([[rhoHHscheme , rerhoHVscheme+imrhoHVscheme*1j],[rerhoVHscheme+imrhoVHscheme*1j, rhoVVscheme]])
resquadscheme=resultscheme**2
purityscheme= resquadscheme.tr()

#save qobjs
qutip.qsave([result, resquad, resultscheme, resquadscheme], outputfilename[:-4])

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