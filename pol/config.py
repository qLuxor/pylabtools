"""
Created on Tue Jun 14 18:23:10 2016

@author: sagnac
"""

from PyQt4 import QtCore,QtGui,uic
import yaml

qtCreatorFile = 'config.ui'

Ui_Widget, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Config(QtGui.QWidget,Ui_Widget):
    def __init__(self):

        QtGui.QWidget.__init__(self)
        Ui_Widget.__init__(self)

        self.setupUi(self)
        self.btnLoadConfig.clicked.connect(self.loadConfig)
        self.btnSaveConfig.clicked.connect(self.saveConfig)
        self.btnConnect.clicked.connect(self.connect)

        self._config = {}
        self.getConfig()
        self.setConfig(self._config)

        self.connected = False


    def connect(self):
        pass

    def getConfig(self):
        '''Get configuration from current form and return it.'''
        oldconfig = self._config
        self._config = {}

        dirRot = ['CW','CCW']

        if self.chkActiveAlice.isChecked():
            self._config['Alice'] = {}
            self._config['Alice']['basis'] = {
                    'serial_number': self.txtSNAlice.text(),
                    'zero': self.txtZeroAlice.text(),
                    'dirRot': dirRot[self.cmbDirAlice.currentIndex()],
                    'home': True }
        if self.chkActiveBob2.isChecked():
            self._config['Bob2'] = {}
            self._config['Bob2']['basis'] = {
                    'serial_number': self.txtSNBob2.text(),
                    'zero': self.txtZeroBob2.text(),
                    'dirRot': dirRot[self.cmbDirBob2.currentIndex()],
                    'home': True }
        if self.chkActiveHWPBob1.isChecked():
            self._config['Bob1'] = {}
            self._config['Bob1']['basis'] = {
                    'serial_number': self.txtSNHWPBob1.text(),
                    'zero': self.txtZeroHWPBob1.text(),
                    'dirRot': dirRot[self.cmbDirHWPBob1.currentIndex()],
                    'home': True }
        if self.chkActiveGlass.isChecked():
            if not 'Bob1' in self._config:
                self._config['Bob1'] = {}
            self._config['Bob1']['meas'] = {
                    'serial_number' : self.txtSNGlass.text(),
                    'posMin': self.txtPosMinGlass.text(),
                    'posMax': self.txtPosMaxGlass.text(),
                    'home': True }
        if self.chkActiveWeak.isChecked():
            self._config['weak'] = {
                    'serial_number' : self.txtSNWeak.text(),
                    'home': True }

        return self._config

    def setConfig(self,config):
        oldconfig = self._config

        try:
            self._config = config

            if 'Alice' in config:
                if 'basis' in config['Alice']:
                    self.chkActiveAlice.setChecked(True)
                    c = config['Alice']['basis']
                    self.txtSNAlice.setText(c['serial_number'])
                    self.txtZeroAlice.setText(c['zero'])
                    if c['dirRot'] == 'CCW':
                        self.cmbDirAlice.setCurrentIndex(1)
                    else:
                        self.cmbDirAlice.setCurrentIndex(0)
                else:
                    self.chkActiveAlice.setChecked(False)
            if 'Bob2' in config:
                if 'basis' in config['Bob2']:
                    self.chkActiveBob2.setChecked(True)
                    c = config['Bob2']['basis']
                    self.txtSNBob2.setText(c['serial_number'])
                    self.txtZeroBob2.setText(c['zero'])
                    if c['dirRot'] == 'CCW':
                        self.cmbDirBob2.setCurrentIndex(1)
                    else:
                        self.cmbDirBob2.setCurrentIndex(0)
                else:
                    self.chkActiveBob2.setChecked(False)
            if 'Bob1' in config:
                if 'basis' in config['Bob1']:
                    self.chkActiveHWPBob1.setChecked(True)
                    c = config['Bob1']['basis']
                    self.txtSNHWPBob1.setText(c['serial_number'])
                    self.txtZeroHWPBob1.setText(c['zero'])
                    if c['dirRot'] == 'CCW':
                        self.cmbDirHWPBob1.setCurrentIndex(1)
                    else:
                        self.cmbDirHWPBob1.setCurrentIndex(0)
                else:
                    self.chkActiveHWPBob1.setChecked(False)
                if 'meas' in config['Bob1']:
                    self.chkActiveGlass.setChecked(True)
                    c = config['Bob1']['meas']
                    self.txtSNGlass.setText(c['serial_number'])
                    self.txtPosMinGlass.setText(c['posMin'])
                    self.txtPosMaxGlass.setText(c['posMax'])
                else:
                    self.chkActiveGlass.setChecked(False)
            if 'weak' in config:
                self.chkActiveWeak.setChecked(True)
                c = config['weak']
                self.txtSNWeak.setText(c['serial_number'])
            else:
                self.chkActiveWeak.setChecked(False)
        except:
            self.setConfig(oldconfig)
            self._config = oldconfig
            return


    def loadConfig(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,
                'Open configuration file...', '.', filter='*.yaml *.yml')
        if fname == '':
            return

        try:
            config = yaml.load(fname)
            self.setConfig(config)
        except:
            return

    def saveConfig(self):
        fname = QtGui.QFileDialog.getSaveFileName(self,
            'Save configuration file...', '.',filter='*.yaml *.yml')
        if fname == '':
            return

        try:
            f = fopen(fname,'w')
            f.write(yaml.dump(self._config,default_flow_style=False))
            f.close()
        except:
            return
