# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 11:42:16 2017

@author: Giulio Foletto
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from math import log10, floor
import sys
from prettytable import PrettyTable
import logging
import traceback
import json
import glob
import os
import datetime

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

def Analyzefile(filename, filenamemobile ="", fixedpower=0):
    if filename[-4:]!=".npz":
        filename +=".npz"
    data = np.load(filename)
    position = data['pos']
    power = data['count']
    datasize= power.size
    hasmobile=False
    if filenamemobile !="":
        hasmobile=True
        if filenamemobile[-4:]!=".npz":
            filenamemobile +=".npz"
        data = np.load(filenamemobile)
        mobilepower = data['count']
        
    print("Analyzing ", filename)
    if hasmobile:
        print("with ", filenamemobile, " and ", fixedpower)
    
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
            
    print(posreduced[np.argmax(vis)], "\t", np.max(vis))
    print(posreduced[np.argmax(viscorrected)], "\t", np.max(viscorrected))
        
    if plot:
        fig=plt.figure()
        ax=fig.add_subplot(121)
        ax.plot(posreduced, vis, "r.")
        ax2=fig.add_subplot(122)
        ax2.plot(posreduced, viscorrected, "b.")
        fig2=plt.figure(2)
        ax3=fig2.add_subplot(121)
        ax3.plot(position, power, "r.")
        ax4=fig2.add_subplot(122)
        ax4.plot(posreduced, mobilepower, "b.")
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
    elif len(sys.argv) ==4:
        filename = str(sys.argv[1])
        filenamemobile = str(sys.argv[2])
        fixedpower = sys.argv[3]
        Analyzefile(filename, filenamemobile, float(fixedpower))
    else:
        print("wrong input")
        filename=""
    
    
elif mode == "folder":
    path = str(sys.argv[sys.argv.index("folder")+1])
    allFiles = glob.glob(path + "/*.npz")  # List of files' name
    plot = False
    for file in allFiles:
        Analyzefile(file)
    