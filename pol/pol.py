# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:43:23 2016

@author: sagnac
"""

import sys
from PyQt4 import QtCore,QtGui,uic
import pyqtgraph as pg
import numpy as np
import os

from scipy.optimize import curve_fit

import itertools

#import os
#if 'LD_LIBRARY_PATH' in os.environ.keys():
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/:'+os.environ['LD_LIBRARY_PATH']
#else:
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/'
        

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag

import config
import apparatus

qtCreatorFile = 'pol.ui'

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Monitor(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        pg.setConfigOption('background', 'w')      # sets background to white                                                 
        pg.setConfigOption('foreground', 'k')      # sets axis color to black 

        self.setupUi(self)
        self.btnStart.clicked.connect(self.Start)

        self.apparatus = apparatus.Apparatus()

        self.btnConfig.clicked.connect(self.showConfigUI)
        self.btnConnect.clicked.connect(self.connectApparatus)
        self.config = config.Config()
        self.configUI = config.ConfigUI(self.config,self.apparatus)
        self.btnMainDir.clicked.connect(self.SetMainDir)
        self.btnAutoMeasure.clicked.connect(self.autoStart)
        
        self.connected = False

        self.savetimer = QtCore.QTimer(self)
        self.savetimer.timeout.connect(self.SaveData)

        self.updatetimer = QtCore.QTimer(self)
        
        self.NumCh = 4

        self.pltMonitor.setMouseEnabled(x=False,y=False)  
        self.pltAlign.setMouseEnabled(x=False,y=False)  
        self.pltDelay.setMouseEnabled(x=False,y=False)  
        self.pltSingleVis.setMouseEnabled(x=False,y=False)  
        self.pltCoincVis.setMouseEnabled(x=False,y=False)  

        self.inAcq = False
        
        self.clock = QtCore.QTime()
        self.clock.start()
        self.saving = False
        self.maindir = ''
        self.saveStartIndex = 0
        self.saveCurIndex = 0
        self.saveInterval = 30
        self.savedSize = 0

        self.autoIndex = 0
        iters = [
                    [0,1], # outcome Bob1
                    [0,1], # Bob1
                    [0,1], # Bob2
                    [2,3]  # Alice
                ]
        self.autoBases = list(itertools.product(*iters))
        self.autoAcq = False

        self.getParameters()


    def showConfigUI(self):
        self.configUI.show()

    def connectApparatus(self):
        if not self.connected:
            self.config.setConfig(self.configUI.getConfigFromUI())
            try:
                self.apparatus.connect(self.config.getConfig())

            except Exception as e:
                print('Exception in rotator initialization')
                print(e.__doc__)

            self.configUI.connect()
            self.btnConnect.setStyleSheet('background-color: red')
            self.btnConnect.setText('Disconnect')
            self.connected = True

            # set visibility of the apparatus input fields
            a = self.apparatus
            if a.alice != None:
                self.lblAlice.setEnabled(True)
                if a.alice.hwp != None:
                    self.cmbBasisAlice.setEnabled(True)
            if a.bob1 != None:
                self.grpBob1.setEnabled(True)
                if a.bob1.hwp != None:
                    self.cmbBasisBob1.setEnabled(True)
                if a.bob1.phshift != None:
                    self.cmbPhaseBob1.setEnabled(True)
#                for i in range(len(a.bob1.weak)):
#                    if a.bob1.weak[i] != None:
#                        if a.bob1.weak[i].func == 'Weak HWP':
#                            self.txtEpsHWPBob1.setEnabled(True)
#                        elif a.bob1.weak[i].func == 'Weak QWP':
#                            self.txtEpsQWPBob1.setEnabled(True)
#                        elif a.bob1.weak[i].func == 'Compensation':
#                            self.txtCompBob1.setEnabled(True)
            if a.bob2 != None:
                self.lblBob2.setEnabled(True)
                if a.bob2.hwp != None:
                    self.cmbBasisBob2.setEnabled(True)
        else:
            self.apparatus.disconnect()
            self.configUI.disconnect()
            self.btnConnect.setText('Connect')
            self.btnConnect.setStyleSheet('')
            self.connected = False

            # disable apparatus input fields
            self.lblAlice.setEnabled(False)
            self.cmbBasisAlice.setEnabled(False)
            self.grpBob1.setEnabled(False)
            self.cmbBasisBob1.setEnabled(False)
            self.cmbPhaseBob1.setEnabled(False)
#            self.txtEpsHWPBob1.setEnabled(False)
#            self.txtEpsQWPBob1.setEnabled(False)
#            self.txtCompBob1.setEnabled(False)
            self.lblBob2.setEnabled(False)
            self.cmbBasisBob2.setEnabled(False)

    
        
        
    def getParameters(self):
        self.bufNum = int(self.txtBufferNo.text())
        self.delay = np.array([float(self.txtDelay1.text()), float(self.txtDelay2.text()),
                               float(self.txtDelay3.text()),float(self.txtDelay4.text())])
        self.delay = self.delay*1e-9
        
        self.exptime = float(self.txtExp.text())/1000
        self.pause = float(self.txtPause.text())
        self.coincWindow = float(self.txtWindow.text())*1e-9
        
        self.delayRange = float(self.txtRange.text())*1e-9

    def closeEvent(self,event):
        if self.connected:
            self.connectApparatus()
        self.configUI.close()
        
    def Start(self):
        if not self.inAcq:
            self.inAcq = True
            self.txtPause.setEnabled(False)
            self.txtBufferNo.setEnabled(False)
            self.btnStart.setStyleSheet('background-color: red')
            self.btnStart.setText('Stop')

            self.cmbBasisAlice.setEnabled(False)
            self.cmbBasisBob1.setEnabled(False)
            self.cmbBasisBob2.setEnabled(False)
            self.cmbPhaseBob1.setEnabled(False)
#            self.txtEpsHWPBob1.setEnabled(False)
#            self.txtEpsQWPBob1.setEnabled(False)
#            self.txtCompBob1.setEnabled(False)

            self.apparatus.setAlice(self.cmbBasisAlice.currentText())
            #self.apparatus.setBob1(self.cmbBasisBob1.currentText(),float(self.cmbPhaseBob1.text()),float(self.txtEpsHWPBob1.text()),float(self.txtEpsQWPBob1.text()),float(self.txtCompBob1.text()))
            self.apparatus.setBob1(self.cmbBasisBob1.currentText(),self.cmbPhaseBob1.currentText(),0,0,0)
            self.apparatus.setBob2(self.cmbBasisBob2.currentText())

            self.getParameters()
            
            self.ttagBuf = ttag.TTBuffer(self.bufNum)   
            
            if self.chkSave.isChecked():
                self.saving = True
                self.saveStartIndex = self.ttagBuf.datapoints
                self.saveCurIndex = self.saveStartIndex
                if self.txtMainDir.text() == '':
                    self.SetMainDir()
                AliceBasis = ['Z','X','D','A']
                self.maindir = self.txtMainDir.text() + '/meas_' + AliceBasis[self.cmbBasisAlice.currentIndex()] + self.cmbBasisBob1.currentText() + self.cmbBasisBob2.currentText() + '_' + self.cmbPhaseBob1.currentText() + '/'
                os.mkdir(self.maindir)
                self.savedSize = 0
                self.saveInterval = float(self.txtSaveInterval.text())
                self.clock.restart()
                self.savetimer.start(self.saveInterval*1000)
                self.lblSize.setText('0 B')

            self.chkSave.setEnabled(False)
            self.txtMainDir.setEnabled(False)
            self.btnMainDir.setEnabled(False)
            self.cmbSave.setEnabled(False)
            self.txtSaveInterval.setEnabled(False)
            
            self.updatetimer.start()
            self.UpdateView()
            
        else:
            self.updatetimer.stop()
            self.inAcq = False    
            self.txtPause.setEnabled(True)
            self.txtBufferNo.setEnabled(True)
            self.btnStart.setStyleSheet('')
            self.btnStart.setText('Start')   

            self.cmbBasisAlice.setEnabled(True)
            self.cmbBasisBob1.setEnabled(True)
            self.cmbBasisBob2.setEnabled(True)
            self.cmbPhaseBob1.setEnabled(True)
#            self.txtEpsHWPBob1.setEnabled(True)
#            self.txtEpsQWPBob1.setEnabled(True)
#            self.txtCompBob1.setEnabled(True)
            
            if self.saving:
                self.savetimer.stop()
                self.SaveData()
                self.saving = False
            
            self.chkSave.setEnabled(True)
            self.txtMainDir.setEnabled(True)
            self.btnMainDir.setEnabled(True)
            self.cmbSave.setEnabled(True)
            self.txtSaveInterval.setEnabled(True)
            
    def AcquiredData(self):
        if self.saving:
            #self.lblAcquired.setText(str(self.ttagBuf.datapoints-self.saveStartIndex))
            self.lblAcquired.setText( str(int(float(self.lblAcquired.text()) + np.sum(self.coincidences[0:2,2:4]))) )
            
    def SaveData(self):
        # save all data
        if self.cmbSave.currentIndex() == 0:
            curtime = self.clock.elapsed()//1000

            filename = 't_'+'{0:05d}'.format(curtime)+'.npz'
            fullname = self.maindir + filename

            lastIndex = self.ttagBuf.datapoints
            print('Save from '+str(self.saveCurIndex)+' to '+str(lastIndex))
            data = self.ttagBuf[self.saveCurIndex:lastIndex]
            np.savez(fullname,tags=data)
            self.saveCurIndex = lastIndex
            
            self.savedSize += os.path.getsize(fullname)
            if not self.savedSize//2**10:
                sizetxt = '{:<4.2f}'.format(self.savedSize)+' B'
            elif not self.savedSize//2**20:
                sizetxt = '{:<4.2f}'.format(self.savedSize/2**10)+' KiB'
            elif not self.savedSize//2**30:
                sizetxt = '{:<4.2f}'.format(self.savedSize/2**20)+' MiB'
            elif not self.savedSize//2**40:
                sizetxt = '{:<4.2f}'.format(self.savedSize/2**30)+' GiB'
            self.lblSize.setText(sizetxt)

    def SetMainDir(self):
        self.txtMainDir.setText( QtGui.QFileDialog.getExistingDirectory(self, "Choose main acquisition folder", '.', QtGui.QFileDialog.ShowDirsOnly) )

    def UpdateView(self):
        QtGui.qApp.processEvents()
        self.getParameters()
        self.getData()
        self.Monitor()
        self.Align()
        self.CoincView()
        self.SingleView()
        self.AcquiredData()
        self.UpdateResults()
        self.DelayFunc()
        if self.autoAcq:
            self.autoUpdate()
        if self.inAcq:
            self.updatetimer.singleShot(self.pause,self.UpdateView)
    
    def getData(self):
        self.singles = self.ttagBuf.singles(self.exptime)
        self.coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
		

    def Monitor(self):
        chs = np.arange(self.NumCh)
        singles = self.singles[:self.NumCh]
        xdict = {0:str(singles[0]),1:str(singles[1]),
            2:str(singles[2]),3:str(singles[3])}
        ax = self.pltMonitor.getAxis('bottom')
        bg = pg.BarGraphItem(x=chs, height=singles, width=0.7, brush='b')
        self.pltMonitor.clear()
        ax.setTicks([xdict.items(), []])
        self.pltMonitor.addItem(bg)

    def Align(self):
        chs=np.arange(3)
        c1 = np.sum(self.singles[0:2])
        c2 = np.sum(self.singles[2:4])
        c12 = np.sum(self.coincidences[0:2,2:4])
        xdict = {0:str(c1),1:str(c2),2:str(c12)}
        C = np.array([c1,c2,c12])
        ax = self.pltAlign.getAxis('bottom')
        bg = pg.BarGraphItem(x=chs, height=C, width=0.7, brush='b')
        self.pltAlign.clear()
        ax.setTicks([xdict.items(),[]])
        self.pltAlign.addItem(bg)

    def CoincView(self):
        chGood = np.array([1,2])
        chErr = np.array([0,3])
        count = self.coincidences[0:2,2:4].flatten()
        pltFig = self.pltCoincVis
        xdict = dict(enumerate(count))
        bgGood = pg.BarGraphItem(x=chGood,height=count[chGood],width=0.7,brush='b')
        bgErr = pg.BarGraphItem(x=chErr,height=count[chErr],width=0.7,brush='r')
        ax = pltFig.getAxis('bottom')
        pltFig.clear()
        ax.setTicks([xdict.items(), []])
        pltFig.addItem(bgGood)
        pltFig.addItem(bgErr)

    def SingleView(self):
        chs = np.arange(self.NumCh)
        count = np.concatenate( (np.sum(self.coincidences[0:2,2:4],axis=1), np.sum(self.coincidences[0:2,2:4],axis=0)) )
        pltFig = self.pltSingleVis
        xdict = dict(enumerate(count))
        bg = pg.BarGraphItem(x=chs,height=count,width=0.7,brush='b')
        ax = pltFig.getAxis('bottom')
        pltFig.clear()
        ax.setTicks([xdict.items(), []])
        pltFig.addItem(bg)

    def UpdateResults(self):
            if np.sum(self.coincidences[0:2,2:4]):
                visRaw = 1 - 2*(self.coincidences[0,2]+self.coincidences[1,3])/np.sum(self.coincidences[0:2,2:4])
                self.lblVis.setText("{:.4f}".format(visRaw))
            else:
                self.lblVis.setText("###")
            C_acc = np.maximum( np.array( [self.singles[0]*self.singles[2:4],self.singles[1]*self.singles[2:4]] ), np.zeros( (2,2) ) )*2*self.coincWindow/self.exptime
            C_noacc = np.maximum( self.coincidences[0:2,2:4] - C_acc, np.zeros( (2,2) ) )
            if np.sum(C_noacc):
                visNet = 1 - 2*(C_noacc[0,0]+C_noacc[1,1])/np.sum(C_noacc)
                self.lblVisNet.setText("{:.4f}".format(visNet))
            else:
                self.lblVisNet.setText("###")





    def DelayFunc(self):
        # data analysed the old way to get delay range plot
        lastTag = np.max(self.ttagBuf.rawtags)
        firstTag = (lastTag - np.int(np.ceil(self.exptime/self.ttagBuf.resolution))).astype(np.uint64)
        rawPos = np.nonzero(np.bitwise_and(self.ttagBuf.rawtags>firstTag,self.ttagBuf.rawtags<lastTag))[0]
        rawTags = self.ttagBuf.rawtags[rawPos]
        rawChan = self.ttagBuf.rawchannels[rawPos]
        rawAll = np.vstack( (rawTags,rawChan) )
#        newAll = np.sort(rawAll,axis=0)
        newTags = rawAll[0]
        newChan = rawAll[1]
        # filter data to plot
        selDelay = self.cmbChannels.currentIndex()
        if selDelay > 3:
            selTags = newTags
            selChan = newChan
        else:
            ch1 = np.array([0,0,1,1,])
            ch2 = np.array([2,3,2,3,])
            selPos = np.nonzero( np.bitwise_or(newChan == ch1[selDelay],newChan == ch2[selDelay]) )[0]
            selTags = newTags[selPos]
            selChan = newChan[selPos]
        # add delays to tags
        selTags = selTags + np.around(self.delay[selChan]/self.ttagBuf.resolution).astype(np.int64)
        # compute delay histogram
        delayEdges = np.arange( -np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32) , np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32), 2 )

        selTags = selTags.astype(np.int64)
        selChan = selChan.astype(np.int8)

        if selDelay > 3:
            chMap = np.array([0,0,1,1])
            selChan = chMap[selChan]

        t12diff = np.diff(selTags)
        chdiff = np.diff(selChan)

        t12diff = t12diff[chdiff!=0]*np.sign(chdiff[chdiff!=0])

        count,bins = np.histogram(t12diff,bins=delayEdges,range=(np.amin(delayEdges),np.amax(delayEdges)))
        binCenter = (bins[1:]+bins[:-1])/2
        delays = binCenter * self.ttagBuf.resolution * 1e9

        bg = pg.BarGraphItem(x=delays,height=count,width=0.1,brush='b')
        self.pltDelay.clear()
        
        # fit results if the fit box is checked
        if self.chkFit.isChecked():
            gaussian = lambda x,A,x0,s: A*np.exp(-(x-x0)**2/(2*s**2))
            p0 = [np.max(count),delays[np.argmax(count)],0.3]
            popt,perr = curve_fit(gaussian,delays,count,p0=p0)
            x = np.linspace(np.amin(delays),np.amax(delays),1000)
            yfit = gaussian(x,*popt)
            self.pltDelay.plot(x,yfit,pen='r')
            self.lblMean.setText("{:.4f}".format(popt[1]))
            self.lblStd.setText("{:.4f}".format(popt[2]))

        self.pltDelay.addItem(bg)

    def autoSetParams(self,ob1,b1,b2,a):
        self.cmbBasisAlice.setCurrentIndex(a)
        self.cmbBasisBob1.setCurrentIndex(b1)
        self.cmbBasisBob2.setCurrentIndex(b2)
        self.cmbPhaseBob1.setCurrentIndex(ob1)

    def autoStart(self):
        if not self.autoAcq:
            self.autoExp = float(self.txtAutoExp.text())
            if self.autoExp <= 0:
                return

            self.autoAcq = True
            self.autoIndex = 0

            self.chkSave.setChecked(True)

            self.lblRemainingTime.setText(str(self.autoExp))
            self.txtAutoExp.setEnabled(False)
            self.btnAutoMeasure.setStyleSheet('background-color: green')

            self.autoSetParams(*self.autoBases[0])
            self.autoIndex += 1
            self.lblMeasNow.setText(str(int(self.autoIndex)))
            self.Start()

        else:
            self.Start() # stop current acquisition
            self.txtAutoExp.setEnabled(True)
            self.btnAutoMeasure.setStyleSheet('')
            self.autoAcq = False

    def autoUpdate(self):
        self.remTime = self.autoExp - self.clock.elapsed()/1000
        if self.remTime > 0:
            self.lblRemainingTime.setText('{:.2f}'.format(self.remTime))
        else:
            self.lblRemainingTime.setText('0.00')
            self.Start() # stop current acquisition
            if self.autoIndex < len(self.autoBases):
                self.autoSetParams(*self.autoBases[self.autoIndex])
                self.autoIndex += 1
                self.lblMeasNow.setText(str(int(self.autoIndex)))
                self.lblRemainingTime.setText('{:.2f}'.format(self.autoExp))
                self.Start()
            else:
                self.btnAutoMeasure.setStyleSheet('')
                self.txtAutoExp.setEnabled(True)
                self.autoAcq = False


if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Monitor()
    window.show()
    sys.exit(app.exec_())
