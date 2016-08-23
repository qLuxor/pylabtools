import sys
from PyQt4 import QtGui,uic
import pyqtgraph as pg
import numpy as np
import time
from scipy.optimize import curve_fit

#import os
#if 'LD_LIBRARY_PATH' in os.environ.keys():
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/:'+os.environ['LD_LIBRARY_PATH']
#else:
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/'
        

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('..')
import aptlib 

qtCreatorFile = 'timebin.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

timeAfterPlateMove = 1

rad_to_grad = 180./np.pi

class Visibility(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background', 'w')      # sets background to white                                                 
        pg.setConfigOption('foreground', 'k')      # sets axis color to black 

        self.setupUi(self)
        self.btnStart.clicked.connect(self.Start)
        self.btnConnect.clicked.connect(self.Connect)
        self.btnSaveData.clicked.connect(self.SaveData)
        self.btnMakeFit.clicked.connect(self.MakeFit)

        self.pltVisibility.setMouseEnabled(x=False,y=False)  
        self.btnSaveData.setEnabled(False)

        self.inAcq = False
        self.connected = False
        self.runStart = 0

        self.getParameters()
        self.Ncounts = []
    
    def SaveData(self):
        data = np.array(self.Ncounts)
        angles = self.anglePlate #np.arange(self.iniAngle, self.finAngle, self.stepAngle)
        filename = self.txtFileName.text()
        np.savez(filename, data=data, angles=angles)
        
    def getParameters(self):
        #Channels
        self.Ch0 = int(self.txtCh0.text())
        self.Ch1 = int(self.txtCh1.text())
        
        self.bufNum = int(self.txtBufferNo.text())
        self.integrationTime = float(self.txtIntTime.text())
        self.stepAngle = float(self.txtStpAngle.text())
        self.iniAngle = float(self.txtIniAngle.text())
        self.finAngle = float(self.txtFinAngle.text())
        
        if self.finAngle < self.iniAngle and self.stepAngle > 0:
            self.stepAngle = -self.stepAngle
        if self.finAngle > self.iniAngle and self.stepAngle < 0:
            self.stepAngle = -self.stepAngle
        
        #Fit parameters
        self.phase0 = float(self.txtPhase0.text())
        self.phase1 = float(self.txtPhase1.text())
        self.maxIntensity0 = float(self.txtMaxIntensity0.text())
        self.maxIntensity1 = float(self.txtMaxIntensity1.text())
        self.noise0 = float(self.txtNoise0.text())
        self.noise1 = float(self.txtNoise1.text())
        self.xi = float(self.txtXi.text())
        self.zeroAngle = float(self.txtAngle0.text())
                
    def Start(self):
        if not self.connected:
            print('Connect the rotator before starting acquisition')
            return
        
        self.btnConnect.setEnabled(False)
        if not self.inAcq:
            self.inAcq = True

            self.txtBufferNo.setEnabled(False)
            self.btnStart.setStyleSheet('background-color: red')
            self.btnStart.setText('Stop')

            self.getParameters()
            
            self.runStart += 1
            if self.runStart > 1:
                return
            self.UpdateLabels()
            print('Acquisition started') 
            self.ttagBuf = ttag.TTBuffer(self.bufNum) 
            self.btnSaveData.setEnabled(True)
            self.Ncounts = np.array([])
            self.anglePlate = np.array([])
            for angle in np.arange(self.iniAngle, self.finAngle, self.stepAngle):
                QtGui.qApp.processEvents()
                if not self.inAcq:
                    break
                
                self.con.goto(float(angle),wait=True) ## Move plate to angle=angle
                time.sleep(0.1)
                
                self.ttagBuf.start()
                time.sleep(self.integrationTime/.9)
                self.ttagBuf.stop()
                time.sleep(.1)
                
                if self.Ncounts.size == 0:
                  self.Ncounts = np.array(self.ttagBuf.singles(self.integrationTime))
                  self.Ncounts = self.Ncounts[np.newaxis,:]
                else:
                  self.Ncounts = np.vstack( (self.Ncounts,self.ttagBuf.singles(self.integrationTime)) )
                
                self.anglePlate = np.concatenate((self.anglePlate, [angle]))
                time.sleep(timeAfterPlateMove)
                self.UpdateView()
                
            self.runStart = 0
            self.btnConnect.setEnabled(True)
            print('Acquisition stopped') 
        
        self.inAcq = False    
        self.txtBufferNo.setEnabled(True)
        self.btnStart.setStyleSheet('')
        self.btnStart.setText('Start')   

    def UpdateView(self):
        self.PlotSingles()
        self.LabelTotalTime()
        self.LabelTimeLeft()
        
    def UpdateLabels(self):
        self.LabelTotalTime()
        self.LabelTimeLeft()
                
    def LabelTimeLeft(self):
        self.txtTimeLeft.setText(str(self.totalTime - len(self.Ncounts)*\
                                 (self.integrationTime/.9 + timeAfterPlateMove)) + " s")
        
    def LabelTotalTime(self):
        self.totalTime = (self.integrationTime/.9 + timeAfterPlateMove +.1) * np.arange(self.iniAngle, self.finAngle, self.stepAngle).size
        self.txtTotTime.setText(str(self.totalTime) + " s")
        
    def PlotSingles(self):
        x = np.arange(self.iniAngle, self.finAngle, self.stepAngle)[:len(self.Ncounts)]
        y = self.Ncounts[:,self.Ch0]
        y2 = self.Ncounts[:,self.Ch1]
        ytot = self.Ncounts[:,self.Ch0] + self.Ncounts[:,self.Ch1]
        
        plot1 = pg.ScatterPlotItem(x,y,symbol='s')
        plot2 = pg.ScatterPlotItem(x,y2)
        plotTot = pg.ScatterPlotItem(x,ytot,symbol='+')
        
        self.pltVisibility.clear()
        if self.checkCh0.isChecked():
            self.pltVisibility.addItem(plot1)
        if self.checkCh1.isChecked():
            self.pltVisibility.addItem(plot2)
        self.pltVisibility.addItem(plotTot)

        maxN0 = np.amax(y)
        minN0 = np.amin(y)
        maxN1 = np.amax(y2)
        minN1 = np.amin(y2)
        vis0 = (maxN0 - minN0) / (maxN0 + minN0)*100
        vis1 = (maxN1 - minN1) / (maxN1 + minN1)*100
        self.txtMaxVis0.setText("{:.4f}".format(vis0) + "%")
        self.txtMaxVis1.setText("{:.4f}".format(vis1) + "%")

    # model of the intensity
    def intensity(self, angle, I0, phi0, xi, angle0, noise):
        if self.checkFitSameXi.isChecked():
            xi = self.xi
        return np.abs(I0)*np.sin(xi/np.cos(angle-angle0) + phi0)**2 + noise
    
    def MakeFit(self):
        self.getParameters()
        # fit channels
        popt0 = [self.maxIntensity0, self.phase0, self.xi, self.zeroAngle/rad_to_grad, self.noise0]
        popt1 = [self.maxIntensity1, self.phase1, self.xi, self.zeroAngle/rad_to_grad, self.noise1]
        if not self.checkFitGuess.isChecked():
            if self.checkCh0.isChecked():
                popt0, pcov0 = curve_fit(self.intensity, self.anglePlate/rad_to_grad, self.Ncounts[:,self.Ch0], p0 = popt0)
            if self.checkCh1.isChecked():
                popt1, pcov1 = curve_fit(self.intensity, self.anglePlate/rad_to_grad, self.Ncounts[:,self.Ch1], p0 = popt1)
        
        popt0[1] = popt0[1] % np.pi
        popt1[1] = popt1[1] % np.pi

        # plot fit
        numAng = len(self.anglePlate)
        x = np.linspace(self.anglePlate[0], self.anglePlate[numAng-1], numAng*100) /rad_to_grad
        self.pltVisibility.clear()
        if self.checkCh0.isChecked():
            fit_counts0 = self.intensity(x, popt0[0], popt0[1], popt0[2], popt0[3], popt0[4])
            self.pltVisibility.plot(x*rad_to_grad, fit_counts0,pen=pg.mkPen('r', width=3))
        if self.checkCh1.isChecked():
            fit_counts1 = self.intensity(x, popt1[0], popt1[1], popt1[2], popt1[3], popt1[4])
            self.pltVisibility.plot(x*rad_to_grad, fit_counts1,pen=pg.mkPen('b', width=3))
        
        # plot data
        x = np.arange(self.iniAngle, self.finAngle, self.stepAngle)[:len(self.Ncounts)]
        y = self.Ncounts[:,self.Ch0]
        y2 = self.Ncounts[:,self.Ch1]
        ytot = self.Ncounts[:,self.Ch0] + self.Ncounts[:,self.Ch1]
        
        plot1 = pg.ScatterPlotItem(x,y,symbol='s')
        plot2 = pg.ScatterPlotItem(x,y2)
        plotTot = pg.ScatterPlotItem(x,ytot,symbol='+')
        if self.checkCh0.isChecked():
            self.pltVisibility.addItem(plot1)
        if self.checkCh1.isChecked():
            self.pltVisibility.addItem(plot2)
        self.pltVisibility.addItem(plotTot)
        
        # set parameters fit
        self.txtFitPhase0.setText("{:.4f}".format(popt0[1]))
        self.txtFitPhase1.setText("{:.4f}".format(popt1[1]))
        self.txtFitMaxIntensity0.setText("{:.4e}".format(popt0[0]))
        self.txtFitMaxIntensity1.setText("{:.4e}".format(popt1[0]))
        self.txtFitNoise0.setText("{:.0f}".format(popt0[4]))
        self.txtFitNoise1.setText("{:.0f}".format(popt1[4]))
        self.txtFitXi.setText("{:4.2f}".format(popt0[2]))
        self.txtFitAngle0.setText("{:4.4f}".format(popt0[3]))
        self.txtDiffPhase.setText("{:.5f}".format(popt0[1] - popt1[1]))
        

    def Connect(self):
        if not self.connected:
            self.connected = True
            self.btnConnect.setStyleSheet('background-color: red')
            self.btnConnect.setText('Disconnect')
            self.SN = int(self.txtSN.text())
            self.con = aptlib.PRM1(serial_number=self.SN)
        else:            
            self.connected =  False
            self.con.close()
            self.btnConnect.setStyleSheet('')            
            self.btnConnect.setText('Connect')


if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Visibility()
    window.show()
    sys.exit(app.exec_())
