# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import time

from pyThorPM100.pm100 import pm100d
import aptlib

import numpy as np

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow, qApp, QApplication
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import instruments as ik

qtCreatorFile = 'visLCR.ui'

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
        
        self.isRotatorConnected = False
        self.isLCRConnected=False
        
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
        
        
        self.voltage_arr = np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,
                                     1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,
                                     2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,
                                     3.1,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,
                                     4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,
                                     5,5.5,6,7,8,9,10,11,13,15,17.5,20,22.5,25])
        
        
    @pyqtSlot()
    def on_btnStart_clicked(self):
        """
        Start a complete acquisition.
        """
        
        if not self.started:
            self.started = True
            
            self.btnStart.setStyleSheet("background-color: green")
            
            # create the object for the power meter
            # open power meter
            pwm = pm100d()
            
            if not self.isRotatorConnected:
                self.connectRotator()
            
            if not self.isLCRConnected:
                self.connectLCR()
                    
            average = int(self.txtAverage.text())
            pos1Stage = float(self.txtPos1.text())
            pos2Stage = float(self.txtPos2.text())
            
            self.pos_arr = [pos1Stage, pos2Stage]
            i = 0
            self.count = np.zeros(2*self.voltage_arr.size)
            self.totvoltage_arr=np.concatenate((self.voltage_arr, np.flipud(self.voltage_arr)), axis=0)
            
            for pos in self.pos_arr:
                self.con.goto(pos, wait=True)
                
                for voltage in self.voltage_arr:
                    self.lcc.voltage1 = voltage
                    time.sleep(1.5)
                    qApp.processEvents()
                    singleMeasure = np.zeros(average)
                    for j in range(average):
                        time.sleep(0.05)
                        p = max(pwm.read()*1000, 0.)
                        singleMeasure[j] = p
                    self.count[i] = np.mean(singleMeasure)
                    self.axVis.plot(self.totvoltage_arr, self.count, '.')
                    self.plotVis.draw()
                    i += 1
                
                
                if not self.started:
                    break
                
                self.voltage_arr= np.flipud(self.voltage_arr)
                    
            filename = self.txtFileName.text()
            np.savez(filename, voltage=self.totvoltage_arr, count=self.count)
            
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


    @pyqtSlot()
    def on_btnSaveData_clicked(self):
        """
        Save acquired data
        """
        np.savez(self.txtFileName.text() + '_Tot', voltage=self.voltage_arr, TotCount=self.count, pos=self.pos_arr)
        
    @pyqtSlot()
    def on_btnConnect_clicked(self):
        if not self.isRotatorConnected:
            self.connectRotator()
        else:
            self.disconnectRotator()
       
    @pyqtSlot()
    def on_btnConnectLCR_clicked(self):
        self.connectLCR()
       
    def connectRotator(self):
        selLinear = str(self.cmbLinearStage.currentText())
        if selLinear == 'thorlabs':
            # open APT controller
            SN = int(self.txtSN.text())
            self.btnConnect.setText('Connecting')
            self.con = aptlib.PRM1(serial_number=SN)
            self.con.home()
            self.btnConnect.setText('Disconnect Rotator')
            self.isRotatorConnected = True
        else:
            self.isRotatorConnected = False
            
    def disconnectRotator(self):
        if self.isRotatorConnected:
            self.con.close()
            self.isRotatorConnected = False
            self.btnConnect.setText('Connect Rotator')
      
    def connectLCR(self):
        port=self.txtPort.text()
        self.lcc = ik.thorlabs.LCC25.open_serial(port, 115200,timeout=1)
        self.lcc.mode = self.lcc.Mode.voltage1
        self.lcc.enable = True
        self.btnConnectLCR.setText('LCR Connected')
        self.btnConnectLCR.setEnabled(False)
        self.isLCRConnected = True
        

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = Vis()
    window.show()
    sys.exit(app.exec_())
