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

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

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
        self.isPWMConnected = False
        self.isSPADConnected = False
        
        self.bufNum=0
        
        self.coincWindow = 2*1e-9
        
        
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
        
        
        self.voltage_arr_complete = np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,
                                     1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,
                                     2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,
                                     3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,
                                     4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,
                                     5,5.5,6,7,8,9,10,11,13,15,17.5,20,22.5,25])
    
        self.voltage_arr_fast = np.array([0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,
                                     5,5.5,6,7,8,9,10,11,13,15,17.5,20,22.5,25])
        
        
    @pyqtSlot()
    def on_btnStart_clicked(self):
        """
        Start a complete acquisition.
        """
        
        if not self.started:
            if(self.isPWMConnected and not self.isSPADConnected):
                # create the object for the power meter and open it
                pwm = pm100d()
            elif (self.isSPADConnected and not self.isPWMConnected):
                #create object for the SPAD
                self.ttagBuf = ttag.TTBuffer(self.bufNum) 
            else:
                print("Please connect a sensor")
                return
            
            if not self.isRotatorConnected:
                self.connectRotator()
            
            if not self.isLCRConnected:
                self.connectLCR()
            else:
                self.lcc.mode = self.lcc.Mode.voltage1
                self.lcc.enable= True
            
            self.started = True
            
            self.btnStart.setStyleSheet("background-color: red")
            self.btnStart.setText('Stop')
            self.btnConnect.setEnabled(False)
            self.btnConnectLCR.setEnabled(False)
            self.btnConnectPWM.setEnabled(False)
            self.btnConnectSPAD.setEnabled(False)
            self.btnOscilloscope.setEnabled(False)
            
            if self.rbtnComplete.isChecked():
                self.voltage_arr=self.voltage_arr_complete
            elif self.rbtnFast.isChecked():
                self.voltage_arr=self.voltage_arr_fast
            
            
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
                    #checks for stop command
                    qApp.processEvents()
                    #breaks if stop has been called
                    if not self.started:
                        break
                    singleMeasure = np.zeros(self.average)
                    if(self.isPWMConnected and not self.isSPADConnected):
                        for j in range(self.average):
                            time.sleep(0.05)
                            p = max(pwm.read()*1000, 0.)
                            singleMeasure[j] = p
                        self.count[i] = np.mean(singleMeasure)
                    elif (self.isSPADConnected and not self.isPWMConnected):
                        time.sleep(self.exptime)
                        singles = self.ttagBuf.singles(self.exptime)
                        coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
                        self.count[i]=coincidences[self.SPADChannel, self.SPADOtherChannel]
                    self.axVis.plot(self.totvoltage_arr, self.count, '.')
                    self.plotVis.draw()
                    self.lblPowerStart.setText("{:.3}".format(float(self.count[i])))
                    i += 1

                if not self.started:
                    break
                
                self.voltage_arr= np.flipud(self.voltage_arr)
            
            if self.started:
                filename = self.txtFileName.text()
                np.savez(filename, voltage=self.totvoltage_arr, count=self.count)
            
            self.btnStart.setStyleSheet("")
            self.btnStart.setText('Start')
            self.btnConnect.setEnabled(True)
            self.btnConnectLCR.setEnabled(True)
            self.btnConnectPWM.setEnabled(True)
            self.btnConnectSPAD.setEnabled(True)
            self.btnOscilloscope.setEnabled(True)
            
            self.started = False
            
        else:
            self.started = False
        
      
        
    
    @pyqtSlot()
    def on_btnOscilloscope_clicked(self):
        """
        Monitor the light incident on the power meter.
        """
        
        # create the object for the power meter
        if not self.oscilloscope:
            if(self.isPWMConnected and not self.isSPADConnected):
                # create the object for the power meter and open it
                pwm = pm100d()
            elif (self.isSPADConnected and not self.isPWMConnected):
                #create object for the SPAD
                self.ttagBuf = ttag.TTBuffer(self.bufNum) 
            else:
                print("Please connect a sensor")
                return
            self.oscilloscope = True
            
            self.btnOscilloscope.setStyleSheet("background-color: red")
            self.btnOscilloscope.setText("Stop Oscilloscope")
            self.btnStart.setEnabled(False)
            self.btnConnectPWM.setEnabled(False)
            self.btnConnectSPAD.setEnabled(False)
            
            acqPause = float(self.txtPause.text())/1000
            
            sampleIndex = 0
            sampleTot = 1000
            sample = np.arange(sampleTot)
            
            power = np.zeros((sampleTot, 1))
            while self.oscilloscope:
                qApp.processEvents()
                if(self.isPWMConnected and not self.isSPADConnected):
                    time.sleep(acqPause)
                    p = max(pwm.read()*1000, 0.)  
                elif (self.isSPADConnected and not self.isPWMConnected):
                    time.sleep(self.exptime)
                    singles = self.ttagBuf.singles(self.exptime)
                    coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
                    p=coincidences[self.SPADChannel, self.SPADOtherChannel]
                power[sampleIndex] = p
                sampleIndex = (sampleIndex+1) % sampleTot
                self.lblPower.setText("{:.3}".format(float(p)))
                self.axOscilloscope.plot(sample, power, '.')
                self.plotOscilloscope.draw()
            
        else:
            self.btnOscilloscope.setStyleSheet("")
            self.btnOscilloscope.setText("Oscilloscope")
            self.btnStart.setEnabled(True)
            self.btnConnectPWM.setEnabled(True)
            self.btnConnectSPAD.setEnabled(True)
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
        if not self.isLCRConnected:
            self.connectLCR()
        else:
            self.disconnectLCR()
   
    @pyqtSlot()
    def on_btnConnectPWM_clicked(self):
        if not self.isPWMConnected:
            self.connectPWM()
        else:
            self.disconnectPWM()
            
    @pyqtSlot()
    def on_btnConnectSPAD_clicked(self):
        if not self.isSPADConnected:
            self.connectSPAD()
        else:
            self.disconnectSPAD()
    
    def connectRotator(self):
        selLinear = str(self.cmbLinearStage.currentText())
        if selLinear == 'thorlabs':
            # open APT controller
            SN = int(self.txtSN.text())
            self.btnConnect.setText('Connecting')
            self.con = aptlib.PRM1(serial_number=SN)
            self.con.home()
            self.btnConnect.setText('Disconnect Rotator')
            self.btnConnect.setStyleSheet("background-color: red")
            self.isRotatorConnected = True
        else:
            self.isRotatorConnected = False
            
    def disconnectRotator(self):
        if self.isRotatorConnected:
            self.con.close()
            self.isRotatorConnected = False
            self.btnConnect.setText('Connect Rotator')
            self.btnConnect.setStyleSheet("")
      
    def connectLCR(self):
        port=self.txtPort.text()
        self.lcc = ik.thorlabs.LCC25.open_serial(port, 115200,timeout=1)
        self.lcc.mode = self.lcc.Mode.voltage1
        self.lcc.enable = True
        self.btnConnectLCR.setText('Disconnect LCR')
        self.btnConnectLCR.setStyleSheet("background-color: red")
        self.isLCRConnected = True
    
    def disconnectLCR(self):
        self.lcc.enable = False
        self.btnConnectLCR.setText('Connect LCR')
        self.btnConnectLCR.setStyleSheet("")
        self.isLCRConnected= False
        
    def connectPWM(self):
        self.isPWMConnected=True
        self.isSPADConnected = False
        self.btnConnectPWM.setText('Disconnect PWM')
        self.btnConnectPWM.setStyleSheet("background-color: red")
        self.average = int(self.txtAverage.text())
        self.btnConnectSPAD.setEnabled(False)
        
    def disconnectPWW(self):
        self.isPWMConnected=False
        self.btnConnectPWM.setText('Connect PWM')
        self.btnConnectPWM.setStyleSheet("")
        self.btnConnectSPAD.setEnabled(True)
        
    def connectSPAD(self):
        self.isSPADConnected=True
        self.isPWMConnected = False
        self.btnConnectSPAD.setText('Disconnect SPAD')
        self.btnConnectSPAD.setStyleSheet("background-color: red")
        self.SPADChannel=int(self.txtSPADChannel.text())
        if self.SPADChannel > 3 or self.SPADChannel <0:
            self.SPADChannel =0
        self.SPADOtherChannel=int(self.txtSPADOtherChannel.text())
        if self.SPADOtherChannel > 3 or self.SPADOtherChannel <0:
            self.SPADOtherChannel =0
        delay=float(self.txtDelay.text())
        otherdelay=float(self.txtOtherDelay.text())
        self.delay = np.array([0.0, 0.0,
                               0.0,0.0])
        self.delay[self.SPADChannel]=delay
        self.delay[self.SPADOtherChannel] = otherdelay
        self.delay = self.delay*1e-9
        self.exptime = float(self.txtExposure.text())
        self.exptime = self.exptime*1e-3
        self.btnConnectPWM.setEnabled(False)
        
    def disconnectSPAD(self):
        self.isSPADConnected=False
        self.btnConnectSPAD.setText('Connect SPAD')
        self.btnConnectSPAD.setStyleSheet("")
        self.btnConnectPWM.setEnabled(True)

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = Vis()
    window.show()
    sys.exit(app.exec_())
