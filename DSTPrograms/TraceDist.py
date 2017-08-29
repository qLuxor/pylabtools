# -*- coding: utf-8 -*-
"""
Created on Sun May  7 21:18:57 2017

@author: Giulio Foletto
"""

import qutip
import sys

if len(sys.argv) ==5:
    inputfilenameA = str(sys.argv[1])
    indexA = int(sys.argv[2])
    inputfilenameB = str(sys.argv[3])
    indexB = int(sys.argv[4])
    if inputfilenameA[-3:]==".qu":
        inputfilenameA = inputfilenameA[:-3]
    if inputfilenameB[-3:]==".qu":
        inputfilenameB = inputfilenameB[:-3]
    
    listA=qutip.qload(inputfilenameA)
    A=listA[indexA]
    listB=qutip.qload(inputfilenameB)
    B=listB[indexB]
elif len(sys.argv) ==4:
    inputfilename = str(sys.argv[1])
    indexA = int(sys.argv[2])
    indexB = int(sys.argv[3])
    if inputfilename[-3:]==".qu":
        inputfilename = inputfilename[:-3]
    
    mylist=qutip.qload(inputfilename)
    A=mylist[indexA]
    B=mylist[indexB]

print("Loaded two objects")
print(A)
print(B)

result = qutip.tracedist(A, B)
print("The trace distance between them is")
print(result)