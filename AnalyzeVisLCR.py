# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 20:02:17 2017

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

#function to format output of number
def round_to_num(x, num):
    return str(round(x, -int(floor(log10(abs(x)))) +(num-1)))


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

#inizialization of data
if len(sys.argv) >0:
    filename = str(sys.argv[1])
else:
    filename =""
data = np.load(filename)
voltage = data['voltage']
power = data['count']

posminimum = np.argmin(power)
if posminimum < power.size/2:
    voltage1=voltage[0:voltage.size//2]
    voltage2=voltage[voltage.size//2:]
    power1=power[0:power.size//2]
    power2=power[power.size//2:]
    label1='Pos1'
    label2='Pos2'
else:
    voltage2=voltage[0:voltage.size//2]
    voltage1=voltage[voltage.size//2:]
    power2=power[0:power.size//2]
    power1=power[power.size//2:]
    label1='Pos2'
    label2='Pos1'

#raw max and min
minimum=np.min(power1)
maximum=np.max(power2)
rawvisibility= (maximum-minimum)/(maximum+minimum)

#voltages corresponding to max and min
voltminimum =voltage1[np.argmin(power1)]
voltmaximum =voltage2[np.argmax(power2)]

#Output of raw results
numSignificantDigits=4
print("\n\nRaw data")
t= PrettyTable(["", "Voltage", "Power"])
t.add_row(["Maximum (0)", round_to_num(voltmaximum, numSignificantDigits),round_to_num(maximum, numSignificantDigits)] )
t.add_row(["Minumum (pi)",round_to_num(voltminimum, numSignificantDigits),round_to_num(minimum, numSignificantDigits)] )
print(t)
print("Raw visibility = "+ round_to_num(rawvisibility,numSignificantDigits))

#halfwidth of the fit range
windowsize=0.5

#definition of the range in terms of position
lbound1= min(find_crossing(voltage1, voltminimum-windowsize),find_crossing(voltage1, voltminimum+windowsize) )
ubound1= max(find_crossing(voltage1, voltminimum-windowsize),find_crossing(voltage1, voltminimum+windowsize) )

#subarrays that will be used in the fit
voltage1fit=voltage1[lbound1:ubound1]
power1fit=power1[lbound1:ubound1]

#same as above 
lbound2=min(find_crossing(voltage2, voltmaximum-windowsize),find_crossing(voltage2, voltmaximum+windowsize))
ubound2=max(find_crossing(voltage2, voltmaximum-windowsize),find_crossing(voltage2, voltmaximum+windowsize))
voltage2fit=voltage2[lbound2:ubound2]
power2fit=power2[lbound2:ubound2]

#actual fit
isZeroFoundWithFit = False
isPiFoundWithFit= False
try:
    if voltage1fit.size>=3:
        popt1, pcov1 = curve_fit(parabola, voltage1fit, power1fit)
        fitminimum = popt1[2]
        isPiFoundWithFit=True
except Exception as e:
    logging.error(traceback.format_exc())
try:
    if voltage2fit.size >=2:
        popt2, pcov2 = curve_fit(parabola, voltage2fit, power2fit)
        fitmaximum = popt2[2]
        isZeroFoundWithFit=True
except Exception as e:
        logging.error(traceback.format_exc())

#search for the other two useful points
halfpoint= (maximum+minimum)/2
isHalfpointFoundWithFit=False
if isZeroFoundWithFit and isPiFoundWithFit:
    halfpoint= (fitmaximum+fitminimum)/2
    isHalfpointFoundWithFit=True
    
#halfwidth of the fit range, in positions
datawindowsize=4

#preparation of arrays
lbound1r=4+ min(find_crossing(power1[4:], halfpoint)-datawindowsize,find_crossing(power1[4:], halfpoint)+datawindowsize )
ubound1r= 4+max(find_crossing(power1[4:], halfpoint)-datawindowsize,find_crossing(power1[4:], halfpoint)+datawindowsize )
voltage1fitr=voltage1[lbound1r:ubound1r]
power1fitr=power1[lbound1r:ubound1r]

lbound2r= min(find_crossing(power2, halfpoint)-datawindowsize,find_crossing(power2, halfpoint)+datawindowsize)
ubound2r= max(find_crossing(power2, halfpoint)-datawindowsize,find_crossing(power2, halfpoint)+datawindowsize )
voltage2fitr=voltage2[lbound2r:ubound2r]
power2fitr=power2[lbound2r:ubound2r]

#actual fit
isPi2FoundWithFit = False
is3Pi2FoundWithFit= False
try:
    if voltage1fitr.size>=2:
        popt1r, pcov1r = curve_fit(stline, voltage1fitr, power1fitr)
        volthalfpi1=interceptstline(halfpoint, popt1r[0], popt1r[1])
        is3Pi2FoundWithFit=True
except Exception as e:
    logging.error(traceback.format_exc())
try:
    if voltage2fitr.size>=2:
        popt2r, pcov2r = curve_fit(stline, voltage2fitr, power2fitr)
        volthalfpi2=interceptstline(halfpoint, popt2r[0], popt2r[1])
        isPi2FoundWithFit = True
except Exception as e:
    logging.error(traceback.format_exc())


#Output of fitted results
print("\n\nFitted data")
tf= PrettyTable(["", "Voltage", "Power"])
if isZeroFoundWithFit:
    tf.add_row(["Maximum (0)", round_to_num(popt2[1], numSignificantDigits),round_to_num(fitmaximum, numSignificantDigits)] )
else:
    tf.add_row(["Maximum (0)", "N/A" ,"N/A"] )
    print ("Could not fit around expected 0")
if isPiFoundWithFit:
    tf.add_row(["Minumum (pi)",round_to_num(popt1[1], numSignificantDigits),round_to_num(fitminimum, numSignificantDigits)] )
else:
    tf.add_row(["Minumum (pi)", "N/A" ,"N/A"] )
    print ("Could not fit around expected pi")
if isPi2FoundWithFit:
    tf.add_row(["Half (pi/2)",round_to_num(volthalfpi2, numSignificantDigits),round_to_num(halfpoint, numSignificantDigits)] )
else: 
    tf.add_row(["Half (pi/2)","N/A",round_to_num(halfpoint, numSignificantDigits)] )
    print ("Could not fit around expected pi/2")
if is3Pi2FoundWithFit:
    tf.add_row(["Half (3pi/2)",round_to_num(volthalfpi1, numSignificantDigits),round_to_num(halfpoint, numSignificantDigits)] )
else:
    tf.add_row(["Half (3pi/2)","N/A",round_to_num(halfpoint, numSignificantDigits)] )
    print ("Could not fit around expected 3pi/2")
print(tf)
if isHalfpointFoundWithFit:
    print("Expected value of power at pi/2 and 3pi/2 was found through fitted max and min")
else:
    print("Expected value of power at pi/2 and 3pi/2 was found through raw max and min")
if isZeroFoundWithFit and isPiFoundWithFit:
    visibility= (fitmaximum-fitminimum)/(fitmaximum+fitminimum)
    print("Visibility = "+ round_to_num(visibility,numSignificantDigits))
else:
    print("Could not find visibility, refer to raw measure")

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('Applied Voltage (V)')
ax.set_ylabel("Power")

plot1,=ax.plot(voltage1, power1, 'bx-', label=label1)
plot2,=ax.plot(voltage2, power2, 'rx-', label=label2)
ax.legend(handles=[plot1, plot2])
if isPiFoundWithFit:
    ax.plot(voltage1fit, parabola(voltage1fit, *popt1), 'red')
if isZeroFoundWithFit:
    ax.plot(voltage2fit, parabola(voltage2fit, *popt2), 'blue')
if is3Pi2FoundWithFit:
    ax.plot(voltage1fitr, stline(voltage1fitr, *popt1r), 'red')
if isPi2FoundWithFit:
    ax.plot(voltage2fitr, stline(voltage2fitr, *popt2r), 'blue')
ax.hlines(halfpoint,0,25,'orange')
plt.show()