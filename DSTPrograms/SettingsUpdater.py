# -*- coding: utf-8 -*-
"""
Created on Mon May  8 22:12:41 2017

@author: Giulio Foletto
"""

import sys
import json

if len(sys.argv) !=4:
    print("Incorrect input")
    sys.exit()

datafilename1=str(sys.argv[1])
datafilename2=str(sys.argv[2])
settingsfilename=str(sys.argv[3])

with open(datafilename1) as jsondata:
    data1 = json.load(jsondata)
    jsondata.close()

with open(datafilename2) as jsondata:
    data2 = json.load(jsondata)
    jsondata.close()

with open(settingsfilename) as jsondata:
    settings = json.load(jsondata)
    jsondata.close()
    
rot1Pos1=settings["rot1Pos1"]
rot1Pos2=settings["rot1Pos2"]
rot2Pos1=settings["rot2Pos1"]
rot2Pos2=settings["rot2Pos2"]

if data1["MaxFound"]:
    int1MaxV=data1["MaxVolt"]
    if data1["MaxPos"]=="Pos1":
        int1MaxPos=rot1Pos1
    elif data1["MaxPos"]=="Pos2":
        int1MaxPos=rot1Pos2
    settings.update({"rot1Angle0": int1MaxPos, "lcc1Voltage0": int1MaxV})
    print("Successfully updated Max in Int1")
    
if data1["MinFound"]:
    int1MinV=data1["MinVolt"]
    if data1["MinPos"]=="Pos1":
        int1MinPos=rot1Pos1
    elif data1["MinPos"]=="Pos2":
        int1MinPos=rot1Pos2
    settings.update({"rot1Angle180": int1MinPos, "lcc1Voltage180": int1MinV})
    print("Successfully updated Min in Int1")
    
if data1["Half1Found"]:
    int1Half1V=data1["Half1Volt"]
    if data1["Half1Pos"]=="Pos1":
        int1Half1Pos=rot1Pos1
    elif data1["Half1Pos"]=="Pos2":
        int1Half1Pos=rot1Pos2
    settings.update({"rot1Angle90": int1Half1Pos, "lcc1Voltage90": int1Half1V}) #changed because of Luca's trick. 270 is the correct value if trust is given to QST, 90 if it is given to scheme
    print("Successfully updated Half1 in Int1")
    
if data1["Half2Found"]:
    int1Half2V=data1["Half2Volt"]
    if data1["Half2Pos"]=="Pos1":
        int1Half2Pos=rot1Pos1
    elif data1["Half2Pos"]=="Pos2":
        int1Half2Pos=rot1Pos2
    settings.update({"rot1Angle90": int1Half2Pos, "lcc1Voltage90": int1Half2V}) #changed because QST is prioritized, change back to 270 if trust is given to scheme
    print("Successfully updated Half2 in Int1")
    
if data2["MaxFound"]:
    int2MaxV=data2["MaxVolt"]
    if data2["MaxPos"]=="Pos1":
        int2MaxPos=rot2Pos1
    elif data2["MaxPos"]=="Pos2":
        int2MaxPos=rot2Pos2
    settings.update({"rot2Angle90": int2MaxPos, "lcc2Voltage90": int2MaxV}) #changed because QST is prioritized, change back to 270 if trust is given to scheme
    print("Successfully updated Max in Int2")
    
if data2["MinFound"]:
    int2MinV=data2["MinVolt"]
    if data2["MinPos"]=="Pos1":
        int2MinPos=rot2Pos1
    elif data2["MinPos"]=="Pos2":
        int2MinPos=rot2Pos2
    settings.update({"rot2Angle270": int2MinPos, "lcc2Voltage270": int2MinV}) #changed because QST is prioritized, change back to 90 if trust is given to scheme
    print("Successfully updated Min in Int2")
    
if data2["Half1Found"] and not data2["Half2Found"]:
    int2Half1V=data2["Half1Volt"]
    if data2["Half1Pos"]=="Pos1":
        int2Half1Pos=rot2Pos1
    elif data2["Half1Pos"]=="Pos2":
        int2Half1Pos=rot2Pos2
    settings.update({"rot2Angle0": int2Half1Pos, "lcc2Voltage0": int2Half1V})
    settings.update({"rot2Angle180": int2Half1Pos, "lcc2Voltage180": int2Half1V})
    print("Successfully updated Half1 in Int2")
    
if data2["Half2Found"] and not data2["Half1Found"]:
    int2Half2V=data2["Half2Volt"]
    if data2["Half2Pos"]=="Pos1":
        int2Half2Pos=rot2Pos1
    elif data2["Half2Pos"]=="Pos2":
        int2Half2Pos=rot2Pos2
    settings.update({"rot2Angle0": int2Half2Pos, "lcc2Voltage0": int2Half2V})
    settings.update({"rot2Angle180": int2Half2Pos, "lcc2Voltage180": int2Half2V})
    print("Successfully updated Half2 in Int2")
    
with open(settingsfilename, 'w') as jsonsettings:
    json.dump(settings, jsonsettings)