#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:44:36 2017

@author: sagnac
"""

import serial
import datetime
import time
import numpy as np

port='/dev/ttyACM1'
baud=9600

#initialize serial
serialobj=serial.Serial()
serialobj.port=port
serialobj.baudrate=baud
serialobj.timeout=1
serialobj.setDTR(False)

#launch serial
serialobj.open()
time.sleep(2)
serialobj.flush()

Filename = 'Temperatures'
Filename += str(datetime.datetime.now())[0:19]
Filename += '.npz'

list_T = []
list_time = []
while(True):
    list_time.append(datetime.datetime.now())
    tempC=serialobj.readline()
    tempC=float(tempC[0:5])
    list_T.append(tempC)
    np.savez(Filename, temp=list_T, time=list_time)
    print(tempC)
    time.sleep(30)
