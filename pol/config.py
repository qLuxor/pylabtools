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
    '''This class manages the UI monitoring the experimental apparatus. The
    apparatus is configured using a YAML file with the following structure:

        Alice:
            basis:
                serial_number: 'xxxxxxxx'
                zero: xxx
                dirRot: 'CW'/'CCW'
                home: True
        Bob2:
            basis:
            ...
        Bob1:
            basis:
            ...
            meas:
                serial_number: 'xxxxxxxx'
                zero: xxx
                posMin: xxx
                posMax: xxx
                home: True
            weak1:
                serial_number: 'xxxxxxxx'
                zero: xxx
                home: True
                func: 'aaa'
            weak2:
                serial_number: 'xxxxxxxx'
                zero: xxx
                home: True
                func: 'aaa'

        The configuration is taken either from the UI or from an external file,
        and can be saved into a YAML file.
        '''


    def __init__(self,c,app):
        '''Constructor of the ConfigUI class.

            Args:
                c: instance of the Config class, containing the configuration of
                   the exerimental apparatus.
                app: instance of the Apparatus class (from the apparatus file),
                     containing information about the state of the experimental
                     apparatus connected.
        '''
            
        QtGui.QWidget.__init__(self)
        Ui_Widget.__init__(self)

        # an istance of the class Config
        self._config = c
        self._app = app

        self.setupUi(self)

        # capture all changes in the UI
#        self.txtSNAlice.textChanged.connect(self.uiChanged)
#        self.txtSNHWPBob1.textChanged.connect(self.uiChanged)
#        self.txtSNBob2.textChanged.connect(self.uiChanged)
#        self.txtZeroAlice.textChanged.connect(self.uiChanged)
#        self.txtZeroHWPBob1.textChanged.connect(self.uiChanged)
#        self.txtZeroBob2.textChanged.connect(self.uiChanged)
#        self.cmbDirAlice.currentIndexChanged.connect(self.uiChanged)
#        self.cmbDirHWPBob1.currentIndexChanged.connect(self.uiChanged)
#        self.cmbDirBob2.currentIndexChanged.connect(self.uiChanged)
        self.chkActiveAlice.stateChanged.connect(self.updateUI)
        self.chkActiveHWPBob1.stateChanged.connect(self.updateUI)
        self.chkActiveBob2.stateChanged.connect(self.updateUI)
        self.chkActiveGlass.stateChanged.connect(self.updateUI)
#        self.txtSNGlass.textChanged.connect(self.uiChanged)
#        self.txtPosMinGlass.textChanged.connect(self.uiChanged)
#        self.txtPosMaxGlass.textChanged.connect(self.uiChanged)
        self.chkActiveWeak1.stateChanged.connect(self.updateUI)
        self.chkActiveWeak2.stateChanged.connect(self.updateUI)
#        self.txtSNWeak.textChanged.connect(self.uiChanged)

        # load and save buttons
        self.btnLoadConfig.clicked.connect(self.loadFileToUI)
        self.btnSaveConfig.clicked.connect(self.saveUItoFile)

        # timer connected to the updateUI function when the apparatus is
        # connected
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateUI)


    def closeEvent(self,event):
        '''This function is called when the signal of window closure is issued.
        It puts the configuration in the UI into the Config object where the
        total configuration of the experimental apparatus is stored.'''
        newConfig = self.getConfigFromUI()
        self._config.setConfig(newConfig)

#    def uiChanged(self):
#        self.updateUI()

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
        '''Save the state of the UI into the Config object and call its
        saveConfigToFile method.'''
        fname = QtGui.QFileDialog.getSaveFileName(self,'Load \
        configuration...','.','*.yml *.yaml')
        
        try:
            self._config.setConfig(self.getConfigFromUI())
            self._config.saveConfigToFile(fname)
            return 0
        except:
            return -1

    def connect(self):
        '''This function shoul be called when the apparatus is connected.'''
        # Disable Alice
        self.chkActiveAlice.setEnabled(False)
        self.cmbDirAlice.setEnabled(False)
        self.txtSNAlice.setEnabled(False)
        self.txtZeroAlice.setEnabled(False)
        
        # Disable Bob1
        self.chkActiveHWPBob1.setEnabled(False)
        self.cmbDirHWPBob1.setEnabled(False)
        self.txtSNHWPBob1.setEnabled(False)
        self.txtZeroHWPBob1.setEnabled(False)
        self.chkActiveGlass.setEnabled(False)
        self.txtSNGlass.setEnabled(False)
        self.txtPosMinGlass.setEnabled(False)
        self.txtPosMaxGlass.setEnabled(False)

        # Disable Bob2
        self.chkActiveBob2.setEnabled(False)
        self.cmbDirBob2.setEnabled(False)
        self.txtSNBob2.setEnabled(False)
        self.txtZeroBob2.setEnabled(False)

        # Disable Weak
        self.chkActiveWeak.setEnabled(False)

        # Start timer
        self.timer.start(100)


    def disconnect(self):
        self.timer.stop()

        # enable WP selection
        self.chkActiveAlice.setEnabled(True)
        self.chkActiveBob2.setEnabled(True)
        self.chkActiveHWPBob1.setEnabled(True)
        self.chkActiveGlass.setEnabled(True)
        self.chkActiveWeak.setEnabled(True)

        # erase control background
        self.lblConnAlice.setStyleSheet('')
        self.lblConnBob2.setStyleSheet('')
        self.lblConnHWPBob1.setStyleSheet('')
        self.lblConnGlass.setStyleSheet('')
        self.lblConnWeak.setStyleSheet('')

        self.lblHomedAlice.setStyleSheet('')
        self.lblHomedBob2.setStyleSheet('')
        self.lblHomedHWPBob1.setStyleSheet('')
        self.lblHomedGlass.setStyleSheet('')
        self.lblHomedWeak.setStyleSheet('')

        self.updateUI()


    def updateUI(self):
        '''Update the UI.'''
        if not self._app.connected:
            #self.chkActiveAlice.setEnabled(True)
            if not self.chkActiveAlice.isChecked():
                self.cmbDirAlice.setEnabled(False)
                self.txtSNAlice.setEnabled(False)
                self.txtZeroAlice.setEnabled(False)
            else:
                self.cmbDirAlice.setEnabled(True)
                self.txtSNAlice.setEnabled(True)
                self.txtZeroAlice.setEnabled(True)

            #self.chkActiveBob2.setEnabled(True)
            if not self.chkActiveBob2.isChecked():
                self.cmbDirBob2.setEnabled(False)
                self.txtSNBob2.setEnabled(False)
                self.txtZeroBob2.setEnabled(False)
            else:
                self.cmbDirBob2.setEnabled(True)
                self.txtSNBob2.setEnabled(True)
                self.txtZeroBob2.setEnabled(True)

            #self.chkActiveHWPBob1.setEnabled(True)
            if not self.chkActiveHWPBob1.isChecked():
                self.cmbDirHWPBob1.setEnabled(False)
                self.txtSNHWPBob1.setEnabled(False)
                self.txtZeroHWPBob1.setEnabled(False)
            else:
                self.cmbDirHWPBob1.setEnabled(True)
                self.txtSNHWPBob1.setEnabled(True)
                self.txtZeroHWPBob1.setEnabled(True)

            #self.chkActiveGlass.setEnabled(True)
            if not self.chkActiveGlass.isChecked():
                self.txtSNGlass.setEnabled(False)
                self.txtPosMinGlass.setEnabled(False)
                self.txtPosMaxGlass.setEnabled(False)
                self.txtZeroGlass.setEnabled(False)
            else:
                self.txtSNGlass.setEnabled(True)
                self.txtPosMinGlass.setEnabled(True)
                self.txtPosMaxGlass.setEnabled(True)
                self.txtZeroGlass.setEnabled(True)

            #self.chkActiveWeak1.setEnabled(True)
            if not self.chkActiveWeak1.isChecked():
                self.cmbFuncWeak1.setEnabled(False)
                self.txtSNWeak1.setEnabled(False)
                self.txtZeroWeak1.setEnabled(False)
            else:
                self.cmbFuncWeak1.setEnabled(True)
                self.txtSNWeak1.setEnabled(True)
                self.txtZeroWeak1.setEnabled(True)
            
            #self.chkActiveWeak2.setEnabled(True)
            if not self.chkActiveWeak2.isChecked():
                self.cmbFuncWeak2.setEnabled(False)
                self.txtSNWeak2.setEnabled(False)
                self.txtZeroWeak2.setEnabled(False)
            else:
                self.cmbFuncWeak2.setEnabled(True)
                self.txtSNWeak2.setEnabled(True)
                self.txtZeroWeak2.setEnabled(True)

        else:
            a = self._app
            # Update state Alice
            if a.alice != None:
                if a.alice.hwp != None:
                    self.lblConnAlice.setStyleSheet('background-color: green')
                    self.lblAngleAlice.setText("{:.4f}".format(a.alice.hwp.getPosition()))
                    if a.alice.hwp.homed:
                        self.lblHomedAlice.setStyleSheet('background-color: green')
            # Update state Bob2
            if a.bob2 != None:
                if a.bob2.hwp != None:
                    self.lblConnBob2.setStyleSheet('background-color: green')
                    self.lblAngleBob2.setText("{:.4f}".format(a.bob2.hwp.getPosition()))
                    if a.bob2.hwp.homed:
                        self.lblHomedBob2.setStyleSheet('background-color: green')
            # Update state Bob1
            if a.bob1 != None:
                if a.bob1.hwp != None:
                    self.lblConnHWPBob1.setStyleSheet('background-color: green')
                    self.lblAngleHWPBob1.setText("{:.4f}".format(a.bob1.hwp.getPosition()))
                    if a.bob1.hwp.homed:
                        self.lblHomedHWPBob1.setStyleSheet('background-color: green')
                if a.bob1.phglass != None:
                    self.lblConnGlass.setStyleSheet('background-color: green')
                    self.lblAngleGlass.setText("{:.4f}".format(a.bob1.phglass.getPosition()))
                    if a.bob1.phglass.homed:
                        self.lblHomedGlass.setStyleSheet('background-color: green')
                if a.bob1.weak[0] != None:
                        self.lblConnWeak1.setStyleSheet('background-color: green')
                        self.lblAngleWeak1.setText("{:.4f}".format(a.bob1.weak[0].getPosition()))
                        if a.bob1.weak[0].homed:
                            self.lblHomedWeak1.setStyleSheet('background-color: green')
                if a.bob1.weak[1] != None:
                        self.lblConnWeak2.setStyleSheet('background-color: green')
                        self.lblAngleWeak2.setText("{:.4f}".format(a.bob1.weak[1].getPosition()))
                        if a.bob1.weak[1].homed:
                            self.lblHomedWeak2.setStyleSheet('background-color: green')

    def getConfigFromUI(self):
        ''' Get configuration from the UI.
            
                Return: structure containing the configuration of the UI.
        '''
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
                    'zero' : float(self.txtZeroGlass.text()),
                    'posMin': float(self.txtPosMinGlass.text()),
                    'posMax': float(self.txtPosMaxGlass.text()),
                    'home': True }
        if self.chkActiveWeak1.isChecked():
            if not 'Bob1' in config:
                config['Bob1'] = {}
            config['Bob1']['weak1'] = {
                    'serial_number' : self.txtSNWeak1.text(),
                    'zero' : float(self.txtZeroWeak1.text()),
                    'home': True,
                    'func': self.cmbFuncWeak1.currentText()}
        if self.chkActiveWeak2.isChecked():
            if not 'Bob1' in config:
                config['Bob1'] = {}
            config['Bob1']['weak2'] = {
                    'serial_number' : self.txtSNWeak2.text(),
                    'zero' : float(self.txtZeroWeak2.text()),
                    'home': True,
                    'func': self.cmbFuncWeak2.currentText()}
                    

        return config

    def setUIFromConfig(self,config):
        ''' Set the UI with the values contained in the provided configuration
        structure.

            Args:
                config: configuration structure, organized in a dictionary with
                        structure equivalent to the structure of YAML
                        configuration files.
        '''
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
                    self.txtZeroGlass.setText(str(c['zero']))
                    self.txtPosMinGlass.setText(str(c['posMin']))
                    self.txtPosMaxGlass.setText(str(c['posMax']))
                else:
                    self.chkActiveGlass.setChecked(False)
#                    self.txtSNGlass.setEnabled(False)
#                    self.txtPosMinGlass.setEnabled(False)
#                    self.txtPosMaxGlass.setEnabled(False)
                if 'weak1' in config['Bob1']:
                    self.chkActiveWeak1.setChecked(True)
                    c = config['Bob1']['weak1']
                    self.txtSNWeak1.setText(c['serial_number'])
                    self.txtZeroWeak1.setText(str(c['zero']))
                    index = self.cmbFuncWeak1.findText(c['func'])
                    if index >= 0:
                        self.cmbFuncWeak1.setCurrentIndex(index)
                    else:
                        raise Exception('Invalid func string in weak1')
                else:
                    self.chkActiveWeak1.setChecked(False)
                if 'weak2' in config['Bob1']:
                    self.chkActiveWeak2.setChecked(True)
                    c = config['Bob1']['weak2']
                    self.txtSNWeak2.setText(c['serial_number'])
                    self.txtZeroWeak2.setText(str(c['zero']))
                    index = self.cmbFuncWeak2.findText(c['func'])
                    if index >= 0:
                        self.cmbFuncWeak2.setCurrentIndex(index)
                    else:
                        raise Exception('Invalid func string in weak2')
                else:
                    self.chkActiveWeak2.setChecked(False)
        except Exception as e:
            print('Exception in setUIFromConfig:')
            print(e.__doc__)
            print(e.message)
            return -1

        return 0

class Config():
    ''' Class containing the configuration of the current apparatus. The
    configuration is stored in the dictionary _config, which is equivalent to
    the following YAML file:

     Alice:
            basis:
                serial_number: 'xxxxxxxx'
                zero: xxx
                dirRot: 'CW'/'CCW'
                home: True
        Bob2:
            basis:
            ...
        Bob1:
            basis:
            ...
            meas:
                serial_number: 'xxxxxxxx'
                posMin: xxx
                posMax: xxx
                home: True
        weak:
            serial_number: 'xxxxxxxx'
            home: True.
    '''

    def __init__(self):
        '''Constructor. Initialize the configuration structure to an empty
        dictionary.'''
        self._config = {}

    def getConfig(self):
        '''Return the current configuration.'''
        return self._config

    def setConfig(self,config):
        '''Set the configuration dictionary to config.'''
        self._config = config

    def loadConfigFromFile(self,fname):
        '''Load configuration from YAML file.'''
        print('Loading configuration from '+fname)
        f = open(fname,'r')
        conffile = f.read()
        f.close()
        config = yaml.load(conffile)
        self.setConfig(config)

    def saveConfigToFile(self,fname):
        '''Save configuration to YAML file.'''
        print('Saving configuration to '+fname)
        f = open(fname,'w')
        f.write(yaml.dump(self._config,default_flow_style=False))
        f.close()

    def printConfig(self):
        '''Print current configuration in dictionary format.'''
        print(yaml.dump(self._config))
