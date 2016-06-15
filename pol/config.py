"""
Created on Tue Jun 14 18:23:10 2016

@author: sagnac
"""

from __future__ import absolute_import

from PyQt4 import QtCore,QtGui,uic
import yaml

import apparatus

qtCreatorFile = 'config.ui'

Ui_Widget, QtBaseClass = uic.loadUiType(qtCreatorFile)

class ConfigUI(QtGui.QWidget,Ui_Widget):
    def __init__(self,c,app):

        QtGui.QWidget.__init__(self)
        Ui_Widget.__init__(self)

        # an istance of the class Config
        self._config = c
        self._app = app

        self.setupUi(self)

        # capture all changes in the UI
        self.txtSNAlice.textChanged.connect(self.uiChanged)
        self.txtSNHWPBob1.textChanged.connect(self.uiChanged)
        self.txtSNBob2.textChanged.connect(self.uiChanged)
        self.txtZeroAlice.textChanged.connect(self.uiChanged)
        self.txtZeroHWPBob1.textChanged.connect(self.uiChanged)
        self.txtZeroBob2.textChanged.connect(self.uiChanged)
        self.cmbDirAlice.currentIndexChanged.connect(self.uiChanged)
        self.cmbDirHWPBob1.currentIndexChanged.connect(self.uiChanged)
        self.cmbDirBob2.currentIndexChanged.connect(self.uiChanged)
        self.chkActiveAlice.stateChanged.connect(self.uiChanged)
        self.chkActiveHWPBob1.stateChanged.connect(self.uiChanged)
        self.chkActiveBob2.stateChanged.connect(self.uiChanged)
        self.chkActiveGlass.stateChanged.connect(self.uiChanged)
        self.txtSNGlass.textChanged.connect(self.uiChanged)
        self.txtPosMinGlass.textChanged.connect(self.uiChanged)
        self.txtPosMaxGlass.textChanged.connect(self.uiChanged)
        self.chkActiveWeak.stateChanged.connect(self.uiChanged)
        self.txtSNWeak.textChanged.connect(self.uiChanged)

        # load and save buttons
        self.btnLoadConfig.clicked.connect(self.loadFileToUI)
        self.btnSaveConfig.clicked.connect(self.saveUItoFile)


    def closeEvent(self,event):
        newConfig = self.getConfigFromUI()
        self._config.setConfig(newConfig)

    def uiChanged(self):
        self.updateUI()

    def loadFileToUI(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'Load \
        configuration...','.','*.yml *.yaml')
        
        try:
            self._config.loadConfigFromFile(fname)
            self.setUIFromConfig(self._config.getConfig())
            return 0
        except:
            return -1


    def saveUItoFile(self):
        fname = QtGui.QFileDialog.getSaveFileName(self,'Load \
        configuration...','.','*.yml *.yaml')
        
        try:
            self._config.setConfig(self.getConfigFromUI())
            self._config.saveConfigToFile(fname)
            return 0
        except:
            return -1



    def updateUI(self):
        if not self._app.connected:
            # Update Alice
            if not self.chkActiveAlice.isChecked():
                self.cmbDirAlice.setEnabled(False)
                self.txtSNAlice.setEnabled(False)
                self.txtZeroAlice.setEnabled(False)
            else:
                self.cmbDirAlice.setEnabled(True)
                self.txtSNAlice.setEnabled(True)
                self.txtZeroAlice.setEnabled(True)
            self.lblConnAlice.setStyleSheet(' {background-color: green}')

            if not self.chkActiveBob2.isChecked():
                self.cmbDirBob2.setEnabled(False)
                self.txtSNBob2.setEnabled(False)
                self.txtZeroBob2.setEnabled(False)
            else:
                self.cmbDirBob2.setEnabled(True)
                self.txtSNBob2.setEnabled(True)
                self.txtZeroBob2.setEnabled(True)

            if not self.chkActiveHWPBob1.isChecked():
                self.cmbDirHWPBob1.setEnabled(False)
                self.txtSNHWPBob1.setEnabled(False)
                self.txtZeroHWPBob1.setEnabled(False)
            else:
                self.cmbDirHWPBob1.setEnabled(True)
                self.txtSNHWPBob1.setEnabled(True)
                self.txtZeroHWPBob1.setEnabled(True)

            if not self.chkActiveGlass.isChecked():
                self.txtSNGlass.setEnabled(False)
                self.txtPosMinGlass.setEnabled(False)
                self.txtPosMaxGlass.setEnabled(False)
            else:
                self.txtSNGlass.setEnabled(True)
                self.txtPosMinGlass.setEnabled(True)
                self.txtPosMaxGlass.setEnabled(True)

            if not self.chkActiveWeak.isChecked():
                self.txtSNWeak.setEnabled(False)
            else:
                self.txtSNWeak.setEnabled(True)
    
    def connect(self):
        pass

    def getConfigFromUI(self):
        '''Get configuration from GUI and put it into object c.'''
        config = {}

        dirRot = ['CW','CCW']

        if self.chkActiveAlice.isChecked():
            config['Alice'] = {}
            config['Alice']['basis'] = {
                    'serial_number': self.txtSNAlice.text(),
                    'zero': float(self.txtZeroAlice.text()),
                    'dirRot': dirRot[self.cmbDirAlice.currentIndex()],
                    'home': True }
        if self.chkActiveBob2.isChecked():
            config['Bob2'] = {}
            config['Bob2']['basis'] = {
                    'serial_number': self.txtSNBob2.text(),
                    'zero': float(self.txtZeroBob2.text()),
                    'dirRot': dirRot[self.cmbDirBob2.currentIndex()],
                    'home': True }
        if self.chkActiveHWPBob1.isChecked():
            config['Bob1'] = {}
            config['Bob1']['basis'] = {
                    'serial_number': self.txtSNHWPBob1.text(),
                    'zero': float(self.txtZeroHWPBob1.text()),
                    'dirRot': dirRot[self.cmbDirHWPBob1.currentIndex()],
                    'home': True }
        if self.chkActiveGlass.isChecked():
            if not 'Bob1' in config:
                config['Bob1'] = {}
            config['Bob1']['meas'] = {
                    'serial_number' : self.txtSNGlass.text(),
                    'posMin': float(self.txtPosMinGlass.text()),
                    'posMax': float(self.txtPosMaxGlass.text()),
                    'home': True }
        if self.chkActiveWeak.isChecked():
            config['weak'] = {
                    'serial_number' : self.txtSNWeak.text(),
                    'home': True }

        return config

    def setUIFromConfig(self,config):
        try:
            if 'Alice' in config:
                if 'basis' in config['Alice']:
                    self.chkActiveAlice.setChecked(True)
#                    self.cmbDirAlice.setEnabled(True)
#                    self.txtSNAlice.setEnabled(True)
#                    self.txtZeroAlice.setEnabled(True)
                    c = config['Alice']['basis']
                    self.txtSNAlice.setText(c['serial_number'])
                    self.txtZeroAlice.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirAlice.setCurrentIndex(1)
                    else:
                        self.cmbDirAlice.setCurrentIndex(0)
                else:
                    self.chkActiveAlice.setChecked(False)
#                    self.cmbDirAlice.setEnabled(False)
#                    self.txtSNAlice.setEnabled(False)
#                    self.txtZeroAlice.setEnabled(False)
            if 'Bob2' in config:
                if 'basis' in config['Bob2']:
                    self.chkActiveBob2.setChecked(True)
#                    self.cmbDirBob2.setEnabled(True)
#                    self.txtSNBob2.setEnabled(True)
#                    self.txtZeroBob2.setEnabled(True)
                    c = config['Bob2']['basis']
                    self.txtSNBob2.setText(c['serial_number'])
                    self.txtZeroBob2.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirBob2.setCurrentIndex(1)
                    else:
                        self.cmbDirBob2.setCurrentIndex(0)
                else:
                    self.chkActiveBob2.setChecked(False)
#                    self.cmbDirBob2.setEnabled(False)
#                    self.txtSNBob2.setEnabled(False)
#                    self.txtZeroBob2.setEnabled(False)
            if 'Bob1' in config:
                if 'basis' in config['Bob1']:
                    self.chkActiveHWPBob1.setChecked(True)
#                    self.cmbDirHWPBob1.setEnabled(True)
#                    self.txtSNHWPBob1.setEnabled(True)
#                    self.txtZeroHWPBob1.setEnabled(True)
                    c = config['Bob1']['basis']
                    self.txtSNHWPBob1.setText(c['serial_number'])
                    self.txtZeroHWPBob1.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirHWPBob1.setCurrentIndex(1)
                    else:
                        self.cmbDirHWPBob1.setCurrentIndex(0)
                else:
                    self.chkActiveHWPBob1.setChecked(False)
#                    self.cmbDirHWPBob1.setEnabled(False)
#                    self.txtSNHWPBob1.setEnabled(False)
#                    self.txtZeroHWPBob1.setEnabled(False)
                if 'meas' in config['Bob1']:
                    self.chkActiveGlass.setChecked(True)
#                    self.txtSNGlass.setEnabled(True)
#                    self.txtPosMinGlass.setEnabled(True)
#                    self.txtPosMaxGlass.setEnabled(True)
                    c = config['Bob1']['meas']
                    self.txtSNGlass.setText(c['serial_number'])
                    self.txtPosMinGlass.setText(str(c['posMin']))
                    self.txtPosMaxGlass.setText(str(c['posMax']))
                else:
                    self.chkActiveGlass.setChecked(False)
#                    self.txtSNGlass.setEnabled(False)
#                    self.txtPosMinGlass.setEnabled(False)
#                    self.txtPosMaxGlass.setEnabled(False)
            if 'weak' in config:
                self.chkActiveWeak.setChecked(True)
#                self.txtSNWeak.setEnabled(True)
                c = config['weak']
                self.txtSNWeak.setText(c['serial_number'])
            else:
                self.chkActiveWeak.setChecked(False)
#                self.txtSNWeak.setEnabled(False)
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            return -1

        return 0

class Config():
    def __init__(self):
        self._config = {}

    def getConfig(self):
        return self._config

    def setConfig(self,config):
        self._config = config

    def loadConfigFromFile(self,fname):
        print('Loading configuration from '+fname)
        f = open(fname,'r')
        conffile = f.read()
        f.close()
        config = yaml.load(conffile)
        self.setConfig(config)

    def saveConfigToFile(self,fname):
        print('Saving configuration to '+fname)
        f = open(fname,'w')
        f.write(yaml.dump(self._config,default_flow_style=False))
        f.close()

    def printConfig(self):
        print(yaml.dump(self._config))
