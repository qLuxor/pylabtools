# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import qutip 

import sys
import glob
import numpy as np


if len(sys.argv) >1:
        path = str(sys.argv[1])
else:
    print("Please insert folder")


allFiles = glob.glob(path + "/*.qu")  # List of files' names

print(path)
b=qutip.Bloch()
pointlist=[]
for file in allFiles:
    file =file[:-3]
    allresults= qutip.qload(file)
    sigmax= qutip.sigmax()
    sigmay=qutip.sigmay()
    sigmaz=qutip.sigmaz()
    
    x= (sigmax*allresults[0]).tr()
    y= (sigmay*allresults[0]).tr()
    z= (sigmaz*allresults[0]).tr()
    
    point=(x,y,z)
    pointlist.append(point)
    b.add_points(point)
    
b.show()