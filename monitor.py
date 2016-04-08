# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:43:23 2016

@author: sagnac
"""

import sys
from PyQt4 import QtCore,QtGui,uic
import pyqtgraph as pg
import numpy as np


#import os
#if 'LD_LIBRARY_PATH' in os.environ.keys():
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/:'+os.environ['LD_LIBRARY_PATH']
#else:
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/'
        

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

qtCreatorFile = 'monitor.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Monitor(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background', 'w')      # sets background to white                                                 
        pg.setConfigOption('foreground', 'k')      # sets axis color to black 

        self.setupUi(self)
        self.btnStart.clicked.connect(self.Start)
        self.tabWidget.currentChanged.connect(self.SetupView)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdateView)
        
        self.curTab = self.tabWidget.currentIndex()
        self.SetupView(self.curTab)

        self.pltMonitor.setMouseEnabled(x=False,y=False)
        
#        self.figMonitor = plt.figure()
#        self.plotMonitor = FigureCanvas(self.figMonitor)
#        self.pltMonitor.addWidget(self.plotMonitor)
#        self.axMonitor = self.figMonitor.add_subplot(111)
#        self.axMonitor.hold(False)
        
        
        self.inAcq = False
        
        self.getParameters()
        
    def SetupView(self,index):
        self.curTab = index
        if self.curTab == 0:
            # three state view
            self.txtDelay5.setEnabled(True)
            self.txtDelay6.setEnabled(True)
        elif self.curTab == 1:
            # visibility view
            self.txtDelay5.setEnabled(False)
            self.txtDelay6.setEnabled(False)
        
    def getParameters(self):
        self.bufNum = int(self.txtBufferNo.text())
        self.delay = np.array([float(self.txtDelay1.text()), float(self.txtDelay2.text()),
                               float(self.txtDelay3.text()),float(self.txtDelay4.text())])
        if self.curTab==0:
            self.delay = np.concatenate( (self.delay,np.array([float(self.txtDelay5.text()),float(self.txtDelay6.text())])) ) 
        
        self.delay = self.delay*1e-9
        
        self.exptime = float(self.txtExp.text())/1000
        self.pause = float(self.txtPause.text())
        self.coincWindow = float(self.txtWindow.text())*1e-9
        
    def Start(self):
        if not self.inAcq:
            self.inAcq = True
            self.txtPause.setEnabled(False)
            self.txtBufferNo.setEnabled(False)
            self.btnStart.setStyleSheet('background-color: red')
            self.btnStart.setText('Stop')

            self.getParameters()
            self.timer.start(self.pause)

            self.ttagBuf = ttag.TTBuffer(self.bufNum)            
            
        else:
            self.timer.stop()
            self.inAcq = False    
            self.txtPause.setEnabled(True)
            self.txtBufferNo.setEnabled(True)
            self.btnStart.setStyleSheet('')
            self.btnStart.setText('Start')   
    
    def UpdateView(self):
        self.getParameters()
        self.Monitor()
        
    def Monitor(self):
        if self.curTab == 0:
            chs = np.arange(6)
            singles = self.ttagBuf.singles(self.exptime)[:6]
            bg = pg.BarGraphItem(x=chs, height=singles, width=0.7, brush='b')
            txt1 = pg.TextItem(text=str(singles[0]),color='k', anchor=(0.5,3.2))
            self.pltMonitor.clear()
            self.pltMonitor.addItem(bg)
            self.pltMonitor.addItem(txt1)
            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Monitor()
    window.show()
    sys.exit(app.exec_())
