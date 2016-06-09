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

    def __init__(self,config):
        '''Initialize the apparatus according to the information in the config
        dictionary. The dictionary is read from a YAML file with the following
        structure:

        Alice:
            basis:
                SN: xxxxxxxx
                zero: xxx
                rotDir: 'CW'/'CCW'
                home: True
        Bob2:
            basis:
            ...
        Bob1:
            basis:
            ...
            meas:
                SN: xxxxxxxx
                posMin: xxx
                posMax: xxx
                home: True
        weak:
            SN: xxxxxxxx
            home: True

        '''

        # TODO: implement the class structure of the experimental apparatus
        pass


class HWP(PRM1):
    ''' This class describes the behaviour of a HWP mounted on a Thorlabs PRM1
    rotator.
    '''

    def __init__(self,serial_number=None,zero=0,dirRot='CW',home=True):
        '''Initialize the rotator, home it and assume the zero of the HWP is at
        0.'''
        super(HWP,self).__init__(serial_number=serial_number)

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


class phGlass(PRM1):
    ''' This class control the rotator of the glass giving a phase shift between
    the two paths of the Sagnac interferometer.'''
    def __init__(self,serial_number,posMin=None,posMax=None,home=True):
        super(phGlass,self).__init__(serial_number)

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
            raise Exception('The position of constructive and destructive
            interference is not set')

        super(phGlass,self).goto(self.posMin)
        self.posRel = 'min'
    
    def gotoMax(self):
        if self.posMax==None:
            raise Exception('The position of constructive and destructive
            interference is not set')

        super(phGlass,self).goto(self.posMax)
        self.posRel = 'max'

    def goto(self,position):
        super(phGlass,self).goto(position)
        self.posRel = 'none'



class epsWP(PRM1):
    '''This class controls the lamina that shifts the phase of the H and the V
    polarization.'''
    def __init__(self,serial_number,home=True):
        super(epsWP,self).__init__(serial_number)

        if home:
            self.home()
            self.homed = True
        else:
            self.homed = False
