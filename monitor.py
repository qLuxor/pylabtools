# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:43:23 2016

@author: sagnac
"""

import sys
from PyQt4 import QtCore,QtGui,uic      # importing Qt libraries

import pyqtgraph as pg                  # importing graph libraries
import numpy as np                      # importing mathematical libraries
from scipy.optimize import curve_fit    # importing fit method

#import os
#if 'LD_LIBRARY_PATH' in os.environ.keys():
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/:'+os.environ['LD_LIBRARY_PATH']
#else:
#    os.environ['LD_LIBRARY_PATH'] = '/home/sagnac/Quantum/ttag/python/'
        

sys.path.append('/home/sagnac/Quantum/ttag/python/')
import ttag                             # importing libraries to read Qtools output

qtCreatorFile = 'monitor.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile) #import the monitor.ui interface

class Monitor(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        pg.setConfigOption('background', 'w')       # sets graph background to white                                                 
        pg.setConfigOption('foreground', 'k')       # sets axis color to black 

        QtGui.QMainWindow.__init__(self)            # These three commands
        Ui_MainWindow.__init__(self)                # are needed to
        self.setupUi(self)                          # to setup the ui

        # La logica di programmare una interfaccia mi sembra la seguente:
        # per prima cosa inizializzo l'interfaccia grafica
        # dopo aver inizializzato l'interfaccia 
        # (che modifico e organizzo tramite Qt Creator)
        # associo ad ogni azione che eseguo sulla interfaccia 
        # un metodo della classe che definisco a seguito

        self.btnStart.clicked.connect(self.Start)
        self.tabWidget.currentChanged.connect(self.SetupView)
        
        self.timer = QtCore.QTimer(self)                # qui richiamo l'oggetto  timer delle libreria QT 
        self.timer.timeout.connect(self.UpdateView)     # e gli dico che quando il timer va in timeout devo fare l'update dells visuale 
        
        self.curTab = self.tabWidget.currentIndex()
        self.SetupView(self.curTab)

        # le istruzioni seguenti servono a disabilitare il mouse su tutti
        # i possobili plot dell'interfaccia
        self.pltMonitor.setMouseEnabled(x=False,y=False)  
        self.pltAlign.setMouseEnabled(x=False,y=False)  
        self.pltDelay.setMouseEnabled(x=False,y=False)  
        self.pltSingle.setMouseEnabled(x=False,y=False)  
        self.pltCoinc.setMouseEnabled(x=False,y=False)  
        self.pltSingleVis.setMouseEnabled(x=False,y=False)  
        self.pltCoincVis.setMouseEnabled(x=False,y=False)  

        self.inAcq = False      # flag di acquisizione in corso o meno

        self.getParameters()
        
    def SetupView(self,index):
        self.curTab = index
        # Abilito o disabilito i campi delay nel caso
        # sia nella modalita' three state o visibility 
        # e cambio l'attributo NumCh -> numero di canali attivi
        if self.curTab == 0:
            # three state view
            self.txtDelay5.setEnabled(True)
            self.txtDelay6.setEnabled(True)
            # parameters
            self.NumCh = 6
        elif self.curTab == 1:
            # visibility view
            self.txtDelay5.setEnabled(False)
            self.txtDelay6.setEnabled(False)
            # parameters
            self.NumCh = 4
        
    def getParameters(self):
        self.bufNum = int(self.txtBufferNo.text())      # registro il TTBufferNumber
        # registro i delay in un array (il numero di delay cambia a seconda della vista scelta)
        # e converto in secondi
        self.delay = np.array([float(self.txtDelay1.text()), float(self.txtDelay2.text()),
                               float(self.txtDelay3.text()),float(self.txtDelay4.text())])
        if self.curTab==0:
            self.delay = np.concatenate( (self.delay,np.array([float(self.txtDelay5.text()),float(self.txtDelay6.text())])) ) 
        
        self.delay = self.delay*1e-9
        
        self.exptime = float(self.txtExp.text())/1000           # registro il exposure time e converto in secondi
        self.pause = float(self.txtPause.text())                # registro il tempo di pausa
        self.coincWindow = float(self.txtWindow.text())*1e-9    # registro la coincidence window e converto in s
        
        self.delayRange = float(self.txtRange.text())*1e-9      # registro il rangr del plot che voglio mostrare
        
    def Start(self):
        if not self.inAcq:
            self.inAcq = True                   # cambio flag sdi acquisizione
            self.txtPause.setEnabled(False)     # disabilito alcuni controlli
            self.txtBufferNo.setEnabled(False)
            self.btnStart.setStyleSheet('background-color: red')    # cambio sfondo e testo bottone di acquisizione
            self.btnStart.setText('Stop')

            self.getParameters()                # registro i parametri
            self.timer.start(self.pause)        # faccio partire il timer, quindi acquisisce (vedi riga sotto) per il tempo self.pause 

            self.ttagBuf = ttag.TTBuffer(self.bufNum)       # creo un oggetto ttagBuf con opzione bufNum, che e' TTBuffer preso dalla libreria ttag
            
        else:
            self.timer.stop()
            self.inAcq = False    
            self.txtPause.setEnabled(True)      # riabilito le caselle di alcune opzioni
            self.txtBufferNo.setEnabled(True)
            self.btnStart.setStyleSheet('')     # cambio sfondo e testo bottone di acquisizione
            self.btnStart.setText('Start')   
    
    def UpdateView(self):
        QtGui.qApp.processEvents()
        self.getParameters()
        self.getData()
        self.Monitor()
        self.Align()
        self.CoincView()
        self.SingleView()
        self.UpdateResults()
        self.DelayFunc()
    
    def getData(self):      # metodo che  legge i dati dal buffer
        # creo l'oggetto singles (definito nella libreria ttag) che carica tutti gli eventi registrati entro un certo exp time
        self.singles = self.ttagBuf.singles(self.exptime)
        # creo l'oggetto coincidences (definito nella libreria ttag) 
        # che carica tutte le coincidenze, avvenute tra i canali shiftati di un certo delay time,
        # accadute entro una cera coincidence window
        self.coincidences = self.ttagBuf.coincidences(self.exptime,self.coincWindow,-self.delay)
        # TODO come sono fatti esattamente questi oggetti? chiedi a Matteo
        # se non sbaglio:
        #   singles e' un array di 8 canali in cui si mettono le coincidenze per ciascun canale
        #   coincidences e' una matrice 8x8 simmetrica con le coincidenze tra i cari canali

    def Monitor(self):      # metodo che stampa i singoli a monitor
        chs = np.arange(self.NumCh)             # creo un array con tanti numeri quanti il numero di canali
        singles = self.singles[:self.NumCh]     # copio in singles (che e' un array) solo i registrati nei canali attivi
        if self.curTab == 0:    # creo un dizionario di oggetti contenenti il numero sdi singoli registrati per ciascun canale
            xdict = {0:str(singles[0]),1:str(singles[1]),
                     2:str(singles[2]),3:str(singles[3]),
                     4:str(singles[4]),5:str(singles[5])}
        elif self.curTab == 1:
            xdict = {0:str(singles[0]),1:str(singles[1]),
                     2:str(singles[2]),3:str(singles[3])}
        # stampo singoli a monitor
        ax = self.pltMonitor.getAxis('bottom')
        bg = pg.BarGraphItem(x=chs, height=singles, width=0.7, brush='b')
        self.pltMonitor.clear()
        ax.setTicks([xdict.items(), []])
        self.pltMonitor.addItem(bg)

    def Align(self):        # metodo che mostra quanti singoli arrivano e quanti di questi dono delle coincidenze
        chs=np.arange(3)
        if self.curTab == 0:
            c1 = np.sum(self.singles[0:3])              # sommo singoli che sono arrivati nei primi tre canali
            c2 = np.sum(self.singles[3:6])              # sommo singoli che sono arrivati negli ultimi tre canali
            c12 = np.sum(self.coincidences[0:3,3:6])    # somma di tutte le possibili coincidenze avvenute tra i primi tre e gli ultimi tre canali
        elif self.curTab == 1:
            c1 = np.sum(self.singles[0:2])
            c2 = np.sum(self.singles[2:4])
            c12 = np.sum(self.coincidences[0:2,2:4])
        xdict = {0:str(c1),1:str(c2),2:str(c12)}
        # stampo somma dei tre canali e somma di tutte le coincidenze a monitor
        C = np.array([c1,c2,c12])
        ax = self.pltAlign.getAxis('bottom')
        bg = pg.BarGraphItem(x=chs, height=C, width=0.7, brush='b')
        self.pltAlign.clear()
        ax.setTicks([xdict.items(),[]])
        self.pltAlign.addItem(bg)

    def CoincView(self):
        if self.curTab == 0:
            chGood = np.array([1,2,4,5,7,8])
            chErr = np.array([0,3,6])
            count = self.coincidences[0:3,3:6].flatten()
            pltFig = self.pltCoinc
        elif self.curTab == 1:
            chGood = np.array([0,3])
            chErr = np.array([1,2])
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
        if self.curTab == 0:
            count = np.concatenate( (np.sum(self.coincidences[0:3,3:6],axis=1), np.sum(self.coincidences[0:3,3:6],axis=0)) )
            pltFig = self.pltSingle
        elif self.curTab == 1:
            count = np.concatenate( (np.sum(self.coincidences[0:2,2:4],axis=1), np.sum(self.coincidences[0:2,2:4],axis=0)) )
            pltFig = self.pltSingleVis
        xdict = dict(enumerate(count))
        bg = pg.BarGraphItem(x=chs,height=count,width=0.7,brush='b')
        ax = pltFig.getAxis('bottom')
        pltFig.clear()
        ax.setTicks([xdict.items(), []])
        pltFig.addItem(bg)

    def UpdateResults(self):
        if self.curTab == 0:
            rate = np.sum(self.coincidences[0:3,3:6])/self.exptime
            # print rate and QBER
            self.lblRate.setText("{:.2f}".format(rate).rstrip('00').rstrip('.'))
            if rate != 0:
                qber = np.sum(np.diag(self.coincidences[0:3,3:6]))/(rate*self.exptime)
                self.lblQBER.setText("{:.4f}".format(qber))
            else:
                self.lblQBER.setText('###')
        elif self.curTab == 1:
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
        # self.ttagBuf.rawtags -> is an array with all the arrival times
        lastTag = np.max(self.ttagBuf.rawtags)
        # qui di seguito trovo il limite inferiore per i tag di interesse, 
        # prendendo la casella di tempo di interesse (exptime), dividendola per la risoluzione,
        # convertendola poi in uint64. In questo modo first tag e' proprio una tag presente nell'array
        firstTag = (lastTag - np.int(np.ceil(self.exptime/self.ttagBuf.resolution))).astype(np.uint64)
        # quello qui di seguito e' un modo molto furbo per ottenere l'array
        # delle posizioni (negli array rawtags e quindi rawchannels) 
        # degli eventi nella finestra temporale del ttag di interesse
        rawPos = np.nonzero(np.bitwise_and(self.ttagBuf.rawtags>firstTag,self.ttagBuf.rawtags<lastTag))[0]
        # qui costruisco un array con i soli tags di interesse ordinati
        rawTags = self.ttagBuf.rawtags[rawPos]
        # qui costruisco un array con i soli tempi di interesse ordinati (nello stesso modo dei tags)
        rawChan = self.ttagBuf.rawchannels[rawPos]
        # vstack -> stack arrays in sequence vertically
        rawAll = np.vstack( (rawTags,rawChan) )
        newTags = rawAll[0]
        newChan = rawAll[1]
        # filter data to plot based on the selected channel combination
        selDelay = self.cmbChannels.currentIndex()
        if selDelay > 8:
            selTags = newTags
            selChan = newChan
        else:
            if self.curTab == 0:
                ch1 = np.array([0,0,0,1,1,1,2,2,2])
                ch2 = np.array([3,4,5,3,4,5,3,4,5])
            elif self.curTab == 1:
                ch1 = np.array([0,0,0,1,1,1,-1,-1,-1])
                ch2 = np.array([2,3,-1,2,3,-1,2,3,-1])
            # modo furbo per otterere l'array delle posizioni in cui ho solo i tag dei canali eletti 
            selPos = np.nonzero( np.bitwise_or(newChan == ch1[selDelay],newChan == ch2[selDelay]) )[0]
            selTags = newTags[selPos]
            selChan = newChan[selPos]
        # add delays to tags
        # il metodo around arrotonda col metodo "piu' vicino numero pari"
        selTags = selTags + np.around(self.delay[selChan]/self.ttagBuf.resolution).astype(np.int64)
        # compute delay histogram
        #delayEdges = np.arange( -np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32) , np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32), 2 )
        # TODO: linea aggiunta
        delayEdges = np.arange( -np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32) , np.around(self.delayRange/self.ttagBuf.resolution).astype(np.int32), 4 )

        selTags = selTags.astype(np.int64)
        selChan = selChan.astype(np.int8)

        if selDelay > 8:
            if self.curTab == 0:
                chMap = np.array([0,0,0,1,1,1])
            elif self.curTab == 1:
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
		

            
            
if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Monitor()
    window.show()
    sys.exit(app.exec_())
