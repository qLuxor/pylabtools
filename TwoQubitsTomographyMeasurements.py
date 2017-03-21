# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 12:38:28 2016

@author: luca
"""

import time
import sys
import numpy as np

sys.path.append('..')
import aptlib
sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

# buffer number
bufNum = 0

IntegrationTime = 5.
CoincidenceRadius = 1e-9

# Channel delays
Delays = [0, 0.3, -9.8, -9.1]

# Serial Numbers of APT controllers
SNAliceHWP = 83830445
SNAliceQWP = 83865112
SNBobHWP = 83825706
SNBobQWP = 83865359

# Set off angles of rotators
zeroAngle = {'AliceHWP': 30.5,
             'AliceQWP': 2,
             'BobHWP': 131,
             'BobQWP': 23.5
             }
            
# Measurement configurations: wave plates positions
# Structure of the dictionary: 'BasisName':[HWPangle, QWPangle] angles are in degrees
#MeasurementsConf = {'HV': [0.,0.], 'VH': [45.,0.], 'DA': [22.5, 45.], 'AD': [67.5, 45.], 'RL': [22.5, 0.], 'LR': [67.5, 0.]}
MeasurementsConf = {'HV': [0.,0.], 'DA': [22.5, 45.], 'RL': [22.5, 0.]}

#OrderOfMeasuredBases = ['HV', 'VH', 'DA', 'AD', 'RL', 'LR']
OrderOfMeasuredBases = ['HV', 'DA', 'RL']

# Homing the plates
def HomingWP():
    conAliceHWP.home()
    conAliceQWP.home()
    conBobHWP.home()
    conBobQWP.home()

# Move all rotators to their set off angle    
def MoveToZeroAngle():
    conAliceHWP.goto(float(zeroAngle['AliceHWP']))
    conAliceQWP.goto(float(zeroAngle['AliceQWP']))
    conBobHWP.goto(float(zeroAngle['BobHWP']))
    conBobQWP.goto(float(zeroAngle['BobQWP']))
    
def RotateWP(con, angle, name):
    con.goto(float(zeroAngle[name] + angle))

##############
#   Main code
##############

# Open buffer for data acquisition
ttagBuf = ttag.TTBuffer(bufNum)

# set channel delays
delays = np.zeros(ttagBuf.channels,dtype=np.double)
delays[0] = Delays[0]*1e-9
delays[1] = Delays[1]*1e-9 
delays[2] = Delays[2]*1e-9 
delays[3] = Delays[3]*1e-9 

# Connect APT controllers
conAliceHWP = aptlib.PRM1(serial_number=SNAliceHWP)
conAliceQWP = aptlib.PRM1(serial_number=SNAliceQWP)
conBobHWP = aptlib.PRM1(serial_number=SNBobHWP)
conBobQWP = aptlib.PRM1(serial_number=SNBobQWP)

# Homing plates
HomingWP()
print('Homing DONE')

# Set plates to zero angle
MoveToZeroAngle()
print('Plates to Zero')

# Initialize dictionary to save coincidences
#Measurements = {'HVHV': 0,
#                'HVDA': 0,
#                'HVRL': 0,
#                'DAHV': 0,
#                'DADA': 0,
#                'DARL': 0,
#                'RLHV': 0,
#                'RLDA': 0,
#                'RLRL': 0}
Measurements={}
for Alice in OrderOfMeasuredBases:
    # Move Alice's plates
    RotateWP(conAliceHWP, MeasurementsConf[Alice][0], 'AliceHWP')
    RotateWP(conAliceQWP, MeasurementsConf[Alice][1], 'AliceQWP')
    
    for Bob in OrderOfMeasuredBases:
        # Move Bob's plates
        RotateWP(conBobHWP, MeasurementsConf[Bob][0], 'BobHWP')
        RotateWP(conBobQWP, MeasurementsConf[Bob][1], 'BobQWP')
        print('Bases: Alice', Alice, '  Bob', Bob)
        # Wait integration time + half a second
        time.sleep( IntegrationTime + 1.0 )
        
        #Aquire data, saving coincidences
        cMatrix = ttagBuf.coincidences(IntegrationTime, CoincidenceRadius, -delays)[0:4,0:4]
        
        #RotateWP(conAliceHWP, MeasurementsConf[Alice][0] + 45., 'AliceHWP')
        #RotateWP(conBobHWP, MeasurementsConf[Bob][0] + 45., 'BobHWP')
        
        #c2 = ttagBuf.coincidences(IntegrationTime, CoincidenceRadius, -delays)[0:4,0:4]
        #cMatrix = [c1, c2]
        print(cMatrix)
        #print(cMatrix[0])
        Measurements[Alice+Bob] = cMatrix
        
# Save measurements
np.save('Tomography.npy',Measurements)
print('Measurements saved')

RotateWP(conAliceHWP, 0., 'AliceHWP')
RotateWP(conAliceQWP, 0., 'AliceQWP')
RotateWP(conBobHWP, 0., 'BobHWP')
RotateWP(conBobQWP, 0., 'BobQWP')
