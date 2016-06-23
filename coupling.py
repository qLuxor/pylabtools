import sys
from PyQt4 import QtGui,uic
import pyqtgraph as pg
import numpy as np
import time

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag


qtCreatorFile = 'coupling.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Coupling(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background', 'w')      # sets background to white                                                 
        pg.setConfigOption('foreground', 'k')      # sets axis color to black 

        self.setupUi(self)
        self.btnStart.clicked.connect(self.Start)
        self.inAcq = False

        self.countsCh = np.zeros(6)
        self.progressBarCh0.setValue(self.countsCh[0])
        self.progressBarCh1.setValue(self.countsCh[1])
        self.progressBarCh2.setValue(self.countsCh[2])
        self.progressBarCh3.setValue(self.countsCh[3])
        self.progressBarCh4.setValue(self.countsCh[4])
        self.progressBarCh5.setValue(self.countsCh[5])

        
            
    def Start(self):
        if not self.inAcq:
            self.inAcq = True
            
            self.txtBufferNo.setEnabled(False)
            self.btnStart.setStyleSheet('background-color: red')
            self.btnStart.setText('Stop')
            
            self.ttagBuf = ttag.TTBuffer(self.bufNum) 
        
            while (self.inAcq):
                QtGui.qApp.processEvents()
                self.getParameters()
                
                self.ttagBuf.start()
                time.sleep(self.integrationTime)
                self.ttagBuf.stop()
                time.sleep(.1)
                self.countsCh = self.ttagBuf.singles(self.IntegrationTime)
                
                #self.countsCh = np.ones(6)*1.9
                #time.sleep(.5)
                
                self.SetProgressBars()
                
        self.inAcq = False

    def SetProgressBars(self):
        countsCh = (self.countsCh - self.Min) / (self.Max - self.Min) * 100.
        self.progressBarCh0.setValue(countsCh[0])
        self.progressBarCh1.setValue(countsCh[1])
        self.progressBarCh2.setValue(countsCh[2])
        self.progressBarCh3.setValue(countsCh[3])
        self.progressBarCh4.setValue(countsCh[4])
        self.progressBarCh5.setValue(countsCh[5])
        
        self.txtCounts0.setText(str(self.countsCh[0]))
        self.txtCounts1.setText(str(self.countsCh[1]))
        self.txtCounts2.setText(str(self.countsCh[2]))
        self.txtCounts3.setText(str(self.countsCh[3]))
        self.txtCounts4.setText(str(self.countsCh[4]))
        self.txtCounts5.setText(str(self.countsCh[5]))
        
    def getParameters(self):
        self.MinCh0 = float(self.txtMinCh0.text())
        self.MinCh1 = float(self.txtMinCh1.text())
        self.MinCh2 = float(self.txtMinCh2.text())
        self.MinCh3 = float(self.txtMinCh3.text())
        self.MinCh4 = float(self.txtMinCh4.text())
        self.MinCh5 = float(self.txtMinCh5.text())
        self.Min = np.array([self.MinCh0, self.MinCh1, self.MinCh2, self.MinCh3, self.MinCh4, self.MinCh5])

        self.MaxCh0 = float(self.txtMaxCh0.text())
        self.MaxCh1 = float(self.txtMaxCh1.text())
        self.MaxCh2 = float(self.txtMaxCh2.text())
        self.MaxCh3 = float(self.txtMaxCh3.text())
        self.MaxCh4 = float(self.txtMaxCh4.text())
        self.MaxCh5 = float(self.txtMaxCh5.text())
        self.Max = np.array([self.MaxCh0, self.MaxCh1, self.MaxCh2, self.MaxCh3, self.MaxCh4, self.MaxCh5])
        
        self.IntegrationTime = float(self.txtIntTime.text())
        self.BuffNo = float(self.txtBufferNo.text())


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Coupling()
    window.show()
    sys.exit(app.exec_())
