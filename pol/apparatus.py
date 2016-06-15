from __future__ import absolute_import

import sys
sys.path.append('../..')
import aptlib

import numpy as np


class Apparatus():
    ''' This class keeps track of the experimental apparatus for the double
    violation of the CHSH inequality. The full apparatus consists of five
    rotators: three for the HWPs of Alice, Bob1 and Bob2, one for the glass and
    one for setting the relative phase of H and V.

    All rotators are subclasses of the PRM1 class, with new methods implementing
    their characteristic behaviour.
    '''

    def __init__(self):
        self.connected = False
        self.alice = None
        self.bob1 = None
        self.bob2 = None
        self.weak = None

    def connect(self,config):
        '''Connect the apparatus according to the information in the config
        dictionary. The dictionary is read from a YAML file with the following
        structure:

        Alice:
            basis:
                serial_number: 'xxxxxxxx'
                zero: xxx
                dirRot: 'CW'/'CCW'
                home: True
        Bob2:
            basis:
            ...
        Bob1:
            basis:
            ...
            meas:
                serial_number: 'xxxxxxxx'
                posMin: xxx
                posMax: xxx
                home: True
        weak:
            serial_number: 'xxxxxxxx'
            home: True

        '''

        if 'Alice' in config:
            A1basis = None
            try:
                if 'basis' in config['Alice']:
                    A1basis = HWP(**config['Alice']['basis'])
                self.alice = Alice(A1basis)
            except:
                self.alice = None
        if 'Bob1' in config:
            B1basis = None
            B1meas = None
            try:
                if 'basis' in config['Bob1']:
                    B1basis = HWP(**config['Bob1']['basis'])
                if 'meas' in config['Bob1']:
                    try:
                        B1meas = phGlass(**config['Bob1']['meas'])
                    except:
                        B1meas = None
                self.bob1 = Bob1(B1basis,B1meas)
            except:
                self.bob1 = None
        if 'Bob2' in config:
            B2basis = None
            try:
                if 'basis' in config['Bob2']:
                    B2basis = HWP(**config['Bob2']['basis'])
                self.bob2 = Bob2(B2basis)
            except:
                self.bob2 = None

        self.connected = True


    def setAlice(self,basis):
        if self.alice == None:
            raise Exception('No Alice defined for the current apparatus')

        self.alice.setBasis(basis)

    def setBob1(self,basis):
        if self.bob1 == None:
            raise Exception('No Bob1 defined for the current apparatus')

        self.Bob1.setBasis(basis)

        if self.bob2 != None:
            self.Bob2.setBasis(self.bob2.curbasis,self.bob1.curbasis)

    def setBob2(self,basis):
        if self.bob2 == None:
            raise Exception('No Bob2 defined for the current apparatus')

        if self.bob1 != None:
            self.bob2.setBasis(basis,self.bob1.curbasis)
        else:
            self.bob2.setBasis(basis)

class AliceBasisException(Exception): pass
class Bob1BasisException(Exception): pass
class Bob1ValueException(Exception): pass
class Bob2BasisException(Exception): pass
        
class Alice():
    def __init__(self,hwp):
        self.hwp = hwp

        self.anglebase = {'Z':0,'X':22.5,'-X-Z':33.75,'-X+Z':11.25}

        self.selBasis('Z')

    def selBasis(self,basis):
        if self.hwp==None:
            raise AliceBasisException('Alice''s HWP not connected')
        if not basis in self.anglebase:
            raise Exception('Basis not implemented')
        
        self.curbasis = basis
        self.curangle = self.anglebase[basis]
        self.hwp.rotate(self.curangle)

class Bob1():
    def __init__(self,hwp,phshift):
        self.hwp = hwp
        self.phshift = phshift

        self.anglebase = {'Z':45,'X':67.5}

        self.selBasis('Z')

        if self.phshift == None:
            self.curval = None
            self.curvalangle = None
        else:
            self.curval = self.phshift.posRel
            self.curvalangle = self.phshift.posAbs

    def selBasis(self,basis):
        if self.hwp == None:
            raise Bob1BasisException('Bob1''s HWP not connected')
        if not basis in self.anglebase:
            raise Exception('Basis not implemented')

        self.curbasis = basis
        self.curangle = self.anglebase[basis]
        self.hwp.rotate(self.curangle)

    def selValueAngle(self,angle):
        if self.phshift == None:
            raise Bob1ValueException('Bob1''s glass not connected')

        self.phshift.goto(angle)
        self.curvalangle = self.phshift.posAbs
        self.curval = self.phshift.posRel

    def selValue(self,value):
        if self.phshift == None:
            raise Bob1ValueException('Bob1''s glass not connected')
        if not value in ['min','max']:
            raise Exception('Value not implemented')

        if value == 'min':
            self.phshift.gotoMin()
        elif value == 'max':
            self.phshift.gotoMax()

        self.curvalangle = self.phshift.posAbs
        self.curval = self.phshift.posRel


class Bob2():
    def __init__(self,hwp):
        self.hwp = hwp

        self.anglebase = { 'Z': 0, 'X': 22.5 }

        self.selBasis('Z')

    def selBasis(self,basis,angleBob1=None):
        if self.hwp==None:
            raise Bob2BasisException('Alice''s HWP not connected')
        if not basis in self.anglebase:
            raise Exception('Basis not implemented')
        
        if angleBob1 != None:
            angle = angleBob1 - self.anglebase[basis]
        else:
            angle = self.anglebase

        self.curbasis = basis
        self.curangle = angle
        self.hwp.rotate(self.curangle)


class HWP(aptlib.PRM1):
    ''' This class describes the behaviour of a HWP mounted on a Thorlabs PRM1
    rotator.
    '''

    def __init__(self,serial_number=None,zero=0,dirRot='CW',home=True):
        '''Initialize the rotator, home it and assume the zero of the HWP is at
        0.'''
        super(HWP,self).__init__(serial_number=int(serial_number))

        if home:
            self.home()
            self.homed = True
        else:
            self.homed = False
        
        self.zero = zero

        # direction of rotation (if the light enters from the side where the
        # numbers are written, the WP rotates CW)
        self.dirRot = dirRot

        self.angle = self._rot2lamina(self.getPosition())

    def _rot2lamina(self,rotangle):
        '''Transform an angle from the rotator system of reference into the
        lamina one.'''
        if self.dirRot != 'CW':
            langle = np.fmod(-rotangle+self.zero,360)
        else:
            langle = np.fmod(rotangle-self.zero,360)
        return langle

    def _lamina2rot(self,langle):
        '''Transform an angle from the lamina system of reference into the
        rotator one.'''
        if self.dirRot != 'CW':
            rotangle = np.fmod(-langle+self.zero,360)
        else:
            rotangle = np.fmod(langle+self.zero,360)
        return rotangle


    def rotate(self,newAngle):
        ''' Rotate the WP of angle degrees in the clockwise direction (if looked
        from the source), using self.zero as zero.'''
        angle = self._lamina2rot(newAngle)
        self.setPosition(angle)

        self.angle = self._rot2lamina(self.getPosition())


class phGlass(aptlib.PRM1):
    ''' This class control the rotator of the glass giving a phase shift between
    the two paths of the Sagnac interferometer.'''
    def __init__(self,serial_number,posMin=None,posMax=None,home=True):
        super(phGlass,self).__init__(int(serial_number))

        if home:
            self.home()
            self.homed = True
        else:
            self.homed = False

        self.posMin = posMin
        self.posMax = posMax

        self.posAbs = self.getPosition()
        # posRel says if the glass is in the position so as to give a maximum
        # ('max'), a minimum ('min') or none of them ('none')
        self.posRel = 'none'

    def gotoMin(self):
        if self.posMin==None:
            raise Exception('The position of constructive and destructive \
            interference is not set')

        super(phGlass,self).goto(self.posMin)
        self.posAbs = self.getPosition()
        self.posRel = 'min'
    
    def gotoMax(self):
        if self.posMax==None:
            raise Exception('The position of constructive and destructive \
            interference is not set')

        super(phGlass,self).goto(self.posMax)
        self.posAbs = self.getPosition()
        self.posRel = 'max'

    def goto(self,position):
        super(phGlass,self).goto(position)
        self.posAbs = self.getPosition()
        self.posRel = 'none'



class epsWP(aptlib.PRM1):
    '''This class controls the lamina that shifts the phase of the H and the V
    polarization.'''
    def __init__(self,serial_number,home=True):
        super(epsWP,self).__init__(int(serial_number))

        if home:
            self.home()
            self.homed = True
        else:
            self.homed = False
