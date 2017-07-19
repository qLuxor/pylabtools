#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:44:36 2017

@author: sagnac
"""

import serial
import datetime
import time
import numpy as np

from plotly.graph_objs import Scatter, Data, Stream, Layout, Figure
import plotly.plotly as py

port='/dev/ttyACM0'
baud=9600
stream_id = '8fki3onim7'


#initialize serial
serialobj=serial.Serial()
serialobj.port=port
serialobj.baudrate=baud
serialobj.timeout=1
serialobj.setDTR(False)

#launch serial
serialobj.open()
time.sleep(2)
serialobj.flush()

Filename = 'Temperatures'
Filename += str(datetime.datetime.now())[0:19]
Filename += '.npz'

# Make instance of stream id object 
stream_1 = Stream(
    token=stream_id,  # link stream id to 'token' key
    #maxpoints=200      # keep a max of 200 pts on screen
)

list_T = []
list_time = []
trace1 = Scatter(
    x=list_time,
    y=list_T, 
    stream=stream_1
)
data = Data([trace1])
# Add title to layout object
layout = Layout(title='Temperature Quantum',
    yaxis=dict(
        range=[20, 30]
    )
)

# Make a figure object
fig = Figure(data=data, layout=layout)

# Send fig to Plotly, initialize streaming plot, open new tab
py.iplot(fig, filename='temperature-streaming')
s = py.Stream(stream_id)
# open a connection
s.open()

while(True):
    # read time
    list_time.append(datetime.datetime.now())
    
    # read temperature
    tempC=serialobj.readline()
    tempC=float(tempC[0:5])
    list_T.append(tempC)
    
    # save data
    np.savez(Filename, temp=list_T, time=list_time)
    print(tempC)
    
    # Send data to plot
    s.write(dict(x=list_time[-1], y=list_T[-1]))
    
    # wait    
    time.sleep(30)

s.close()
