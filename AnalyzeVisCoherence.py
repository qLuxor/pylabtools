# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 11:42:16 2017

@author: Giulio Foletto
"""

import numpy as np
import matplotlib.pyplot as plt
from math import log10, floor
import sys
import glob

#function to format output of number
def round_to_num(x, num):
    if x ==0:
        x=1e-10
    return str(round(x, -int(floor(log10(abs(x)))) +(num-1)))

def visibility(arr):
    minvalue = np.min(arr)
    maxvalue = np.max(arr)
    return (maxvalue-minvalue)/(maxvalue+minvalue)


#function that returns the position of the value that preceeds the crossing 
def find_crossing(array, value):
    for i in range(array.size-1):
        if (array[i] <= value and array[i+1]> value) or (array[i]>= value and array[i+1]< value):
            return i
    return -1

#function that defines a parabola with vertex in x0
def parabola(x, a, x0, h):
    return a*(x-x0)**2+h

def stline(x, m, q):
    return m*x+q

def interceptstline(y,m,q):
    return (y-q)/m

def align_yaxis(ax1, v1, ax2, v2, y2min, y2max):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1."""

    """where y2max is the maximum value in your secondary plot. I haven't
     had a problem with minimum values being cut, so haven't set this. This
     approach doesn't necessarily make for axis limits at nice near units,
     but does optimist plot space"""

    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny, maxy = ax2.get_ylim()
    scale = 1
    while scale*(maxy+dy) < y2max:
        scale += 0.05
    ax2.set_ylim(scale*(miny+dy), scale*(maxy+dy))

def Analyzefile(filename, hasmobile=False, filenamemobile ="", fixedpower=0, dataset = "", coefficient=1):
    dataset.lower()
    if (dataset !="a" and dataset!="b"):
        dataset = ""
    if filename[-4:]!=".npz":
        filename +=".npz"
    data = np.load(filename)
    position = data['pos']
    power = data['count'+dataset]
    power *=coefficient
    datasize= power.size
    reducedsize=datasize//10
    posreduced=np.zeros(reducedsize)
    if filenamemobile !="":
        if filenamemobile[-4:]!=".npz":
            filenamemobile +=".npz"
        data = np.load(filenamemobile)
        mobilepower = data['count'+dataset]
        mobilepower *=coefficient
        while mobilepower.size>reducedsize:
            mobilepower=mobilepower[:-1]
        fixedpower*=coefficient
         
    if hasmobile:
        print("Analyzing ", filename, " with mobile power ", filenamemobile, " and fixed power ", fixedpower)
    else:
        print("Analyzing ", filename)
    
    if subtract:
        minimum= np.min(power)
        if background > 1e-10:
            minimum = min(minimum, background)
        for i in range(datasize):
            power[i]-=minimum
     
    
    
    vis=np.zeros(reducedsize)
    deltastep=position[10]-position[0]
    for i in range(0, reducedsize):
        posreduced[i]=position[i*10]+deltastep
        vis[i]=visibility(power[i*10:(i+1)*10])
        
    if hasmobile:
        viscorrected=np.zeros(reducedsize)
        for i in range(0, reducedsize):
            viscorrected[i]=vis[i]/(2*np.sqrt(fixedpower*mobilepower[i])/(fixedpower+mobilepower[i]))
    
    posmaxvis=posreduced[np.argmax(vis)]
    print("Max raw visibility = ",np.max(vis), " at ", posreduced[np.argmax(vis)] )
    if hasmobile:
        print("Max corr visibility = ",np.max(viscorrected), " at ", posreduced[np.argmax(viscorrected)] )
    posdiff=np.zeros(datasize)
    for i in range(0, datasize):
        posdiff[i]=2*(position[i]-posmaxvis)
    posdiffreduced=np.zeros(reducedsize)
    for i in range(0, reducedsize):
        posdiffreduced[i]=2*(posreduced[i]-posmaxvis)
        
    if plot:
        fig=plt.figure(1)
        fig2=plt.figure(2)
        fig3=plt.figure(3)
        if hasmobile:
            ax=fig.add_subplot(121)
            ax.plot(posdiffreduced, vis, "r.")
            ax.set_xlabel("OPL (mm)")
            ax.set_ylabel("Visibility")
            ax.set_title("Raw Visibility")
            ax2=fig.add_subplot(122)
            ax2.plot(posdiffreduced, viscorrected, "b.")
            ax2.set_xlabel("OPL (mm)")
            ax2.set_ylabel("Visibility")
            ax2.set_title("Corrected Visibility")
            ax3=fig2.add_subplot(121)
            ax3.plot(position, power, "r.")
            ax3.set_xlabel("LinStage position (mm)")
            ax3.set_ylabel("Counts per second")
            ax3.set_title("Interference")
            ax4=fig2.add_subplot(122)
            ax4.plot(posreduced, mobilepower, "b.")
            ax4.set_xlabel("LinStage position (mm)")
            ax4.set_ylabel("Counts per second")
            ax4.set_title("Mobile arm")
        else:
            ax=fig.add_subplot(111)
            ax.plot(posdiffreduced, vis, "r.")
            ax.set_xlabel("OPL (mm)")
            ax.set_ylabel("Visibility")
            ax.set_title("Raw Visibility")
            ax3=fig2.add_subplot(111)
            ax3.plot(position, power, "r.")
            ax3.set_xlabel("LinStage position (mm)")
            ax3.set_ylabel("Counts per second")
            ax3.set_title("Interference")
        ax5=fig3.add_subplot(111)
        ax5.plot(posdiff, power, "b.")
        ax5.set_xlabel("OPL (mm)")
        ax5.set_ylabel("Counts per second")
        ax6=ax5.twinx()
        ax6.plot(posdiffreduced, viscorrected, "r-")
        ax6.axhline(np.exp(-1), color="0.80")
        ax6.set_ylabel(r'Coefficient $\gamma$')
        align_yaxis(ax5, np.mean(power), ax6, 0,-1,1)
        plt.show()

if "subtract" in sys.argv:
    subtract = True
    background = float(sys.argv[sys.argv.index("subtract")+1])
else:
    subtract = False
    
if "noplot" in sys.argv:
    plot= False
else:
    plot=True
    
if "folder" in sys.argv:
    mode = "folder"
else:
    mode="file"

if "multiply" in sys.argv:
    coefficient=float(sys.argv[sys.argv.index("multiply")+1])
else:
    coefficient=1
    
if "mobile" in sys.argv and "fixed" in sys.argv:
    hasmobile = True
    filenamemobile=str(sys.argv[sys.argv.index("mobile")+1])
    fixedpower=float(sys.argv[sys.argv.index("fixed")+1])
else:
    hasmobile=False 
    filenamemobile =""
    fixedpower=0
    
if "dataset" in sys.argv:
    dataset=str(sys.argv[sys.argv.index("mobile")+1])
else:
    dataset =""

if mode == "file":
    #inizialization of data
    if len(sys.argv) >1:
        filename = str(sys.argv[1])
        Analyzefile(filename, hasmobile=hasmobile, filenamemobile=filenamemobile, fixedpower=float(fixedpower), dataset=dataset, coefficient=coefficient)
    else:
        print("wrong input")
        filename=""
    
    
elif mode == "folder":
    path = str(sys.argv[sys.argv.index("folder")+1])
    allFiles = glob.glob(path + "/*.npz")  # List of files' name
    plot = False
    for file in allFiles:
        Analyzefile(file)
    
