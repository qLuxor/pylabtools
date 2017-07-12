# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

import time

from pyThorPM100.pm100 import pm100d
import aptlib

import numpy as np

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow, qApp, QApplication, QMessageBox
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import instruments as ik

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

import json
import logging
import traceback
import datetime

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
        
        self.coincWindow = 1*1e-9
        
        self.angleErr=1e-3
        
        
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
        
        self.btnMove1.setEnabled(False)
        self.btnMove2.setEnabled(False)
        
        self.voltage_arr_complete = np.array([[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,
                                     1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,
                                     2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,
                                     3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,
                                     4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,
                                     5,5.5,6,7,8,9,10,11,13,15,17.5,20,22.5,25], 
                                    [25, 22.5, 20, 17.5, 15, 13,11,10,9,8,7,6,5.5,5,
                                     4.9,4.8,4.7,4.6,4.5,4.4,4.3,4.2,4.1,4.0,
                                     3.9,3.8,3.7,3.6,3.5,3.4,3.3,3.2,3.1,3.0,
                                     2.9,2.8,2.7,2.6,2.5,2.4,2.3,2.2,2.1,2.0,
                                     1.9,1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1.0,
                                     0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.0]])
    
        self.voltage_arr_fast = np.array([[0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,
                                     5,6,7,10,15,20,25],
                                    [25,20,15,10,7,6,5,4.5,4.0,3.5,3.0,2.5,2.0,
                                     1.5,1.0,0.5,0]])
        self.voltage_arr_aimed = np.array([[0,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,
                                    2.1,2.2,2.3,2.4,2.5],
                                    [2.5,2.4,2.3,2.2,2.1,2.0,1.9,1.8,1.7,1.6,
                                    1.5,1.4,1.3,1.2,1.1,1.0,0.9,0.8,0.7,0.6,0.5,0]])
        if len(sys.argv) >1:
            self.txtLoadFileName.setText(str(sys.argv[1]))
            self.loadsettings()
        
        
    @pyqtSlot()
    def on_btnLoad_clicked(self):
        self.loadsettings()
                 
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
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("No sensor connected")
                msg.setInformativeText("Please connect a sensor before proceeding")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
            
            manualmode=False
            if not self.isRotatorConnected:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("No rotator connected")
                msg.setInformativeText("Do you want to use a manual rotator?")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                retval = msg.exec_()
                if retval ==65536:
                    self.connectRotator()
                    manualmode=False
                elif retval ==16384:
                    manualmode=True
            
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
            self.txtPos1.setEnabled(False)
            self.txtPos2.setEnabled(False)
            self.btnMove1.setEnabled(False)
            self.btnMove2.setEnabled(False)
            self.btnLoad.setEnabled(False)
            
            if self.rbtnComplete.isChecked():
                self.voltage_arr=self.voltage_arr_complete
            elif self.rbtnFast.isChecked():
                self.voltage_arr=self.voltage_arr_fast
            elif self.rbtnAimed.isChecked():
                self.voltage_arr=self.voltage_arr_aimed
                
            self.allowtime=float(self.txtAllowTime.text())
            
            self.repetitions= int(self.txtRepetitions.text())
            if self.repetitions <1:
                self.repetitions=1    
                
            self.hibernation =float(self.txtHibernation.text())
            
            pos1Stage = float(self.txtPos1.text())
            pos2Stage = float(self.txtPos2.text())
            
            self.pos_arr = [pos1Stage, pos2Stage]
            for cont in range(self.repetitions):
                i = 0
                j = 0
                
                self.totvoltage_arr=self.voltage_arr.flatten()
                self.count = np.zeros(self.totvoltage_arr.size)
                self.resultdata={}
                starttime=datetime.datetime.now()
                for pos in self.pos_arr:
                    if not manualmode:
                        self.con.goto(pos, wait=True)
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Manual rotation")
                        msg.setInformativeText("Please move rotator to "+ str(pos) +"\nClick Ok when ready")
                        msg.setWindowTitle("Warning")
                        msg.setStandardButtons(QMessageBox.Ok)
                        retval = msg.exec_()
                    
                    for voltage in self.voltage_arr[j]:
                        self.lcc.voltage1 = voltage
                        time.sleep(self.allowtime)
                        #checks for stop command
                        qApp.processEvents()
                        #breaks if stop has been called
                        if not self.started:
                            break
                        if(self.isPWMConnected and not self.isSPADConnected):
                            singleMeasure = np.zeros(self.average)
                            for k in range(self.average):
                                time.sleep(self.pause)
                                p = max(pwm.read()*1000, 0.)
                                singleMeasure[k] = p
                            self.count[i] = np.mean(singleMeasure)
                        elif (self.isSPADConnected and not self.isPWMConnected):
                            time.sleep(self.exptime)
                            if self.SPADChannel == self.SPADOtherChannel:
                                singles = self.ttagBuf.singles(self.exptime)
                                self.count[i]=singles[self.SPADChannel]
                            else:
                                coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
                                self.count[i]=coincidences[self.SPADChannel, self.SPADOtherChannel]
                        self.axVis.plot(self.totvoltage_arr, self.count, '.')
                        self.plotVis.draw()
                        self.lblPowerStart.setText("{:.3}".format(float(self.count[i])))
                        self.lblVoltageStart.setText("{:.3}".format(float(voltage)))
                        i += 1
                    j+=1
                    if not self.started:
                        break
                
                if self.started:
                    filename = self.txtFileName.text()
                    if self.repetitions>1:
                        filename = filename+"_"+str(cont+1)
                    np.savez(filename, voltage=self.totvoltage_arr, count=self.count)
                    minpower=np.min(self.count)
                    maxpower=np.max(self.count)
                    minvolt=self.totvoltage_arr[np.argmin(self.count)]
                    maxvolt=self.totvoltage_arr[np.argmax(self.count)]
                    rawvisibility=(maxpower-minpower)/(maxpower+minpower)
                    stoptime=datetime.datetime.now()
                    self.resultdata.update({"RawMaxVolt":maxvolt, "RawMinVolt": minvolt, "RawMaxPower":maxpower, "RawMinPower": minpower, "RawVisibility":rawvisibility, "StartTime":str(starttime), "StopTime":str(stoptime)})
                    with open(filename+".json", 'w') as outfile:
                        json.dump(self.resultdata, outfile)
                    time.sleep(self.hibernation)
                else:
                    break
            
            self.btnStart.setStyleSheet("")
            self.btnStart.setText('Start')
            self.btnConnect.setEnabled(True)
            self.btnConnectLCR.setEnabled(True)
            self.btnConnectPWM.setEnabled(True)
            self.btnConnectSPAD.setEnabled(True)
            self.btnOscilloscope.setEnabled(True)
            self.txtPos1.setEnabled(True)
            self.txtPos2.setEnabled(True)
            self.btnMove1.setEnabled(True)
            self.btnMove2.setEnabled(True)
            self.btnLoad.setEnabled(True)
            
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
            self.btnLoad.setEnabled(False)
            
            sampleIndex = 0
            sampleTot = 1000
            sample = np.arange(sampleTot)
            
            power = np.zeros((sampleTot, 1))
            while self.oscilloscope:
                qApp.processEvents()
                if(self.isPWMConnected and not self.isSPADConnected):
                    time.sleep(self.pause)
                    p = max(pwm.read()*1000, 0.)  
                elif (self.isSPADConnected and not self.isPWMConnected):
                    time.sleep(self.exptime)
                    if self.SPADChannel == self.SPADOtherChannel:
                        singles = self.ttagBuf.singles(self.exptime)
                        p = singles[self.SPADChannel]
                    else:
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
            self.btnLoad.setEnabled(True)
            self.oscilloscope = False

        
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
            
    @pyqtSlot()
    def on_btnMove1_clicked(self):
        if self.isRotatorConnected:
            pos1Stage = float(self.txtPos1.text())
            self.setangle(self.con, pos1Stage, self.angleErr)
        else:
            print("Please Connect Rotator")
            
    @pyqtSlot()
    def on_btnMove2_clicked(self):
        if self.isRotatorConnected:
            pos2Stage = float(self.txtPos2.text())
            self.setangle(self.con, pos2Stage, self.angleErr)
        else:
            print("Please Connect Rotator")
    
    @pyqtSlot()        
    def msgbtn(self,i):
        print ("Button pressed is:",i.text())
	
    
    def connectRotator(self):
        # open APT controller
        SN = int(self.txtSN.text())
        self.btnConnect.setText('Connecting')
        self.con = aptlib.PRM1(serial_number=SN)
        home = self.cbHome.isChecked()
        if home:
            self.con.home()
        self.btnConnect.setText('Disconnect Rotator')
        self.btnConnect.setStyleSheet("background-color: red")
        self.isRotatorConnected = True
        self.txtSN.setEnabled(False)
        self.btnMove1.setEnabled(True)
        self.btnMove2.setEnabled(True)
            
    def disconnectRotator(self):
        if self.isRotatorConnected:
            self.con.close()
            self.isRotatorConnected = False
            self.btnConnect.setText('Connect Rotator')
            self.btnConnect.setStyleSheet("")
            self.txtSN.setEnabled(True)
            self.btnMove1.setEnabled(False)
            self.btnMove2.setEnabled(False)
      
    def connectLCR(self):
        port=self.txtPort.text()
        self.lcc = ik.thorlabs.LCC25.open_serial(port, 115200,timeout=1)
        self.lcc.mode = self.lcc.Mode.voltage1
        self.lcc.enable = True
        self.btnConnectLCR.setText('Disconnect LCR')
        self.btnConnectLCR.setStyleSheet("background-color: red")
        self.isLCRConnected = True
        self.txtPort.setEnabled(False)
    
    def disconnectLCR(self):
        if self.isLCRConnected:
            self.lcc.enable = False
            self.btnConnectLCR.setText('Connect LCR')
            self.btnConnectLCR.setStyleSheet("")
            self.isLCRConnected= False
            self.txtPort.setEnabled(True)
        
    def connectPWM(self):
        self.isPWMConnected=True
        self.isSPADConnected = False
        self.btnConnectPWM.setText('Disconnect PWM')
        self.btnConnectPWM.setStyleSheet("background-color: red")
        self.average = int(self.txtAverage.text())
        self.pause = float(self.txtPause.text())
        self.pause = self.pause *1e-3
        self.btnConnectSPAD.setEnabled(False)
        self.txtAverage.setEnabled(False)
        self.txtPause.setEnabled(False)
        
    def disconnectPWM(self):
        if self.isPWMConnected:
            self.isPWMConnected=False
            self.btnConnectPWM.setText('Connect PWM')
            self.btnConnectPWM.setStyleSheet("")
            self.btnConnectSPAD.setEnabled(True)
            self.txtAverage.setEnabled(True)
            self.txtPause.setEnabled(True)
        
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
        self.txtSPADChannel.setEnabled(False)
        self.txtSPADOtherChannel.setEnabled(False)
        self.txtDelay.setEnabled(False)
        self.txtOtherDelay.setEnabled(False)
        self.txtExposure.setEnabled(False)
        
    def disconnectSPAD(self):
        if self.isSPADConnected:
            self.isSPADConnected=False
            self.btnConnectSPAD.setText('Connect SPAD')
            self.btnConnectSPAD.setStyleSheet("")
            self.btnConnectPWM.setEnabled(True)
            self.txtSPADChannel.setEnabled(True)
            self.txtSPADOtherChannel.setEnabled(True)
            self.txtDelay.setEnabled(True)
            self.txtOtherDelay.setEnabled(True)
            self.txtExposure.setEnabled(True)
        
    def setangle(self, rot, angle, angleErr):
        if abs(rot.position()-angle)> angleErr:
            rot.goto(angle, wait=True)
    
    def loadsettings(self):
        try:
            loadfilename=self.txtLoadFileName.text()
            with open(loadfilename) as json_data:
                settings = json.load(json_data)
                json_data.close()
            if "outputFileName" in settings:
                self.txtFileName.setText(settings["outputFileName"])
            if "modeVoltage" in settings:
                mode=settings["modeVoltage"]
                if mode=="Complete":
                    self.rbtnComplete.setChecked(True)
                    self.rbtnFast.setChecked(False)
                    self.rbtnAimed.setChecked(False)
                elif mode=="Fast":
                    self.rbtnComplete.setChecked(False)
                    self.rbtnFast.setChecked(True)
                    self.rbtnAimed.setChecked(False)
                elif mode=="Aimed":
                    self.rbtnComplete.setChecked(False)
                    self.rbtnFast.setChecked(False)
                    self.rbtnAimed.setChecked(True)
            if "allowTime" in settings:
                self.txtAllowTime.setText("{:5.2}".format(settings["allowTime"]))
            if "repetitions" in settings:
                self.txtRepetitions.setText("{0}".format(settings["repetitions"]))
            if "hibernation" in settings:
                self.txtHibernation.setText("{0}".format(settings["hibernation"]))
            if "pwmAverage" in settings:
                self.txtAverage.setText("{0}".format(settings["pwmAverage"]))
            if "pwmWait" in settings:
                self.txtPause.setText("{0}".format(settings["pwmWait"]))
            if "spadExposure" in settings:
                self.txtExposure.setText("{0}".format(settings["spadExposure"]))
            if "spadChannel" in settings:
                self.txtSPADChannel.setText("{0}".format(settings["spadChannel"]))
            if "spadOtherChannel" in settings:
                self.txtSPADOtherChannel.setText("{0}".format(settings["spadOtherChannel"]))
            if "spadDelay" in settings:
                self.txtDelay.setText("{:8.3}".format(settings["spadDelay"]))
            if "spadOtherDelay" in settings:
                self.txtOtherDelay.setText("{:8.3}".format(settings["spadOtherDelay"]))
            if "port" in settings:
                self.txtPort.setText(settings["port"])
            if "sn" in settings:
                self.txtSN.setText("{0}".format(settings["sn"]))
            if "home" in settings:
                self.cbHome.setChecked(settings["home"])
            if "pos1" in settings:
                self.txtPos1.setText("{:10.5}".format(settings["pos1"]))
            if "pos2" in settings:
                self.txtPos2.setText("{:10.5}".format(settings["pos2"]))
            self.disconnectPWM()
            self.disconnectSPAD()
            self.disconnectRotator()
            self.disconnectLCR()
        except Exception as e:
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = Vis()
    window.show()
    sys.exit(app.exec_())
