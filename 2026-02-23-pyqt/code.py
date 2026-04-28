# Welcome to Day-3
# This is your coding workspace

import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Major Classes Demo")
        self.setGeometry(100, 100, 500, 300)
        label = QLabel("Hello, PyQt6!", self )
        label.setGeometry(150, 80, 200, 50)
        label.setStyleSheet("color: blue; font-size: 20px; font-weight: bold; font-family: Arial; background-color: yellow;border: 2px solid red; border-radius: 10px; padding: 10px; text-align: center;")
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

def main():
   app = QApplication(sys.argv)
   window = MainWindow()
   window.show()
   sys.exit(app.exec())      


if __name__ == "__main__":
    main()
