# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 11:14:59 2016

@author: sagnac
"""

import sys
from PyQt4 import QtCore, QtGui, uic

sys.path.append('..')
import aptlib

qtCreatorFile = 'rotator.ui'

Ui_Widget, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Apt(QtGui.QWidget, Ui_Widget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        Ui_Widget.__init__(self)
        self.setupUi(self)
        self.btnUp.setAutoRepeat(True)
        self.btnDown.setAutoRepeat(True)
        self.btnUp.clicked.connect(self.MoveUp)
        self.btnDown.clicked.connect(self.MoveDown)
        self.btnConnect.clicked.connect(self.Connect)
        self.btnMove.clicked.connect(self.Move)
        self.btnHome.clicked.connect(self.Home)
        self.txtStep.textEdited.connect(self.ChangeStep)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdatePos)
#        self.timer.setSingleShot(True)
        
        self.step = float(self.txtStep.text())
        self.connected = False

    def Connect(self):
        if not self.connected:
            self.connected = True
            self.btnConnect.setStyleSheet('background-color: red')
            self.btnConnect.setText('Disconnect')
            self.SN = int(self.txtSN.text())
            self.con = aptlib.PRM1(serial_number=self.SN)
            
            self.btnUp.setEnabled(True)
            self.btnDown.setEnabled(True)
            self.btnHome.setEnabled(True)
            self.txtPos.setEnabled(True)
            self.btnMove.setEnabled(True)
            
            self.timer.start(100)

        else:
            self.timer.stop()            
            
            self.connected =  False
            self.con.close()
            self.btnConnect.setStyleSheet('')            
            self.btnConnect.setText('Connect')
            
            self.btnUp.setEnabled(False)
            self.btnDown.setEnabled(False)
            self.btnHome.setEnabled(False)
            self.txtPos.setEnabled(False)
            self.btnMove.setEnabled(False)


            
    def Home(self):
        self.con.home()
    
    def Move(self):
        newPos = float(self.txtMove.text())
        self.con.goto(newPos)
        
    def ChangeStep(self):
        self.step = float(self.txtStep.text())
    
    def MoveUp(self):
        self.con.move(self.step)
    
    def MoveDown(self):
        self.con.move(-self.step)
        
    def UpdatePos(self):
        self.txtPos.setText("{:10.5}".format(self.con.position()))
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Apt()
    window.show()
    sys.exit(app.exec_())
