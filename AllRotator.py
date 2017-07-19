
import sys
from PyQt4 import QtCore, QtGui, uic

sys.path.append('..')
from ThorCon import ThorCon

qtCreatorFile = 'AllRotator.ui'

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
        
        self.txtStep.textEdited.connect(self.ChangeStep)        
        self.step = float(self.txtStep.text())
        self.connected = False
        self.connected_2 = False
        self.connected_3 = False
        self.connected_4 = False
        self.connected_5 = False
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdatePos)
        self.timerStarted = False

    def Connect(self):
        if not self.connected:
            self.connected = True
            self.btnConnect.setStyleSheet('background-color: red')
            self.btnConnect.setText('Disconnect')
            self.SN = int(self.txtSN.text())
            self.con = ThorCon(serial_number=self.SN)
            
            self.btnUp.setEnabled(True)
            self.btnDown.setEnabled(True)
            self.btnHome.setEnabled(True)
            self.txtPos.setEnabled(True)
            self.btnMove.setEnabled(True)
            
            if self.timerStarted == False:
                self.timer.start(100)

        else:
            if not (self.connected_2 or self.connected_3 or self.connected_4 or self.connected_5):
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

    def Connect_2(self):
        if not self.connected_2:
            self.connected_2 = True
            self.btnConnect_2.setStyleSheet('background-color: red')
            self.btnConnect_2.setText('Disconnect')
            self.SN_2 = int(self.txtSN_2.text())
            self.con_2 = ThorCon(serial_number=self.SN_2)
            
            self.btnUp_2.setEnabled(True)
            self.btnDown_2.setEnabled(True)
            self.btnHome_2.setEnabled(True)
            self.txtPos_2.setEnabled(True)
            self.btnMove_2.setEnabled(True)
            
            if self.timerStarted == False:
                self.timer.start(100)

        else:
            if not (self.connected or self.connected_3 or self.connected_4 or self.connected_5):
                self.timer.stop()           
            
            self.connected_2 =  False
            self.con_2.close()
            self.btnConnect_2.setStyleSheet('')            
            self.btnConnect_2.setText('Connect')
            
            self.btnUp_2.setEnabled(False)
            self.btnDown_2.setEnabled(False)
            self.btnHome_2.setEnabled(False)
            self.txtPos_2.setEnabled(False)
            self.btnMove_2.setEnabled(False)
            
    def Connect_3(self):
        if not self.connected_3:
            self.connected_3 = True
            self.btnConnect_3.setStyleSheet('background-color: red')
            self.btnConnect_3.setText('Disconnect')
            self.SN_3 = int(self.txtSN_3.text())
            self.con_3 = ThorCon(serial_number=self.SN_3)
            
            self.btnUp_3.setEnabled(True)
            self.btnDown_3.setEnabled(True)
            self.btnHome_3.setEnabled(True)
            self.txtPos_3.setEnabled(True)
            self.btnMove_3.setEnabled(True)
            
            if self.timerStarted == False:
                self.timer.start(100)

        else:
            if not (self.connected_2 or self.connected or self.connected_4 or self.connected_5):
                self.timer.stop()
            
            self.connected_3 =  False
            self.con_3.close()
            self.btnConnect_3.setStyleSheet('')            
            self.btnConnect_3.setText('Connect')
            
            self.btnUp_3.setEnabled(False)
            self.btnDown_3.setEnabled(False)
            self.btnHome_3.setEnabled(False)
            self.txtPos_3.setEnabled(False)
            self.btnMove_3.setEnabled(False)
            
    def Connect_4(self):
        if not self.connected_4:
            self.connected_4 = True
            self.btnConnect_4.setStyleSheet('background-color: red')
            self.btnConnect_4.setText('Disconnect')
            self.SN_4 = int(self.txtSN_4.text())
            self.con_4 = ThorCon(serial_number=self.SN_4)
            
            self.btnUp_4.setEnabled(True)
            self.btnDown_4.setEnabled(True)
            self.btnHome_4.setEnabled(True)
            self.txtPos_4.setEnabled(True)
            self.btnMove_4.setEnabled(True)
            
            if self.timerStarted == False:
                self.timer.start(100)

        else:
            if not (self.connected_2 or self.connected_3 or self.connected or self.connected_5):
                self.timer.stop()
            
            self.connected_4 =  False
            self.con_4.close()
            self.btnConnect_4.setStyleSheet('')            
            self.btnConnect_4.setText('Connect')
            
            self.btnUp_4.setEnabled(False)
            self.btnDown_4.setEnabled(False)
            self.btnHome_4.setEnabled(False)
            self.txtPos_4.setEnabled(False)
            self.btnMove_4.setEnabled(False)
            
    def Connect_5(self):
        if not self.connected_5:
            self.connected_5 = True
            self.btnConnect_5.setStyleSheet('background-color: red')
            self.btnConnect_5.setText('Disconnect')
            self.SN_5 = int(self.txtSN_5.text())
            self.con_5 = ThorCon(serial_number=self.SN_5)
            
            self.btnUp_5.setEnabled(True)
            self.btnDown_5.setEnabled(True)
            self.btnHome_5.setEnabled(True)
            self.txtPos_5.setEnabled(True)
            self.btnMove_5.setEnabled(True)
            
            if self.timerStarted == False:
                self.timer.start(100)

        else:
            if not (self.connected_2 or self.connected_3 or self.connected_4 or self.connected):
                self.timer.stop()
            
            self.connected_5 =  False
            self.con_5.close()
            self.btnConnect_5.setStyleSheet('')            
            self.btnConnect_5.setText('Connect')
            
            self.btnUp_5.setEnabled(False)
            self.btnDown_5.setEnabled(False)
            self.btnHome_5.setEnabled(False)
            self.txtPos_5.setEnabled(False)
            self.btnMove_5.setEnabled(False)
            
    def Home(self):
        self.con.home()
    def Home_2(self):
        self.con_2.home()
    def Home_3(self):
        self.con_3.home()
    def Home_4(self):
        self.con_4.home()
    def Home_5(self):
        self.con_5.home()
    
    def Move(self):
        newPos = float(self.txtMove.text())
        self.con.goto(newPos)
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
        
    def MoveUp(self):
        self.con.move(self.step)
    def MoveUp_2(self):
        self.con_2.move(self.step)
    def MoveUp_3(self):
        self.con_3.move(self.step)
    def MoveUp_4(self):
        self.con_4.move(self.step)
    def MoveUp_5(self):
        self.con_5.move(self.step)
        
    def MoveDown(self):
        self.con.move(-self.step)
    def MoveDown_2(self):
        self.con_2.move(-self.step)
    def MoveDown_3(self):
        self.con_3.move(-self.step)
    def MoveDown_4(self):
        self.con_4.move(-self.step)
    def MoveDown_5(self):
        self.con_5.move(-self.step)
        
    def UpdatePos(self):
        if self.connected:
            self.txtPos.setText("{:10.5}".format(self.con.position()))
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
    
            
if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = Apt()
    window.show()
    sys.exit(app.exec_())
