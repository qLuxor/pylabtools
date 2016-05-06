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

timeAfterPlateMove = 1.

class Visibility(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background', 'w')      # sets background to white                                                 
        pg.setConfigOption('foreground', 'k')      # sets axis color to black 

        self.setupUi(self)
        self.btnStart.clicked.connect(self.Start)
        self.btnConnect.clicked.connect(self.Connect)

        self.pltVisibility.setMouseEnabled(x=False,y=False)  

        self.inAcq = False
        self.connected = False
        self.runStart = 0

        self.getParameters()
        self.Ncounts = []
        
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
            self.Ncounts = []
            for angle in np.arange(self.iniAngle, self.finAngle, self.stepAngle):
                QtGui.qApp.processEvents()
                if not self.inAcq:
                    break
                self.ttagBuf.start()
                time.sleep(self.integrationTime/.9)
                self.ttagBuf.stop()
                time.sleep(.1)
                self.Ncounts.append(sum(self.ttagBuf.singles(self.integrationTime)))
                
                self.con.move(self.stepAngle) ## Move plate to angle=angle
                
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
        self.LabelMaxVis()
        self.LabelTotalTime()
        self.LabelTimeLeft()
        
    def UpdateLabels(self):
        self.LabelTotalTime()
        self.LabelTimeLeft()
                
    def LabelMaxVis(self):        
        maxN = np.amax(np.array(self.Ncounts))
        minN = np.amin(np.array(self.Ncounts))
        self.txtMaxVis.setText(str((maxN - minN) / (maxN + minN)*100) + "%")
        
    def LabelTimeLeft(self):
        self.txtTimeLeft.setText(str(self.totalTime - len(self.Ncounts)*\
                                 (self.integrationTime/.9 + timeAfterPlateMove)) + " s")
        
    def LabelTotalTime(self):
        self.totalTime = (self.integrationTime/.9 + timeAfterPlateMove +.1) * np.arange(self.iniAngle, self.finAngle, self.stepAngle).size
        self.txtTotTime.setText(str(self.totalTime) + " s")
    def PlotSingles(self):
        x = np.arange(self.iniAngle, self.finAngle, self.stepAngle)[:len(self.Ncounts)]
        y = np.array(self.Ncounts)
#        self.pltVisibility.plot(x,y)
#        ax = self.pltVisibility.getAxis('bottom')
        plot = pg.ScatterPlotItem(x,y)
        self.pltVisibility.clear()
        self.pltVisibility.addItem(plot)
#        self.pltVisibility.showGrid()
    
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
