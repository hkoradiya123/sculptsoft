import sys
from PyQt6.QtWidgets import QApplication, QButtonGroup , QMainWindow , QRadioButton , QVBoxLayout , QWidget, QLabel

class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Radio Button Example")
        self.radioBtn1 = QRadioButton("Gpay",self )
        self.radioBtn2 = QRadioButton("paytm",self )
        self.radioBtn3 = QRadioButton("Bhim",self )
        self.radioBtn4 = QRadioButton("PhonePay",self )
        self.radioBtn5 = QRadioButton("💵CASH",self)
        self.radioBtn6 = QRadioButton("💳Online",self)

        self.radiobtn_group_1= QButtonGroup(self)
        self.radiobtn_group_2= QButtonGroup(self)


        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 600, 500)
        self.radioBtn1.setGeometry(0,0,200,100)
        self.radioBtn2.setGeometry(0,50,200,100)
        self.radioBtn3.setGeometry(0,100,200,100)
        self.radioBtn4.setGeometry(0,150,200,100)
        self.radioBtn5.setGeometry(0,250,200,100)
        self.radioBtn6.setGeometry(150,250,200,100)

        self.radiobtn_group_1.addButton(self.radioBtn1)
        self.radiobtn_group_1.addButton(self.radioBtn2)
        self.radiobtn_group_1.addButton(self.radioBtn3)
        self.radiobtn_group_1.addButton(self.radioBtn4)

        self.radiobtn_group_2.addButton(self.radioBtn5)
        self.radiobtn_group_2.addButton(self.radioBtn6)

    
        self.radioBtn1.toggled.connect(self.onRadioBtnClicked)
        self.radioBtn2.toggled.connect(self.onRadioBtnClicked)
        self.radioBtn3.toggled.connect(self.onRadioBtnClicked)
        self.radioBtn4.toggled.connect(self.onRadioBtnClicked)
        self.radioBtn5.toggled.connect(self.onRadioBtnClicked)
        self.radioBtn6.toggled.connect(self.onRadioBtnClicked)

    def onRadioBtnClicked(self):
        radio = self.sender()
        print(f'{radio.text()} is selected')



        self.setStyleSheet("QRadioButton{font-family:arial;"
                           "font-size:20px;"
                           "}")

       

def main():
    app = QApplication(sys.argv)
    window = mainwindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()