import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 500, 500)
        self.line_edit = QLineEdit(self)
        self.myButton = QPushButton("My_button", self)
        
        # Fix: Create buttons without setObjectName call
        self.btn1 = QPushButton('btn1', self)
        self.btn1.setObjectName("btn1")
        self.btn2 = QPushButton('btn2', self)
        self.btn2.setObjectName("btn2")
        self.btn3 = QPushButton('btn3', self)
        self.btn3.setObjectName("btn3")
        
        self.initUi()
    
    def initUi(self):
        central_Widget = QWidget()
        
        # Use vertical layout to organize widgets
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        
        # Add widgets to layouts
        vbox.addWidget(self.line_edit)
        vbox.addWidget(self.myButton)
        
        hbox.addWidget(self.btn1)
        hbox.addWidget(self.btn2)
        hbox.addWidget(self.btn3)
        
        vbox.addLayout(hbox)
        
        central_Widget.setLayout(vbox)
        self.setCentralWidget(central_Widget)
        
        self.line_edit.setStyleSheet('font-size:25px; font-family:Arial')
        self.myButton.clicked.connect(self.submit)
        self.line_edit.setObjectName("line_edit")
        self.setStyleSheet('''
            QPushButton {
                font-size:30px;
                font-family:Arial;
                padding:20px;
                margin:10px;
                border:1px solid black;
                border-radius:20px;
            }
            #btn1{
                background-color:red;
            }
            #btn2{
                background-color:yollow;
            }
            #btn3{
                background-color:blue;
            }
        ''')
    
    def submit(self):
        print(f"button is clicked, {self.line_edit.text()}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())