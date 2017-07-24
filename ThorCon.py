# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 14:27:11 2017

@author: Giulio Foletto
"""

from enum import Enum
import sys
sys.path.append('..')
import thorpy
import aptlib
import time

from thorpy.comm.port import Port
from serial.tools.list_ports import comports

def discoverPort(serial_number):
    serial_ports = [(x[0], x[1], dict(y.split('=', 1) for y in x[2].split(' ') if '=' in y)) for x in comports()]
    port_candidates = [x[0] for x in serial_ports if x[2].get('SER', None) == serial_number]
    if len(port_candidates)==1:
        return port_candidates[0]
    else:
        raise ValueError("No device with serial number "+serial_number)

class ThorConType(Enum):
    APT=1
    KIN=2

class ThorCon:
    #this class wraps thorpy and aptlib
    def __init__(self, serial_number):
        serial_number=str(serial_number)
        if serial_number[:2]=="27":
            self.type=ThorConType.KIN
            port= discoverPort(serial_number)
            self.p=Port.create(port, serial_number)
            found_stages=self.p.get_stages().values()
            stages=list(found_stages)
            self.con=stages[0]
        else:
            self.type=ThorConType.APT
            self.con=aptlib.PRM1(serial_number=int(serial_number))
            
    def goto(self, pos, channel=0, wait=True):
        pos=float(pos)
        if self.type==ThorConType.APT:
            self.con.goto(pos, channel, wait)
        elif self.type==ThorConType.KIN:
            self.con.position=pos
            if wait:
                while abs(self.con.position-pos)>0.01:
                    time.sleep(0.1)
            
    def move(self, dist, channel=0, wait=True):
        dist=float(dist)
        if self.type==ThorConType.APT:
            self.con.move(dist, channel, wait)
        elif self.type==ThorConType.KIN:
            curpos = self.con.position
            newpos=curpos+dist
            self.con.position=newpos
            if wait:
                while abs(self.con.position-newpos)>0.01:
                    time.sleep(0.1)
                    
    def home(self, channel=0, force = False):
        if self.type==ThorConType.APT:
            self.con.home(channel)
        elif self.type==ThorConType.KIN:
            self.con.home(force)
            
    def position(self, channel=0):
        if self.type==ThorConType.APT:
            return self.con.position()
        elif self.type==ThorConType.KIN:
            return self.con.position
        
    def close(self):
        if self.type==ThorConType.APT:
            return self.con.close()
        elif self.type==ThorConType.KIN:
            #del self.con
            del self.p
            return
        
            
    
        
            
            
        
