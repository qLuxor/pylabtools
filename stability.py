import sys
from PyQt4 import QtCore, QtGui, uic

import pyqtgraph as pg
import numpy as np

import threading
import time

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

qtCreatorFile = 'stability.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Stability(QtGui.QMainWindow, Ui_MainWindow):

    # Signal emitted when new data are ready
    dataReady = QtCore.pyqtSignal(tuple)

    # Signal emitted when new data are to be saved
    saveReady = QtCore.pyqtSignal(tuple)

    def __init__(self):

        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        self.setupUi(self)

        self.btnStart.clicked.connect(self.Start)
        self.dataReady.connect(self.updateUI)

        self.saveReady.connect(self.saveData)
        self.saveInterval = 30
        self.clock = QtCore.QTime()

        self.inAcq = False


    def Start(self):
        if not self.inAcq:
            self.inAcq = True
            self.txtExposure.setEnabled(False)
            self.cmbSource.setEnabled(False)
            self.txtBufNo.setEnabled(False)
            self.cmbChannel.setEnabled(False)
            self.chkSave.setEnabled(False)

            self.btnStart.setText('Stop')
            self.btnStart.setStyleSheet('background-color: red')

            self.exposure = float(self.txtExposure.text())/1000.
            self.channel = self.cmbChannel.currentIndex()
            self.bufNo = int(self.txtBufNo.text())

            self.ttagBuf = ttag.TTBuffer(self.bufNo)

            self.counts = []
            self.time = []
            self.index = 0

            self.saveFlag = self.chkSave.isChecked()

            if self.saveFlag:
                self.saveFile = QtGui.QFileDialog.getSaveFileName(self,'Save file','/home/saganc/doubleCHSH/','*.npz')
                self.saveTime = 0

            self.clock.start()

            self.stopAcq = threading.Event()
            self.c_thread = threading.Thread(target=self.funcAcq, args=(self.stopAcq,))
            self.c_thread.start()
        else:
            self.inAcq = False
            self.stopAcq.set()
            
            self.txtExposure.setEnabled(True)
            self.cmbSource.setEnabled(True)
            self.txtBufNo.setEnabled(True)
            self.cmbChannel.setEnabled(True)
            self.chkSave.setEnabled(True)

            self.btnStart.setText('Start')
            self.btnStart.setStyleSheet('')

    def updateUI(self,data):
        x = data[0]
        y = data[1]

        pl1 = pg.ScatterPlotItem(x,y)
        self.pltOscilloscope.clear()
        self.pltOscilloscope.addItem(pl1)

        self.lblMin.setText(str(self.minCount))
        self.lblMax.setText(str(self.maxCount))
        self.lblMean.setText(str(self.meanCount))
        self.lblStd.setText(str(self.stdCount))


    def funcAcq(self,stopAcq):
        while not stopAcq.isSet():
            time.sleep(self.exposure/0.9)
            self.singles = self.ttagBuf.singles(self.exposure)

            self.counts.append(self.singles[self.channel])
            self.time.append(self.clock.elapsed()/1000.)
            self.index += 1

            #print(self.index,self.time[-1],self.counts[-1])

            x = np.array(self.time)
            y = np.array(self.counts)

            #pl1 = pg.ScatterPlotItem(x,y)
            #self.pltOscilloscope.clear()
            #self.pltOscilloscope.addItem(pl1)

            # compute statistics on the array
            self.minCount = np.amin(y)
            self.maxCount = np.amax(y)
            self.meanCount = np.mean(y)
            self.stdCount = np.std(y)

            #self.lblMin.setText(str(self.minCount))
            #self.lblMax.setText(str(self.maxCount))
            #self.lblMean.setText(str(self.meanCount))
            #self.lblStd.setText(str(self.stdCount))
    
            if self.saveFlag and (stopAcq.isSet() or ((self.time[-1] - self.saveTime) > self.saveInterval) ):
                self.saveTime = self.time[-1]
                self.saveReady.emit( (x,y) )

            self.dataReady.emit( (x,y) )

    def saveData(self, data):
        self.save_thread = threading.Thread(target=self.saveThreadFunc,args=(data,))
        self.save_thread.start()

    def saveThreadFunc(self, data):
        time = data[0]
        count = data[1]

        np.savez(self.saveFile,time=time,count=count)
        


if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Stability()
    window.show()
    sys.exit(app.exec_())
