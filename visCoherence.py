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

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

import json
import logging
import traceback
import datetime

qtCreatorFile = 'visCoherence.ui'

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
        
        self.isLinStageConnected = False
        self.isPWMConnected = False
        self.isSPADConnected = False
        
        self.bufNum=0
        
        self.coincWindow = 1*1e-9
        
        self.posErr=1e-6
        
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
        
        self.btnMoveMin.setEnabled(False)
        self.btnMoveMax.setEnabled(False)
        self.btnMoveUp.setEnabled(False)
        self.btnMoveDown.setEnabled(False)
        
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
                print("Please connect a sensor")
                return
            
            if not self.isLinStageConnected:
                self.connectLinStage()
            
            self.started = True
            
            self.btnStart.setStyleSheet("background-color: red")
            self.btnStart.setText('Stop')
            self.btnConnect.setEnabled(False)
            self.btnConnectPWM.setEnabled(False)
            self.btnConnectSPAD.setEnabled(False)
            self.btnOscilloscope.setEnabled(False)
            self.txtPosMin.setEnabled(False)
            self.txtPosMax.setEnabled(False)
            self.txtStep.setEnabled(False)
            self.btnMoveMin.setEnabled(False)
            self.btnMoveMax.setEnabled(False)
            self.btnMoveUp.setEnabled(False)
            self.btnMoveDown.setEnabled(False)
            self.btnLoad.setEnabled(False)
                
            self.allowtime=float(self.txtAllowTime.text())
            
            self.repetitions= int(self.txtRepetitions.text())
            if self.repetitions <1:
                self.repetitions=1    
                
            self.hibernation =float(self.txtHibernation.text())
            
            posMinStage = float(self.txtPosMin.text())
            posMaxStage = float(self.txtPosMax.text())
            stepStage = float(self.txtStep.text())
            
            self.pos_arr = np.arange(posMinStage, posMaxStage, stepStage)
            for cont in range(self.repetitions):
                i = 0                
                self.count = np.zeros(self.pos_arr.size)
                self.countA = np.zeros(self.pos_arr.size)
                self.countB = np.zeros(self.pos_arr.size)
                self.resultdata={}
                starttime=datetime.datetime.now()
                if posMinStage > 0.02:
                    self.setPos(self.con, posMinStage-0.02, self.posErr)
                    time.sleep(self.allowtime)
                for pos in self.pos_arr:
                    self.setPos(self.con, pos, self.posErr)
                    
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
                            self.countA[i]=self.count[i]
                            self.countB[i]=self.count[i]
                        else:
                            coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
                            self.count[i]=coincidences[self.SPADChannel, self.SPADOtherChannel]
                            self.countA[i]=coincidences[self.SPADChannel, self.SPADChannel]
                            self.countB[i]=coincidences[self.SPADOtherChannel, self.SPADOtherChannel]
                    self.axVis.plot(self.pos_arr, self.count, '.')
                    self.plotVis.draw()
                    self.lblPowerStart.setText("{:.3}".format(float(self.count[i])))
                    self.lblPosStart.setText("{:.3}".format(float(pos)))
                    i += 1
                
                if self.started:
                    filename = self.txtFileName.text()
                    if self.repetitions>1:
                        filename = filename+"_"+str(cont+1)
                    np.savez(filename, pos=self.pos_arr, count=self.count, countA=self.countA, countB=self.countB)
                    minpower=np.min(self.count)
                    maxpower=np.max(self.count)
                    stoptime=datetime.datetime.now()
                    self.resultdata.update({"RawMaxPower":maxpower, "RawMinPower": minpower, "StartTime":str(starttime), "StopTime":str(stoptime)})
                    with open(filename+".json", 'w') as outfile:
                        json.dump(self.resultdata, outfile)
                    time.sleep(self.hibernation)
                else:
                    break
            
            self.btnStart.setStyleSheet("")
            self.btnStart.setText('Start')
            self.btnConnect.setEnabled(True)
            self.btnConnectPWM.setEnabled(True)
            self.btnConnectSPAD.setEnabled(True)
            self.btnOscilloscope.setEnabled(True)
            self.txtPosMin.setEnabled(True)
            self.txtPosMax.setEnabled(True)
            self.txtStep.setEnabled(True)
            self.btnMoveMin.setEnabled(True)
            self.btnMoveMax.setEnabled(True)
            self.btnMoveUp.setEnabled(True)
            self.btnMoveDown.setEnabled(True)
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
        if not self.isLinStageConnected:
            self.connectLinStage()
        else:
            self.disconnectLinStage()
       
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
    def on_btnMoveMin_clicked(self):
        if self.isLinStageConnected:
            posMinStage = float(self.txtPosMin.text())
            self.setPos(self.con, posMinStage, self.posErr)
        else:
            print("Please Connect LinStage")
            
    @pyqtSlot()
    def on_btnMoveMax_clicked(self):
        if self.isLinStageConnected:
            posMaxStage = float(self.txtPosMax.text())
            self.setPos(self.con, posMaxStage, self.posErr)
        else:
            print("Please Connect LinStage")
            
    @pyqtSlot()
    def on_btnMoveUp_clicked(self):
        if self.isLinStageConnected:
            step = float(self.txtStep.text())
            self.MoveUp(step, self.posErr)
        else:
            print("Please Connect LinStage")
            
    @pyqtSlot()
    def on_btnMoveDown_clicked(self):
        if self.isLinStageConnected:
            step = float(self.txtStep.text())
            self.MoveDown(step, self.posErr)
        else:
            print("Please Connect LinStage")
    
    def connectLinStage(self):
        # open APT controller
        SN = int(self.txtSN.text())
        self.btnConnect.setText('Connecting')
        self.con = aptlib.Z8XX(serial_number=SN)
        home = self.cbHome.isChecked()
        if home:
            self.con.home()
        self.btnConnect.setText('Disconnect LinStage')
        self.btnConnect.setStyleSheet("background-color: red")
        self.isLinStageConnected = True
        self.txtSN.setEnabled(False)
        self.btnMoveMin.setEnabled(True)
        self.btnMoveMax.setEnabled(True)
        self.btnMoveUp.setEnabled(True)
        self.btnMoveDown.setEnabled(True)
        pos=self.con.position()
        self.lblPosStart.setText("{:.3}".format(float(pos)))
            
    def disconnectLinStage(self):
        if self.isLinStageConnected:
            self.con.close()
            self.isLinStageConnected = False
            self.btnConnect.setText('Connect LinStage')
            self.btnConnect.setStyleSheet("")
            self.txtSN.setEnabled(True)
            self.btnMoveMin.setEnabled(False)
            self.btnMoveMax.setEnabled(False)
            self.btnMoveUp.setEnabled(False)
            self.btnMoveDown.setEnabled(False)
        
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
        
    def setPos(self, stage, pos, posErr):
        pos = float(pos)
        if abs(stage.position()-pos)> posErr:
            stage.goto(pos, wait=True)
            self.lblPosStart.setText("{:.3}".format(float(pos)))
            
    def MoveUp(self, step, posErr):
        if step >= posErr:
            self.con.move(step)
        pos=self.con.position()
        self.lblPosStart.setText("{:.3}".format(float(pos)))
    
    def MoveDown(self, step, posErr):
        if step >= posErr:
            self.con.move(-step)
        pos=self.con.position()
        self.lblPosStart.setText("{:.3}".format(float(pos)))
    
    def loadsettings(self):
        try:
            loadfilename=self.txtLoadFileName.text()
            with open(loadfilename) as json_data:
                settings = json.load(json_data)
                json_data.close()
            if "outputFileName" in settings:
                self.txtFileName.setText(settings["outputFileName"])
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
            if "posMin" in settings:
                self.txtPosMin.setText("{:10.5}".format(settings["posMin"]))
            if "posMax" in settings:
                self.txtPosMax.setText("{:10.5}".format(settings["posMax"]))
            if "step" in settings:
                self.txtStep.setText("{:10.5}".format(settings["step"]))
            self.disconnectPWM()
            self.disconnectSPAD()
            self.disconnectLinStage()
        except Exception as e:
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = Vis()
    window.show()
    sys.exit(app.exec_())
