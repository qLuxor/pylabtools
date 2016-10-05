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
            basis1:
                ...
            basis2:
                ...
            meas:
                serial_number: 'xxxxxxxx'
                zero: xxx
                posMin: xxx
                posMax: xxx
                home: True
            weak:
                serial_number: 'xxxxxxxx'
                zero: xxx
                home: True
                func: 'aaa'   

        '''

        if 'Alice' in config:
            print('Initilizing Alice...')
            A1basis = None
            try:
                if 'basis' in config['Alice']:
                    print(config)
                    A1basis = HWP(**config['Alice']['basis'])
                self.alice = Alice(A1basis)
            except AliceBasisException as e:
                self.alice = None
        if 'Bob1' in config:
            print('Initializing Bob1...')
            B1basis1 = None
            B1basis2 = None
            B1meas = None
            B1weak = None
            try:
                if 'basis1' in config['Bob1']:
                    B1basis1 = HWP(**config['Bob1']['basis1'])
                if 'basis2' in config['Bob1']:
                    try:
                        B1basis2 = HWP(**config['Bob1']['basis2'])
                    except:
                        B1basis2 = None
                if 'meas' in config['Bob1']:
                    try:
                        B1meas = phGlass(**config['Bob1']['meas'])
                    except:
                        B1meas = None
                if 'weak' in config['Bob1']:
                    try:
                        B1weak1 = epsWP(**config['Bob1']['weak'])
                    except:
                        B1weak1 = None
                self.bob1 = Bob1(B1basis1,B1basis2,B1meas,B1weak)
                print('DONE')
            except Exception as e:
                print(e.__doc__)
                print('Exception in Bob1 intialization')
                self.bob1 = None
        if 'Bob2' in config:
            print('Initializing Bob2...')
            B2basis = None
            try:
                if 'basis' in config['Bob2']:
                    B2basis = HWP(**config['Bob2']['basis'])
                self.bob2 = Bob2(B2basis)
                print('DONE')
            except:
                print('Exception in Bob2 initialization')
                self.bob2 = None

        self.connected = True

    def disconnect(self):
        if self.alice != None:
            self.alice.hwp.close()
        if self.bob2 != None:
            self.bob2.hwp.close()
        if self.bob1 != None:
            if self.bob1.hwp1 != None:
                self.bob1.hwp1.close()
            if self.bob1.hwp2 != None:
                self.bob1.hwp2.close()
            if self.bob1.phshift != None:
                self.bob1.phshift.close()
        self.alice = None
        self.bob1 = None
        self.bob2 = None
        self.connected = False


    def setAlice(self,basis):
        if self.alice == None:
            print('No Alice defined for the current apparatus')
            return

        self.alice.selBasis(basis)

    def setBob1(self,basis,posglass,epsHWP,epsQWP,comp):
        if self.bob1 == None:
            print('No Bob1 defined for the current apparatus')
            return

        self.bob1.selBasis(basis)

        if self.bob1.hwp2 == None and self.bob2 != None:
            self.bob2.selBasis(self.bob2.curbasis,self.bob1.curangle)

        self.bob1.selValue(posglass)
        self.bob1.selWeakHWPAngle(epsHWP)
        self.bob1.selWeakQWPAngle(epsQWP)
        self.bob1.selWeakCompAngle(comp)

    def setBob2(self,basis):
        if self.bob2 == None:
            print('No Bob2 defined for the current apparatus')
            return

        if self.bob1 != None and self.bob1.hwp2 == None:
            self.bob2.selBasis(basis,self.bob1.curangle)
        else:
            self.bob2.selBasis(basis)

class AliceBasisException(Exception): pass
class Bob1BasisException(Exception): pass
class Bob1ValueException(Exception): pass
class Bob1WeakException(Exception): pass
class Bob2BasisException(Exception): pass
        
class Alice():
    def __init__(self,hwp=None):
        self.hwp = hwp

        self.anglebase = {'Z':0,'X':22.5,'-X-Z':33.75,'-X+Z':11.25}

        self.selBasis('Z')

    def selBasis(self,basis):
        if self.hwp==None:
            print('Alice''s HWP not connected')
            return
            #raise AliceBasisException('Alice''s HWP not connected')
        if not basis in self.anglebase:
            print('Basis not implemented')
            return
            #raise Exception('Basis not implemented')
        
        self.curbasis = basis
        self.curangle = self.anglebase[basis]
        self.hwp.rotate(self.curangle)

class Bob1():
    def __init__(self,hwp1=None,hwp2=None,phshift=None,weak=None):
        self.hwp1 = hwp1
        self.hwp2 = hwp2
        self.phshift = phshift
        self.weak = [weak]

        #self.anglebase = {'Z':45,'X':67.5}
        self.anglebase = {'Z':0, 'X': 22.5}

    def selBasis(self,basis):
        if self.hwp1 == None:
            print('Bob1''s first HWP not connected')
            return
            #raise Bob1BasisException('Bob1''s HWP not connected')
        if not basis in self.anglebase:
            print('Basis not implemented')
            return
            #raise Exception('Basis not implemented')

        self.curbasis = basis
        self.curangle = self.anglebase[basis]
        self.hwp1.rotate(self.curangle)

        if self.hwp2 != None:
            self.hwp2.rotate(self.curangle)

    def selValueAngle(self,angle):
        if self.phshift == None:
            print('Bob1''s glass not connected')
            return
            #raise Bob1ValueException('Bob1''s glass not connected')

        self.phshift.goto(angle)
        self.curvalangle = self.phshift.posAbs
        
        self.curval = self.phshift.posRel

    def selValue(self,value):
        if self.phshift == None:
            print('Bob1''s glass not connected')
            return
            #raise Bob1ValueException('Bob1''s glass not connected')
        if not value in ['min','max']:
            print('Value not implemented')
            return
            #raise Exception('Value not implemented')

        if value == 'min':
            self.phshift.gotoMin()
        elif value == 'max':
            self.phshift.gotoMax()

        self.curvalangle = self.phshift.posAbs
        self.curval = self.phshift.posRel

    def _getRotFromFunc(self,reqfunc):
        func = {}
        for i in range(len(self.weak)):
            if self.weak[i] != None:
                func[self.weak[i].func] = i
        return self.weak[func[reqfunc]]
        
    def selWeakHWPAngle(self,angle):
        reqfunc = 'Weak HWP'
        try:
            rot = self._getRotFromFunc(reqfunc)
        except KeyError:
            print('No rotator associated to Bob1''s Weak HWP')
            return
            #raise Exception('No rotator associated to Bob1''s Weak HWP')

        rot.goto(angle)

    def selWeakQWPAngle(self,angle):
        reqfunc = 'Weak QWP'
        try:
            rot = self._getRotFromFunc(reqfunc)
        except KeyError:
            print('No rotator associated to Bob1''s Weak QWP')
            return
            #raise Exception('No rotator associated to Bob1''s Weak QWP')

        rot.goto(angle)

    def selWeakCompAngle(self,angle):
        reqfunc = 'Compensation'
        try:
            rot = self._getRotFromFunc(reqfunc)
        except KeyError:
            print('No rotator associated to Bob1''s Weak compensation')
            return
            #raise Exception('No rotator associated to Bob1''s Weak compensation\
            #WP')

        rot.goto(angle)

class Bob2():
    def __init__(self,hwp=None):
        self.hwp = hwp

        self.anglebase = { 'Z': 0, 'X': 22.5 }

        self.selBasis('Z')

    def selBasis(self,basis,angleBob1=None):
        if self.hwp==None:
            print('Bob2''s HWP not connected')
            return
            #raise Bob2BasisException('Bob2''s HWP not connected')
        if not basis in self.anglebase:
            print('Basis not implemented')
            return
            #raise Exception('Basis not implemented')
        
        if angleBob1 != None:
            angle = angleBob1 - self.anglebase[basis]
        else:
            angle = self.anglebase[basis]

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
            print('Homing HWP...',end='')
            self.home()
            print('done')
            self.homed = True
        else:
            self.homed = False
        
        self.zero = zero

        # direction of rotation (if the light enters from the side where the
        # numbers are written, the WP rotates CW)
        self.dirRot = dirRot

        self.angle = self.getPosition()

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
        super(HWP,self).goto(float(angle))

        self.angle = self.getPosition()

    def getPosition(self):
        return self._rot2lamina(super(HWP,self).getPosition())


class phGlass(aptlib.PRM1):
    ''' This class control the rotator of the glass giving a phase shift between
    the two paths of the Sagnac interferometer.'''
    def __init__(self,serial_number,zero=None,posMin=None,posMax=None,home=True):
        super(phGlass,self).__init__(int(serial_number))

        if home:
            print('Homing phGlass...',end='')
            self.home()
            print('done')
            self.homed = True
        else:
            self.homed = False

        self.zero = zero
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

        super(phGlass,self).goto(float(self._pos2rot(self.posMin)))
        self.posAbs = self.getPosition()
        self.posRel = 'min'
    
    def gotoMax(self):
        if self.posMax==None:
            raise Exception('The position of constructive and destructive \
            interference is not set')

        super(phGlass,self).goto(float(self._pos2rot(self.posMax)))
        self.posAbs = self.getPosition()
        self.posRel = 'max'

    def _pos2rot(self,position):
        return np.fmod(position + self.zero,360)

    def _rot2pos(self,rot):
        return np.fmod(rot - self.zero,360)

    def goto(self,position):
        ''' Go to position, related to the zero value contained in self.zero.
        '''
        super(phGlass,self).goto(float(self._pos2rot(position)))
        self.posAbs = self.getPosition()
        self.posRel = 'none'

    def getPosition(self):
        return self._rot2pos(super(phGlass,self).getPosition())

class epsWP(aptlib.PRM1):
    '''This class controls the lamina that shifts the phase of the H and the V
    polarization.'''
    def __init__(self,serial_number,zero=None,func=None,home=True):
        super(epsWP,self).__init__(int(serial_number))

        if home:
            self.home()
            self.homed = True
        else:
            self.homed = False

        self.zero = zero

        self.func = func

        self.angle = self.getPosition()

    def _pos2rot(self,position):
        return np.fmod(position + self.zero,360)

    def _rot2pos(self,rot):
        return np.fmod(rot - self.zero,360)

    def goto(self,position):
        super(epsWP,self).goto(float(self._pos2rot(position)))
        self.angle = self.getPosition()

    def getPosition(self):
        return self._rot2pos(super(epsWP,self).getPosition())
