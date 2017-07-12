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
import datetime
import matplotlib

hastemperature=False
if len(sys.argv) ==2:
    path = str(sys.argv[1])
elif len(sys.argv) ==3:
    path = str(sys.argv[1])
    temperaturesFile=str(sys.argv[2])
    hastemperatures=True
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
timelist=[]

cont=0
hastime= True
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
    if "StartTime" in data:
        timelist.insert(cont, datetime.datetime.strptime(data["StartTime"],"%Y-%m-%d %H:%M:%S.%f"))
        hastime = hastime and True
    elif "ModifiedTime" in data:
        timelist.insert(cont, datetime.datetime.strptime(data["ModifiedTime"],"%Y-%m-%d %H:%M:%S"))
        hastime = hastime and True
    else:
        hastime= False
    
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

if hastemperatures:
    temperatures=np.load(temperaturesFile)
    rawtemplist=temperatures["temp"]
    rawtemptimelist=temperatures["time"]
    
    templist=np.copy(rawtemplist)
    temptimelist=np.copy(rawtemptimelist)
    
    meantemp=np.mean(rawtemplist)
    stdtemp=np.std(rawtemplist)
    for i in range(0, len(rawtemplist)):
        if np.abs(rawtemplist[i]-meantemp)>5*stdtemp:
            templist[i]=meantemp
    for i in range(5, len(templist)):
        lastmean = np.mean(templist[i-5:i])
        thstd = np.std(templist[0:5])
        if np.abs(templist[i]-lastmean)>5*thstd:
            corrfactor=templist[i-1]/templist[i]
            for j in range(i, len(templist)):
                templist[j]=templist[j]*corrfactor
    plottabletemptimes = matplotlib.dates.date2num(temptimelist)
    
fig, ax = plt.subplots()

if hastime:
    plottabletimes = matplotlib.dates.date2num(timelist)
    ax.plot_date(plottabletimes, maxvoltarray, 'bx', label="Max")
    ax.plot_date(plottabletimes, minvoltarray, 'rx', label="Min")
    ax.plot_date(plottabletimes, rawmaxvoltarray, 'gx', label="RawMax")
    ax.plot_date(plottabletimes, rawminvoltarray, 'yx', label="RawMin")
    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter("%H:%M"))
    ax.set_xlabel("Time")
    if hastemperatures:
        ax2=ax.twinx()
        ax2.plot_date(plottabletemptimes, templist, "k.", label="Temp")
        ax2.set_ylabel("Temperature (°C)")
else:
    ax.plot(np.arange(len(allFiles)), maxvoltarray, 'bx-', label="Max")
    ax.plot(np.arange(len(allFiles)), minvoltarray, 'rx-', label="Min")
    ax.plot(np.arange(len(allFiles)), rawmaxvoltarray, 'gx-', label="RawMax")
    ax.plot(np.arange(len(allFiles)), rawminvoltarray, 'yx-', label="RawMin")
    ax.set_xlabel("File index")
    
ax.set_ylabel("Voltage (V)")
ax.grid()
plt.show()
