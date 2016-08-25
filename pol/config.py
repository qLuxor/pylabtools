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
            basis1:
            ...
            basis2:
            ...
            meas:
                serial_number: 'xxxxxxxx'
                zero: xxx
                posMin: xxx
                posMax: xxx
                home: True
            weak:
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
        self.chkActiveAlice.stateChanged.connect(self.updateUI)
        self.chkActiveHWP1Bob1.stateChanged.connect(self.updateUI)
        self.chkActiveHWP2Bob1.stateChanged.connect(self.updateUI)
        self.chkActiveBob2.stateChanged.connect(self.updateUI)
        self.chkActiveGlass.stateChanged.connect(self.updateUI)
        self.chkActiveWeak.stateChanged.connect(self.updateUI)

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
        self.chkActiveHWP1Bob1.setEnabled(False)
        self.cmbDirHWP1Bob1.setEnabled(False)
        self.txtSNHWP1Bob1.setEnabled(False)
        self.txtZeroHWP1Bob1.setEnabled(False)
        self.chkActiveHWP2Bob1.setEnabled(False)
        self.cmbDirHWP2Bob1.setEnabled(False)
        self.txtSNHWP2Bob1.setEnabled(False)
        self.txtZeroHWP2Bob1.setEnabled(False)
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
        self.chkActiveHWP1Bob1.setEnabled(True)
        self.chkActiveHWP2Bob1.setEnabled(True)
        self.chkActiveGlass.setEnabled(True)
        self.chkActiveWeak.setEnabled(True)

        # erase control background
        self.lblConnAlice.setStyleSheet('')
        self.lblConnBob2.setStyleSheet('')
        self.lblConnHWP1Bob1.setStyleSheet('')
        self.lblConnHWP2Bob1.setStyleSheet('')
        self.lblConnGlass.setStyleSheet('')
        self.lblConnWeak.setStyleSheet('')

        self.lblHomedAlice.setStyleSheet('')
        self.lblHomedBob2.setStyleSheet('')
        self.lblHomedHWP1Bob1.setStyleSheet('')
        self.lblHomedHWP2Bob1.setStyleSheet('')
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

            #self.chkActiveHWP1Bob1.setEnabled(True)
            if not self.chkActiveHWP1Bob1.isChecked():
                self.cmbDirHWP1Bob1.setEnabled(False)
                self.txtSNHWP1Bob1.setEnabled(False)
                self.txtZeroHWP1Bob1.setEnabled(False)
            else:
                self.cmbDirHWP1Bob1.setEnabled(True)
                self.txtSNHWP1Bob1.setEnabled(True)
                self.txtZeroHWP1Bob1.setEnabled(True)

            #self.chkActiveHWP2Bob1.setEnabled(True)
            if not self.chkActiveHWP2Bob1.isChecked():
                self.cmbDirHWP2Bob1.setEnabled(False)
                self.txtSNHWP2Bob1.setEnabled(False)
                self.txtZeroHWP2Bob1.setEnabled(False)
            else:
                self.cmbDirHWP2Bob1.setEnabled(True)
                self.txtSNHWP2Bob1.setEnabled(True)
                self.txtZeroHWP2Bob1.setEnabled(True)

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

            #self.chkActiveWeak.setEnabled(True)
            if not self.chkActiveWeak.isChecked():
                self.cmbFuncWeak.setEnabled(False)
                self.txtSNWeak.setEnabled(False)
                self.txtZeroWeak.setEnabled(False)
            else:
                self.cmbFuncWeak.setEnabled(True)
                self.txtSNWeak.setEnabled(True)
                self.txtZeroWeak.setEnabled(True)
            
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
                if a.bob1.hwp1 != None:
                    self.lblConnHWP1Bob1.setStyleSheet('background-color: green')
                    self.lblAngleHWP1Bob1.setText("{:.4f}".format(a.bob1.hwp1.getPosition()))
                    if a.bob1.hwp1.homed:
                        self.lblHomedHWP1Bob1.setStyleSheet('background-color: green')
                if a.bob1.hwp2 != None:
                    self.lblConnHWP2Bob1.setStyleSheet('background-color: green')
                    self.lblAngleHWP2Bob1.setText("{:.4f}".format(a.bob1.hwp2.getPosition()))
                    if a.bob1.hwp2.homed:
                        self.lblHomedHWP2Bob1.setStyleSheet('background-color: green')
                if a.bob1.phshift != None:
                    self.lblConnGlass.setStyleSheet('background-color: green')
                    self.lblAngleGlass.setText("{:.4f}".format(a.bob1.phshift.getPosition()))
                    if a.bob1.phshift.homed:
                        self.lblHomedGlass.setStyleSheet('background-color: green')
                if a.bob1.weak[0] != None:
                        self.lblConnWeak.setStyleSheet('background-color: green')
                        self.lblAngleWeak.setText("{:.4f}".format(a.bob1.weak[0].getPosition()))
                        if a.bob1.weak[0].homed:
                            self.lblHomedWeak.setStyleSheet('background-color: green')

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
        if self.chkActiveHWP1Bob1.isChecked():
            config['Bob1'] = {}
            config['Bob1']['basis1'] = {
                    'serial_number': self.txtSNHWP1Bob1.text(),
                    'zero': float(self.txtZeroHWP1Bob1.text()),
                    'dirRot': dirRot[self.cmbDirHWP1Bob1.currentIndex()],
                    'home': True }
        if self.chkActiveHWP2Bob1.isChecked():
            if not 'Bob1' in config:
                config['Bob1'] = {}
            config['Bob1']['basis2'] = {
                    'serial_number': self.txtSNHWP2Bob1.text(),
                    'zero': float(self.txtZeroHWP2Bob1.text()),
                    'dirRot': dirRot[self.cmbDirHWP2Bob1.currentIndex()],
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
        if self.chkActiveWeak.isChecked():
            if not 'Bob1' in config:
                config['Bob1'] = {}
            config['Bob1']['weak'] = {
                    'serial_number' : self.txtSNWeak.text(),
                    'zero' : float(self.txtZeroWeak.text()),
                    'home': True,
                    'func': self.cmbFuncWeak.currentText()}

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
                    c = config['Alice']['basis']
                    self.txtSNAlice.setText(c['serial_number'])
                    self.txtZeroAlice.setText(str(c['zero']))
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
                    self.txtZeroBob2.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirBob2.setCurrentIndex(1)
                    else:
                        self.cmbDirBob2.setCurrentIndex(0)
                else:
                    self.chkActiveBob2.setChecked(False)
            if 'Bob1' in config:
                if 'basis1' in config['Bob1']:
                    self.chkActiveHWP1Bob1.setChecked(True)
                    c = config['Bob1']['basis1']
                    self.txtSNHWP1Bob1.setText(c['serial_number'])
                    self.txtZeroHWP1Bob1.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirHWP1Bob1.setCurrentIndex(1)
                    else:
                        self.cmbDirHWP1Bob1.setCurrentIndex(0)
                else:
                    self.chkActiveHWP1Bob1.setChecked(False)
                if 'basis2' in config['Bob1']:
                    self.chkActiveHWP2Bob1.setChecked(True)
                    c = config['Bob1']['basis2']
                    self.txtSNHWP2Bob1.setText(c['serial_number'])
                    self.txtZeroHWP2Bob1.setText(str(c['zero']))
                    if c['dirRot'] == 'CCW':
                        self.cmbDirHWP2Bob1.setCurrentIndex(1)
                    else:
                        self.cmbDirHWP2Bob1.setCurrentIndex(0)
                else:
                    self.chkActiveHWP2Bob1.setChecked(False)
                if 'meas' in config['Bob1']:
                    self.chkActiveGlass.setChecked(True)
                    c = config['Bob1']['meas']
                    self.txtSNGlass.setText(c['serial_number'])
                    self.txtZeroGlass.setText(str(c['zero']))
                    self.txtPosMinGlass.setText(str(c['posMin']))
                    self.txtPosMaxGlass.setText(str(c['posMax']))
                else:
                    self.chkActiveGlass.setChecked(False)
                if 'weak' in config['Bob1']:
                    self.chkActiveWeak.setChecked(True)
                    c = config['Bob1']['weak']
                    self.txtSNWeak.setText(c['serial_number'])
                    self.txtZeroWeak.setText(str(c['zero']))
                    index = self.cmbFuncWeak.findText(c['func'])
                    if index >= 0:
                        self.cmbFuncWeak.setCurrentIndex(index)
                    else:
                        raise Exception('Invalid func string in weak')
                else:
                    self.chkActiveWeak1.setChecked(False)
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
            basis1:
                ...
            basis2:
                ...
            meas:
                serial_number: 'xxxxxxxx'
                zero: xxx
                posMin: xxx
                posMax: xxx
                home: True
            weak:
                serial_number: 'xxxxxxxx'
                zero: xxx
                home: True
                func: 'aaa'   
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
        if 'basis' in config['Bob1']:
            config['Bob1']['basis1'] = config['Bob1'].pop('basis')
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
