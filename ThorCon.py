# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 14:27:11 2017

@author: Giulio Foletto
"""

from enum import Enum
import thorpy
import aptlib
import time

from thorpy.port import Port
from serial.tools.list_ports import comports

def discoverPort(SN):
    serial_ports = [(x[0], x[1], dict(y.split('=', 1) for y in x[2].split(' ') if '=' in y)) for x in comports()]
    port_candidates = [x[0] for x in serial_ports if x[2].get('SER', None) == SN]
    if len(port_candidates==1):
        return port_candidates[0]
    else:
        raise ValueError("No device with serial number "+SN)

class ThorConType(Enum):
    APT=1
    KIN=2

class ThorCon:
    #this class wraps thorpy and aptlib
    def __init__(self, SN):
        SN=str(SN)
        if SN[:2]=="27":
            self.type=ThorConType.KIN
            port= discoverPort(SN)
            p=Port.Create(port, SN)
            found_stages=p.get_stages().values()
            stages=list(found_stages)
            self.con=stages[0]
        else:
            self.type=ThorConType.APT
            self.con=aptlib.PRM1(serial_number=SN)
            
    def goto(self, pos, channel=0, wait=True):
        if self.type==ThorConType.APT:
            self.con.goto(pos, channel, wait)
        elif self.type==ThorConType.KIN:
            self.con.position=pos
            if wait:
                while not self.con.status_settled:
                    time.sleep(0.1)
            
    def move(self, dist, channel=0, wait=True):
        if self.type==ThorConType.APT:
            self.con.move(dist, channel, wait)
        elif self.type==ThorConType.KIN:
            curpos = self.con.position
            newpos=curpos+dist
            self.con.position=newpos
            if wait:
                while not self.con.status_settled:
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
        
            
    
        
            
            
        