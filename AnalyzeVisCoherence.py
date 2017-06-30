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

def Analyzefile(filename, filenamemobile ="", fixedpower=0, mode = ""):
    mode.lower()
    if (mode !="a" and mode!="b"):
        mode = ""
    if filename[-4:]!=".npz":
        filename +=".npz"
    data = np.load(filename)
    position = data['pos']
    power = data['count'+mode]
    datasize= power.size
    hasmobile=False
    if filenamemobile !="":
        hasmobile=True
        if filenamemobile[-4:]!=".npz":
            filenamemobile +=".npz"
        data = np.load(filenamemobile)
        mobilepower = data['count'+mode]
         
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
     
    
    reducedsize=datasize//10
    posreduced=np.zeros(reducedsize)
    vis=np.zeros(reducedsize)
    for i in range(0, reducedsize):
        posreduced[i]=position[i*10]
        vis[i]=visibility(power[i*10:(i+1)*10])
        
    if hasmobile:
        viscorrected=np.zeros(reducedsize)
        for i in range(0, reducedsize):
            viscorrected[i]=vis[i]/(2*np.sqrt(fixedpower*mobilepower[i])/(fixedpower+mobilepower[i]))
    
    posmaxvis=posreduced[np.argmax(vis)]
    print("Max raw visibility = ",np.max(vis), " at ", posreduced[np.argmax(vis)] )
    print("Max corr visibility = ",np.max(viscorrected), " at ", posreduced[np.argmax(viscorrected)] )
    posdiff=np.zeros(reducedsize)
    for i in range(0, reducedsize):
        posdiff[i]=2*(posreduced[i]-posmaxvis)
        
    if plot:
        fig=plt.figure(1)
        fig2=plt.figure(2)
        if hasmobile:
            ax=fig.add_subplot(121)
            ax.plot(posdiff, vis, "r.")
            ax.set_xlabel("OPL (mm)")
            ax.set_ylabel("Visibility")
            ax.set_title("Raw Visibility")
            ax2=fig.add_subplot(122)
            ax2.plot(posdiff, viscorrected, "b.")
            ax2.set_xlabel("OPL (mm)")
            ax2.set_ylabel("Visibility")
            ax2.set_title("Corrected Visibility")
            ax3=fig2.add_subplot(121)
            ax3.plot(position, power, "r.")
            ax3.set_xlabel("LinStage position (mm)")
            ax3.set_ylabel("Power")
            ax3.set_title("Interference")
            ax4=fig2.add_subplot(122)
            ax4.plot(posreduced, mobilepower, "b.")
            ax4.set_xlabel("LinStage position (mm)")
            ax4.set_ylabel("Power")
            ax4.set_title("Mobile arm")
        else:
            ax=fig.add_subplot(111)
            ax.plot(posdiff, vis, "r.")
            ax.set_xlabel("OPL (mm)")
            ax.set_ylabel("Visibility")
            ax.set_title("Raw Visibility")
            ax3=fig2.add_subplot(111)
            ax3.plot(position, power, "r.")
            ax3.set_xlabel("LinStage position (mm)")
            ax3.set_ylabel("Power")
            ax3.set_title("Interference")
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
    
if "skim" in sys.argv:
    skim = True
else:
    skim=False 
    
if "windowsize" in sys.argv:
    windowsize = float(sys.argv[sys.argv.index("windowsize")+1])
else:
    windowsize=0.5 

if mode == "file":
    hasmobile=False
    #inizialization of data
    if len(sys.argv) ==2:
        filename = str(sys.argv[1])
        Analyzefile(filename)
    elif len(sys.argv) ==3:
        filename = str(sys.argv[1])
        mode = str(sys.argv[2])
        Analyzefile(filename, mode =mode)
    elif len(sys.argv) ==4:
        filename = str(sys.argv[1])
        filenamemobile = str(sys.argv[2])
        fixedpower = sys.argv[3]
        Analyzefile(filename, filenamemobile, float(fixedpower))
    elif len(sys.argv) ==5:
        filename = str(sys.argv[1])
        filenamemobile = str(sys.argv[2])
        fixedpower = sys.argv[3]
        mode = str(sys.argv[4])
        Analyzefile(filename, filenamemobile, float(fixedpower), mode=mode)
    else:
        print("wrong input")
        filename=""
    
    
elif mode == "folder":
    path = str(sys.argv[sys.argv.index("folder")+1])
    allFiles = glob.glob(path + "/*.npz")  # List of files' name
    plot = False
    for file in allFiles:
        Analyzefile(file)
    