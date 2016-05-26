import sys
from PyQt4 import QtCore,QtGui,uic
import pyqtgraph as pg
import numpy as np
import time

#import os
#if 'LD_LIBRARY_PATH' in os.environ.keys():
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/:'+os.environ['LD_LIBRARY_PATH']
#else:
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/'
        

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

sys.path.append('../pyAPT')
import pyAPT

qtCreatorFile = 'timebin.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

timeAfterPlateMove = 1

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

        self.pltVisibility.setMouseEnabled(x=False,y=False)  
        self.btnSaveData.setEnabled(False)

        self.inAcq = False
        self.connected = False
        self.runStart = 0

        self.getParameters()
        self.Ncounts = []
    
    def SaveData(self):
        data = np.array(self.Ncounts)
        angles = np.arange(self.iniAngle, self.finAngle, self.stepAngle)
        filename = self.txtFileName.text()
        np.savez(filename, data=data, angles=angles)
        
    def getParameters(self):
        self.bufNum = int(self.txtBufferNo.text())
        self.integrationTime = float(self.txtIntTime.text())
        self.stepAngle = float(self.txtStpAngle.text())
        self.iniAngle = float(self.txtIniAngle.text())
        self.finAngle = float(self.txtFinAngle.text())
        
        if self.finAngle < self.iniAngle and self.stepAngle > 0:
            self.stepAngle = -self.stepAngle
        if self.finAngle > self.iniAngle and self.stepAngle < 0:
            self.stepAngle = -self.stepAngle
                
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
            for angle in np.arange(self.iniAngle, self.finAngle, self.stepAngle):
                QtGui.qApp.processEvents()
                if not self.inAcq:
                    break
                
                self.con.goto(angle,wait=True) ## Move plate to angle=angle
                time.sleep(0.1)
                
                self.ttagBuf.start()
                time.sleep(self.integrationTime/.9)
                self.ttagBuf.stop()
                time.sleep(.1)
           #     print(self.ttagBuf.singles(self.integrationTime))
           #     print(self.Ncounts)
           #     print()
                if self.Ncounts.size == 0:
                  self.Ncounts = np.array(self.ttagBuf.singles(self.integrationTime))
                  self.Ncounts = self.Ncounts[np.newaxis,:]
                else:
                  self.Ncounts = np.vstack( (self.Ncounts,self.ttagBuf.singles(self.integrationTime)) )
                
                
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
        y = self.Ncounts[:,0]
        y2 = self.Ncounts[:,1]
        ytot = self.Ncounts[:,0] + self.Ncounts[:,1]
        
        plot1 = pg.ScatterPlotItem(x,y,symbol='s')
        plot2 = pg.ScatterPlotItem(x,y2)
        plotTot = pg.ScatterPlotItem(x,ytot,symbol='+')
        
        self.pltVisibility.clear()
        self.pltVisibility.addItem(plot1)
        self.pltVisibility.addItem(plot2)
        self.pltVisibility.addItem(plotTot)

        maxN = np.amax(ytot)
        minN = np.amin(ytot)
        self.txtMaxVis.setText(str((maxN - minN) / (maxN + minN)*100) + "%")
        
    
    def Connect(self):
        if not self.connected:
            self.connected = True
            self.btnConnect.setStyleSheet('background-color: red')
            self.btnConnect.setText('Disconnect')
            self.SN = int(self.txtSN.text())
            self.con = pyAPT.PRM1(serial_number=self.SN)
        else:            
            self.connected =  False
            self.con.close()
            self.btnConnect.setStyleSheet('')            
            self.btnConnect.setText('Connect')


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Visibility()
    window.show()
    sys.exit(app.exec_())
