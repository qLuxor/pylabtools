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

hastemperatures=False
if len(sys.argv) ==2:
    path = str(sys.argv[1])
elif len(sys.argv) ==3:
    path = str(sys.argv[1])
    temperaturesFile=str(sys.argv[2])
    hastemperatures=True
else:
    print("Please insert folder")
    
def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / N 


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
deltaphimaxarray=np.zeros(len(allFiles))
deltaphiminarray=np.zeros(len(allFiles))
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
    else:
        maxvolt=rawmaxvolt
        maxpower=rawmaxpower
    maxvoltarray[cont]=maxvolt
    maxpowerarray[cont]=maxpower
    if data["MinFound"]:
        minvolt=data["MinVolt"]
        minpower=data["MinPower"]
    else:
        minvolt=rawminvolt
        minpower=rawminpower
    minvoltarray[cont]=minvolt
    minpowerarray[cont]=minpower
    if data["MaxFound"] and data["MinFound"]:
        visibility=data["Visibility"]
        visarray[cont]=visibility
    if data["Half1Found"]:
        half1volt=data["Half1Volt"]
    if data["Half2Found"]:
        half2volt=data["Half2Volt"]    
        
    curpowerinmax=data["curpowerinmax"]
    curpowerinmin=data["curpowerinmin"]    
    
    #assuming vis=1
    deltaphimax=np.arccos(2*(curpowerinmax-minpower)/(maxpower-minpower)-1)
    if maxvoltarray[cont]>maxvoltarray[0]:
        deltaphimax *=-1
    deltaphimin=np.arccos(2*(curpowerinmin-minpower)/(maxpower-minpower)-1)-np.pi
    if minvoltarray[cont]>minvoltarray[0]:
        deltaphimin *=-1
        
    deltaphimaxarray[cont]=deltaphimax
    deltaphiminarray[cont]=deltaphimin
    cont +=1
    
#convert time to timedelta objects
timelist=np.array(timelist)
time0=timelist[0]
timelist = timelist-time0

#convert timedeltas to minutes
timelist=np.array([x.total_seconds()/60 for x in timelist])

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
    
    temptime0=temptimelist[0]
    temptimelist= temptimelist-temptime0
    temptimelist=np.array([x.total_seconds()/60 for x in temptimelist])
    
    #running mean
    window_size=1
    if window_size>1 and window_size % 2 ==1:
        templist=running_mean(templist, window_size)
        temptimelist=temptimelist[window_size//2:-(window_size//2)]
    
fig, ax = plt.subplots()
fig2, ax2 = plt.subplots()

if hastime:
    ax.plot(timelist, maxvoltarray, 'bx', label="Max")
    ax.plot(timelist, minvoltarray, 'rx', label="Min")
    ax.plot(timelist, rawmaxvoltarray, 'gx', label="RawMax")
    ax.plot(timelist, rawminvoltarray, 'yx', label="RawMin")
    ax.set_xlabel("Time (minutes)")
    ax2.plot(timelist, deltaphimaxarray, 'bx', label="Near Max")
    ax2.plot(timelist, deltaphiminarray, 'rx', label="Near Min")
    ax2.set_xlabel("Time (minutes)")
    if hastemperatures:
        axtemp=ax.twinx()
        axtemp.plot(temptimelist, templist, "k.", label="Temperature")
        axtemp.set_ylabel("Temperature (°C)")
        axtemp.legend(loc="lower right")
        axtemp2=ax2.twinx()
        axtemp2.plot(temptimelist, templist, "k.", label="Temperature")
        axtemp2.set_ylabel("Temperature (°C)")
        axtemp2.legend(loc="lower right")
    ax.legend(loc="lower left")
    ax2.legend(loc="lower left")
else:
    ax.plot(np.arange(len(allFiles)), maxvoltarray, 'bx-', label="Max")
    ax.plot(np.arange(len(allFiles)), minvoltarray, 'rx-', label="Min")
    ax.plot(np.arange(len(allFiles)), rawmaxvoltarray, 'gx-', label="RawMax")
    ax.plot(np.arange(len(allFiles)), rawminvoltarray, 'yx-', label="RawMin")
    ax.set_xlabel("File index")
    ax2.plot(np.arange(len(allFiles)), deltaphimaxarray, 'bx-', label="Near Max")
    ax2.plot(np.arange(len(allFiles)), deltaphiminarray, 'rx-', label="Near Min")
    ax2.set_xlabel("File index")
    ax.legend(loc="lower left")
    ax2.legend(loc="lower left")
    
ax.set_ylabel("Voltage (V)")
ax.grid()
ax2.set_ylabel("Phase Variation (rad)")
ax2.grid()
plt.show()
