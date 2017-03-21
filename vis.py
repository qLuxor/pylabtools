# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import time

from pyThorPM100.pm100 import pm100d
import aptlib

import numpy as np
from scipy.optimize import curve_fit

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow, qApp, QApplication
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

qtCreatorFile = 'vis.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Vis(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(Vis, self).__init__()
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
        
        self.figVis = plt.figure()
        self.plotVis = FigureCanvas(self.figVis)
        self.ltVis.addWidget(self.plotVis)
        self.axVis = self.figVis.add_subplot(111)
        self.axVis.hold(False)
        self.axVis.set_xlabel('Position [mm]')
        self.axVis.set_ylabel('Power [mW]')
        
    
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
            
            x = np.deg2rad(np.arange(minStage, maxStage, step))
            count = np.zeros(x.size)
            
            # open power meter
            pwm = pm100d()
            
            selLinear = str(self.cmbLinearStage.currentText())
            if selLinear == 'thorlabs':
                # open APT controller
                SN = int(self.txtSN.text())
                con = aptlib.PRM1(serial_number=SN)
                con.goto(float(np.rad2deg(x[0])), wait=True)

            for i in range(x.size):
                qApp.processEvents()
                con.goto(float(np.rad2deg(x[i])),  wait=True)
                # wait until the movement has finished
                #stat = con.status()
                #while stat.moving:
                #    time.sleep(0.01)
                #    stat = con.status
                time.sleep(0.1)
                singleMeasure = np.zeros(average)
                for j in range(average):
                    p = max(pwm.read()*1000, 0.)
                    singleMeasure[j] = p
                count[i] = np.mean(singleMeasure)
                self.axVis.plot(np.rad2deg(x), count, '.')
                self.plotVis.draw()
                
                if not self.started:
                    break
            
            if self.started:
                # find medium point
                I_max = np.max(count)
                I_min = np.min(count)
                x_max = x[np.argmax(count)]
                
                # calculate fit
                func = lambda x, a, b, c: a*np.cos(2*x + b)**2 + c
                p0 = [I_max - I_min, x_max, I_min]
                print(p0)
                bnds = ([0,-np.inf,0],[np.inf,np.inf,np.inf])
                p, pcov = curve_fit(func, x, count, p0=p0,bounds=bnds)
                perr = np.sqrt(np.diag(pcov))
                
                xvis = np.linspace(x[0],x[-1],1000)
                self.axVis.hold(True)
                self.axVis.plot(np.rad2deg(xvis), func(xvis, *p), 'r')
                self.plotVis.draw()
                self.axVis.hold(False)
                
                self.lblA0.setText("{:.4}".format(p[0])+' \u00B1 '+"{:.4}".format(perr[0]))
                self.lblA1.setText("{:.4}".format(np.rad2deg(p[1]))+' \u00B1 '+"{:.4}".format(np.rad2deg(perr[1])))
                self.lblA2.setText("{:.4}".format(p[2])+' \u00B1 '+"{:.4}".format(perr[2]))
                
                vis = p[0] / (p[0] + 2*p[2])
                errVis = 2/(p[0] + 2*p[2])**2 * np.sqrt( (p[2]*perr[0])**2 + (p[0]*perr[2])**2 )
                
                self.lblVis.setText("{:.4}".format(vis*100)+' \u00B1 '+"{:.4}".format(errVis*100))
                
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


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = Vis()
    window.show()
    sys.exit(app.exec_())
