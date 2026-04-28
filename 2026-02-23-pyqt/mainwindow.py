from PyQt6.QtWidgets import *
import sys


app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("My First PyQt App")
window.setGeometry(100, 100, 500, 300)

submit = QPushButton("Submit", window)
username = QLineEdit(window)
username.setPlaceholderText("enter your name")
username.setGeometry(200,70,150,30)
submit.setGeometry(200,200,70,30)


label = QLabel(f"hello user",window)
label.setGeometry(200,150,100,30)


def onclick():
    label.setText(f"hello {username.text()}")
submit.clicked.connect(onclick)
window.show()
window.setFixedSize(500,300)
sys.exit(app.exec())