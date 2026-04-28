import sys
from PyQt6.QtWidgets import QApplication, QCheckBox, QMainWindow, QLabel, QPushButton,QVBoxLayout,QHBoxLayout, QWidget,QGridLayout  
from PyQt6.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.button = QPushButton("Click Me",self)
        self.lebel = QLabel("Hello, PyQt!",self)
        self.checkbox = QCheckBox("Check Me",self)
        self.initui()

    def initui(self):
        self.button.setGeometry(250, 150, 100, 50)
        self.lebel.setGeometry(250, 100, 200, 50)
        self.checkbox.setGeometry(250, 200, 100, 50)
        self.setWindowTitle("PyQt Layout Managers")
        self.setGeometry(self.screen().availableGeometry().width() // 2 - 300, self.screen().availableGeometry().height() // 2 - 200, 600, 400)
        self.button.clicked.connect(self.onButtonClick)
        self.checkbox.stateChanged.connect(self.onCheckboxStateChange)

    def onCheckboxStateChange(self, state):
        if state == 2:  # Checked
            self.lebel.setText("Checkbox Checked!")
            self.button.setEnabled(True)
        else:
            self.lebel.setText("Checkbox Unchecked!")
            self.button.setEnabled(True)

    def onButtonClick(self):
        self.lebel.setText("Button Clicked!")
        self.button.setText("Clicked")
        self.button.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()