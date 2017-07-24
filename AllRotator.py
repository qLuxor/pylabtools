
import sys
from PyQt4 import QtCore, QtGui, uic

sys.path.append('..')
from ThorCon import ThorCon

import logging
import traceback
import json

qtCreatorFile = 'AllRotator.ui'

Ui_Widget, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Apt(QtGui.QWidget, Ui_Widget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        Ui_Widget.__init__(self)
        self.setupUi(self)
        
        self.btnLoadSettings.clicked.connect(self.LoadSettings)
        
        self.btnUp_1.setAutoRepeat(True)
        self.btnDown_1.setAutoRepeat(True)
        self.btnUp_1.clicked.connect(self.MoveUp_1)
        self.btnDown_1.clicked.connect(self.MoveDown_1)
        self.btnConnect_1.clicked.connect(self.Connect_1)
        self.btnMove_1.clicked.connect(self.Move_1)
        self.btnHome_1.clicked.connect(self.Home_1)
        
        self.btnUp_2.setAutoRepeat(True)
        self.btnDown_2.setAutoRepeat(True)
        self.btnUp_2.clicked.connect(self.MoveUp_2)
        self.btnDown_2.clicked.connect(self.MoveDown_2)
        self.btnConnect_2.clicked.connect(self.Connect_2)
        self.btnMove_2.clicked.connect(self.Move_2)
        self.btnHome_2.clicked.connect(self.Home_2)
        
        self.btnUp_3.setAutoRepeat(True)
        self.btnDown_3.setAutoRepeat(True)
        self.btnUp_3.clicked.connect(self.MoveUp_3)
        self.btnDown_3.clicked.connect(self.MoveDown_3)
        self.btnConnect_3.clicked.connect(self.Connect_3)
        self.btnMove_3.clicked.connect(self.Move_3)
        self.btnHome_3.clicked.connect(self.Home_3)
        
        self.btnUp_4.setAutoRepeat(True)
        self.btnDown_4.setAutoRepeat(True)
        self.btnUp_4.clicked.connect(self.MoveUp_4)
        self.btnDown_4.clicked.connect(self.MoveDown_4)
        self.btnConnect_4.clicked.connect(self.Connect_4)
        self.btnMove_4.clicked.connect(self.Move_4)
        self.btnHome_4.clicked.connect(self.Home_4)
        
        self.btnUp_5.setAutoRepeat(True)
        self.btnDown_5.setAutoRepeat(True)
        self.btnUp_5.clicked.connect(self.MoveUp_5)
        self.btnDown_5.clicked.connect(self.MoveDown_5)
        self.btnConnect_5.clicked.connect(self.Connect_5)
        self.btnMove_5.clicked.connect(self.Move_5)
        self.btnHome_5.clicked.connect(self.Home_5)
        self.btnConnect_All.clicked.connect(self.Connect_All)
        self.btnDisconnect_All.clicked.connect(self.Disconnect_All)
        self.btnHome_All.clicked.connect(self.Home_All)
        self.btnMove_All.clicked.connect(self.Move_All)
        
        self.txtStep.textEdited.connect(self.ChangeStep)        
        self.step = float(self.txtStep.text())
        self.connected_1 = False
        self.connected_2 = False
        self.connected_3 = False
        self.connected_4 = False
        self.connected_5 = False
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdatePos)
        self.timerStarted = False

    def Connect_1(self):
        if not self.connected_1:
            self.connected_1 = True
            self.SN_1 = int(self.txtSN.text())
            self.con_1 = ThorCon(serial_number=self.SN)            
            if self.timerStarted == False:
                self.timer.start(100)
        else:
            if not (self.connected_2 or self.connected_3 or self.connected_4 or self.connected_5):
                self.timer.stop()
            self.connected_1 =  False
            self.con_1.close()
        self.checkConnections()

    def Connect_2(self):
        if not self.connected_2:
            self.connected_2 = True
            self.SN_2 = int(self.txtSN_2.text())
            self.con_2 = ThorCon(serial_number=self.SN_2)            
            if self.timerStarted == False:
                self.timer.start(100)
        else:
            if not (self.connected_1 or self.connected_3 or self.connected_4 or self.connected_5):
                self.timer.stop()           
            self.connected_2 =  False
            self.con_2.close()
        self.checkConnections()
            
    def Connect_3(self):
        if not self.connected_3:
            self.connected_3 = True
            self.SN_3 = int(self.txtSN_3.text())
            self.con_3 = ThorCon(serial_number=self.SN_3)            
            if self.timerStarted == False:
                self.timer.start(100)
        else:
            if not (self.connected_2 or self.connected_1 or self.connected_4 or self.connected_5):
                self.timer.stop()
            self.connected_3 =  False
            self.con_3.close()
        self.checkConnections()
            
    def Connect_4(self):
        if not self.connected_4:
            self.connected_4 = True
            self.SN_4 = int(self.txtSN_4.text())
            self.con_4 = ThorCon(serial_number=self.SN_4)            
            if self.timerStarted == False:
                self.timer.start(100)
        else:
            if not (self.connected_2 or self.connected_3 or self.connected_1 or self.connected_5):
                self.timer.stop()
            self.connected_4 =  False
            self.con_4.close()
        self.checkConnections()
            
    def Connect_5(self):
        if not self.connected_5:
            self.connected_5 = True
            self.SN_5 = int(self.txtSN_5.text())
            self.con_5 = ThorCon(serial_number=self.SN_5)
            if self.timerStarted == False:
                self.timer.start(100)
        else:
            if not (self.connected_2 or self.connected_3 or self.connected_4 or self.connected_1):
                self.timer.stop()
            self.connected_5 =  False
            self.con_5.close()
        self.checkConnections()
        
    def Connect_All(self):
        if not self.connected_1:
            self.Connect_1()
        if not self.connected_2:
            self.Connect_2()
        if not self.connected_3:
            self.Connect_3()
        if not self.connected_4:
            self.Connect_4()
        if not self.connected_5:
            self.Connect_5()
            
    def Disconnect_All(self):
        if self.connected_1:
            self.Connect_1()
        if self.connected_2:
            self.Connect_2()
        if self.connected_3:
            self.Connect_3()
        if self.connected_4:
            self.Connect_4()
        if self.connected_5:
            self.Connect_5()
            
    def Home_1(self):
        self.con_1.home()
    def Home_2(self):
        self.con_2.home()
    def Home_3(self):
        self.con_3.home()
    def Home_4(self):
        self.con_4.home()
    def Home_5(self):
        self.con_5.home()
        
    def Home_All(self):
        if self.connected_1:
            self.Home_1()
        if self.connected_2:
            self.Home_2()
        if self.connected_3:
            self.Home_3()
        if self.connected_4:
            self.Home_4()
        if self.connected_5:
            self.Home_5()
    
    def Move_1(self):
        newPos = float(self.txtMove_1.text())
        self.con_1.goto(newPos)
    def Move_2(self):
        newPos = float(self.txtMove_2.text())
        self.con_2.goto(newPos)
    def Move_3(self):
        newPos = float(self.txtMove_3.text())
        self.con_3.goto(newPos)
    def Move_4(self):
        newPos = float(self.txtMove_4.text())
        self.con_4.goto(newPos)
    def Move_5(self):
        newPos = float(self.txtMove_5.text())
        self.con_5.goto(newPos)
        
    def Move_All(self):
        if self.connected_1:
            self.Move_1()
        if self.connected_2:
            self.Move_2()
        if self.connected_3:
            self.Move_3()
        if self.connected_4:
            self.Move_4()
        if self.connected_5:
            self.Move_5()
        
    def MoveUp_1(self):
        self.con_1.move(self.step)
    def MoveUp_2(self):
        self.con_2.move(self.step)
    def MoveUp_3(self):
        self.con_3.move(self.step)
    def MoveUp_4(self):
        self.con_4.move(self.step)
    def MoveUp_5(self):
        self.con_5.move(self.step)
        
    def MoveDown_1(self):
        self.con_1.move(-self.step)
    def MoveDown_2(self):
        self.con_2.move(-self.step)
    def MoveDown_3(self):
        self.con_3.move(-self.step)
    def MoveDown_4(self):
        self.con_4.move(-self.step)
    def MoveDown_5(self):
        self.con_5.move(-self.step)
        
    def UpdatePos(self):
        if self.connected_1:
            self.txtPos_1.setText("{:10.5}".format(self.con_1.position()))
        if self.connected_2:
            self.txtPos_2.setText("{:10.5}".format(self.con_2.position()))
        if self.connected_3:
            self.txtPos_3.setText("{:10.5}".format(self.con_3.position()))
        if self.connected_4:
            self.txtPos_4.setText("{:10.5}".format(self.con_4.position()))
        if self.connected_5:
            self.txtPos_5.setText("{:10.5}".format(self.con_5.position()))
    
    def ChangeStep(self):
        self.step = float(self.txtStep.text())
        
    def LoadSettings(self):
        try:
            loadfilename=self.txtLoadFileName.text()
            with open(loadfilename) as json_data:
                settings = json.load(json_data)
                json_data.close()
            if "Label_1" in settings:
                self.txtLabel_1.setText(settings["Label_1"])
            if "Label_2" in settings:
                self.txtLabel_2.setText(settings["Label_2"])
            if "Label_3" in settings:
                self.txtLabel_3.setText(settings["Label_3"])
            if "Label_4" in settings:
                self.txtLabel_4.setText(settings["Label_4"])
            if "Label_5" in settings:
                self.txtLabel_5.setText(settings["Label_5"])
            if "SN_1" in settings:
                self.txtSN_1.setText(settings["SN_1"]) 
            if "SN_2" in settings:
                self.txtSN_2.setText(settings["SN_2"]) 
            if "SN_3" in settings:
                self.txtSN_3.setText(settings["SN_3"]) 
            if "SN_4" in settings:
                self.txtSN_4.setText(settings["SN_4"]) 
            if "SN_5" in settings:
                self.txtSN_5.setText(settings["SN_5"]) 
            if "pos_1" in settings:
                self.txtMove_1.setText(settings["pos_1"]) 
            if "pos_2" in settings:
                self.txtMove_2.setText(settings["pos_2"]) 
            if "pos_3" in settings:
                self.txtMove_3.setText(settings["pos_3"]) 
            if "pos_4" in settings:
                self.txtMove_4.setText(settings["pos_4"]) 
            if "pos_5" in settings:
                self.txtMove_5.setText(settings["pos_5"])            
        except Exception as e:
            logging.error(traceback.format_exc())
            
    def checkConnections(self):
        if self.connected_1:
            self.btnConnect_1.setStyleSheet('background-color: red')
            self.btnConnect_1.setText('Disconnect')
            self.btnUp_1.setEnabled(True)
            self.btnDown_1.setEnabled(True)
            self.btnHome_1.setEnabled(True)
            self.txtPos_1.setEnabled(True)
            self.btnMove_1.setEnabled(True)
        else:
            self.btnConnect_1.setStyleSheet('')            
            self.btnConnect_1.setText('Connect')            
            self.btnUp_1.setEnabled(False)
            self.btnDown_1.setEnabled(False)
            self.btnHome_1.setEnabled(False)
            self.txtPos_1.setEnabled(False)
            self.btnMove_1.setEnabled(False)
        
        if self.connected_2:
            self.btnConnect_2.setStyleSheet('background-color: red')
            self.btnConnect_2.setText('Disconnect')
            self.btnUp_2.setEnabled(True)
            self.btnDown_2.setEnabled(True)
            self.btnHome_2.setEnabled(True)
            self.txtPos_2.setEnabled(True)
            self.btnMove_2.setEnabled(True)
        else:
            self.btnConnect_2.setStyleSheet('')            
            self.btnConnect_2.setText('Connect')            
            self.btnUp_2.setEnabled(False)
            self.btnDown_2.setEnabled(False)
            self.btnHome_2.setEnabled(False)
            self.txtPos_2.setEnabled(False)
            self.btnMove_2.setEnabled(False)
            
        if self.connected_3:
            self.btnConnect_3.setStyleSheet('background-color: red')
            self.btnConnect_3.setText('Disconnect')
            self.btnUp_3.setEnabled(True)
            self.btnDown_3.setEnabled(True)
            self.btnHome_3.setEnabled(True)
            self.txtPos_3.setEnabled(True)
            self.btnMove_3.setEnabled(True)
        else:
            self.btnConnect_3.setStyleSheet('')            
            self.btnConnect_3.setText('Connect')            
            self.btnUp_3.setEnabled(False)
            self.btnDown_3.setEnabled(False)
            self.btnHome_3.setEnabled(False)
            self.txtPos_3.setEnabled(False)
            self.btnMove_3.setEnabled(False)
            
        if self.connected_4:
            self.btnConnect_4.setStyleSheet('background-color: red')
            self.btnConnect_4.setText('Disconnect')
            self.btnUp_4.setEnabled(True)
            self.btnDown_4.setEnabled(True)
            self.btnHome_4.setEnabled(True)
            self.txtPos_4.setEnabled(True)
            self.btnMove_4.setEnabled(True)
        else:
            self.btnConnect_4.setStyleSheet('')            
            self.btnConnect_4.setText('Connect')            
            self.btnUp_4.setEnabled(False)
            self.btnDown_4.setEnabled(False)
            self.btnHome_4.setEnabled(False)
            self.txtPos_4.setEnabled(False)
            self.btnMove_4.setEnabled(False)
            
        if self.connected_5:
            self.btnConnect_5.setStyleSheet('background-color: red')
            self.btnConnect_5.setText('Disconnect')
            self.btnUp_5.setEnabled(True)
            self.btnDown_5.setEnabled(True)
            self.btnHome_5.setEnabled(True)
            self.txtPos_5.setEnabled(True)
            self.btnMove_5.setEnabled(True)
        else:
            self.btnConnect_5.setStyleSheet('')            
            self.btnConnect_5.setText('Connect')            
            self.btnUp_5.setEnabled(False)
            self.btnDown_5.setEnabled(False)
            self.btnHome_5.setEnabled(False)
            self.txtPos_5.setEnabled(False)
            self.btnMove_5.setEnabled(False)
            
        if self.connected_1 or self.connected_2 or self.connected_3 or self.connected_4 or self.connected_5:
            self.btnDisconnect_All.setEnabled(True)
            self.btnDisconnect_All.setStyleSheet('background-color: red')
            self.btnMove_All.setEnabled(True)
            self.btnHome_All.setEnabled(True)
        else:
            self.btnDisconnect_All.setEnabled(False)
            self.btnDisconnect_All.setStyleSheet('')
            self.btnMove_All.setEnabled(False)
            self.btnHome_All.setEnabled(False)
            
        if self.connected_1 and self.connected_2 and self.connected_3 and self.connected_4 and self.connected_5:
            self.btnConnect_All.setEnabled(True)
        else:
            self.btnConnect_All.setEnabled(False)
            
    
            
if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Apt()
    window.show()
    sys.exit(app.exec_())
