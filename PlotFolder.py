# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:44:07 2017

@author: Giulio Foletto
"""

import sys
import json
import glob
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) >1:
        path = str(sys.argv[1])
else:
    print("Please insert folder")


allFiles = glob.glob(path + "/*.json")  # List of files' names

rawmaxvoltarray=np.zeros(len(allFiles))
rawminvoltarray=np.zeros(len(allFiles))
rawmaxpowerarray=np.zeros(len(allFiles))
rawminpowerarray=np.zeros(len(allFiles))
rawvisarray=np.zeros(len(allFiles))
maxvoltarray=np.zeros(len(allFiles))
minvoltarray=np.zeros(len(allFiles))
maxpowerarray=np.zeros(len(allFiles))
minpowerarray=np.zeros(len(allFiles))
visarray=np.zeros(len(allFiles))

cont=0
for file in allFiles:
    with open(file) as json_settings:
        data = json.load(json_settings)
        json_settings.close()
    rawmaxvolt = data["RawMaxVolt"]
    rawmaxpower= data["RawMaxPower"]
    rawmaxvoltarray[cont]=rawmaxvolt
    rawmaxpowerarray[cont]=rawmaxpower
    rawminvolt = data["RawMinVolt"]
    rawminpower= data["RawMinPower"]
    rawminvoltarray[cont]=rawminvolt
    rawminpowerarray[cont]=rawminpower
    rawvisibility= data["RawVisibility"]
    rawvisarray[cont]=rawvisibility
    
    if data["MaxFound"]:
        maxvolt = data["MaxVolt"]
        maxpower= data["MaxPower"]
        maxvoltarray[cont]=maxvolt
        maxpowerarray[cont]=maxpower
    if data["MinFound"]:
        minvolt=data["MinVolt"]
        minpower=data["MinPower"]
        minvoltarray[cont]=minvolt
        minpowerarray[cont]=minpower
    if data["MaxFound"] and data["MinFound"]:
        visibility=data["Visibility"]
        visarray[cont]=visibility
    if data["Half1Found"]:
        half1volt=data["Half1Volt"]
    if data["Half2Found"]:
        half2volt=data["Half2Volt"]    
    cont +=1
    
fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.set_ylabel("Voltage")

#plot1,=ax.plot(np.arange(len(allFiles)), maxvoltarray, 'bx-', label="Max")
#plot2,=ax.plot(np.arange(len(allFiles)), minvoltarray, 'rx-', label="Min")
plt.plot(np.arange(len(allFiles))*0.1, maxvoltarray, 'bx-', label="Max")
plt.plot(np.arange(len(allFiles))*0.1, minvoltarray, 'rx-', label="Min")
plt.plot(np.arange(len(allFiles))*0.1, rawmaxvoltarray, 'gx-', label="RawMax")
plt.plot(np.arange(len(allFiles))*0.1, rawminvoltarray, 'yx-', label="RawMin")
plt.grid()

plt.show()