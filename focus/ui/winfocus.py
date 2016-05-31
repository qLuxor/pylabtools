# -*- coding: utf-8 -*-

"""
Module implementing WinFocus.
"""
# TODO: change from pyAPT to aptlib

import sys
sys.path.append('/home/sagnac/Quantum/')
sys.path.append('/home/sagnac/Quantum/pyAPT/')

import time

from pyThorPM100.pm100 import pm100d
import pyAPT

import numpy as np
from scipy.special import erfc
from scipy.optimize import curve_fit

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
        self.started = False
        
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
        if not self.started:
            self.started = True
            
            self.btnStart.setStyleSheet("background-color: green")
            
            average = int(self.txtAverage.text())
            minStage = float(self.txtMin.text())
            maxStage = float(self.txtMax.text())
            step = float(self.txtStep.text())
            
            x = np.arange(minStage, maxStage, step)
            count = np.zeros(x.size)
            
            # open power meter
            pwm = pm100d()
            
            selLinear = str(self.cmbLinearStage.currentText())
            if selLinear == 'thorlabs':
                # open APT controller
                SN = int(self.txtSN.text())
                con = pyAPT.MTS50(serial_number=SN)
                con.goto(x[0], wait=True)

            for i in range(x.size):
                qApp.processEvents()
                con.goto(x[i],  wait=True)
                # wait until the movement has finished
                stat = con.status()
                while stat.moving:
                    time.sleep(0.01)
                    stat = con.status
                singleMeasure = np.zeros(average)
                for j in range(average):
                    p = max(pwm.read()*1000, 0.)
                    singleMeasure[j] = p
                count[i] = np.mean(singleMeasure)
                self.axErf.plot(x, count, '.')
                self.plotErf.draw()
                
                if not self.started:
                    break
            
            if self.started:
                # find medium point
                x_thres = x[np.nonzero(count>(np.max(count)+np.min(count))/2)[0]]
                x0 = np.min(x_thres)
                
                # calculate fit
                func = lambda x, a, b, c, d: a*erfc(b*(x-c)) + d
                p0 = [np.max(count)/2,  1,  x0,  np.min(count)/2]
                p, perr = curve_fit(func, x, count, p0=p0)
                
                self.axErf.hold(True)
                self.axErf.plot(x, func(x, *p), 'r')
                self.plotErf.draw()
                self.axErf.hold(False)
                
                self.lblA0.setText("{:.4}".format(p[0]))
                self.lblA1.setText("{:.4}".format(p[1]))
                self.lblA2.setText("{:.4}".format(p[2]))
                self.lblA3.setText("{:.4}".format(p[3]))
                
                waist = np.sqrt(2)/p[1]*1e3 # in um
                
                self.lblWaist.setText("{:.4}".format(waist))
                
            self.btnStart.setStyleSheet("")
            self.started = False
            
        else:
            self.btnStart.setStyleSheet("")
            self.started = False
        
      
        
    
    @pyqtSlot()
    def on_btnOscilloscope_clicked(self):
        """
        Monitor the light incident on the power meter.
        """
        
        # create the object for the power meter
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

