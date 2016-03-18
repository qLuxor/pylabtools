# -*- coding: utf-8 -*-

"""
Module implementing WinFocus.
"""

import sys
sys.path.append('/home/sagnac/Quantum/')

import time

from pyThorPM100.pm100 import pm100d

import numpy as np

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow, qApp

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from .Ui_focus import Ui_MainWindow

class WinFocus(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(WinFocus, self).__init__(parent)
        self.setupUi(self)
        
        self.oscilloscope = False
        
        self.figOscilloscope = plt.figure()
        self.plotOscilloscope = FigureCanvas(self.figOscilloscope)
        self.ltOscilloscope.addWidget(self.plotOscilloscope)
        self.axOscilloscope = self.figOscilloscope.add_subplot(111)
        self.axOscilloscope.hold(False)
        self.axOscilloscope.set_xlabel('Time [s]')
        self.axOscilloscope.set_ylabel('Power [mW]')
        
        self.figErf = plt.figure()
        self.plotErf = FigureCanvas(self.figErf)
        self.ltErf.addWidget(self.plotErf)
        self.axErf = self.figErf.add_subplot(111)
        self.axErf.hold(False)
        self.axErf.set_xlabel('Position [mm]')
        self.axErf.set_ylabel('Power [mW]')
        
    
    @pyqtSlot()
    def on_btnStart_clicked(self):
        """
        Start a complete acquisition.
        """
        
        # create the object for the power meter
        #pwm = pm100d()
        pass
        
    
    @pyqtSlot()
    def on_btnOscilloscope_clicked(self):
        """
        Monitor the light incident on the power meter.
        """
        
        # create the object for the power meter
        # pwm = pm100d()
        
        
        if not self.oscilloscope:
            self.oscilloscope = True
            
            self.btnOscilloscope.setStyleSheet("background-color: green")
            
            acqPause = float(self.txtPause.text())
            
            sampleIndex = 0
            sampleTot = 1000
            sample = np.arange(sampleTot)*acqPause/1000
            pwm = pm100d()
            
            power = np.zeros((sampleTot, 1))
            while self.oscilloscope:
                qApp.processEvents()
                p = max(pwm.read()*1000, 0.)
                power[sampleIndex] = p
                sampleIndex = (sampleIndex+1) % sampleTot
                self.lblPower.setText("{:.3}".format(p))
                self.axOscilloscope.plot(sample, power, '.')
                self.plotOscilloscope.draw()
                
                time.sleep(acqPause/1000)
            
        else:
            self.btnOscilloscope.setStyleSheet("")
            self.oscilloscope = False
