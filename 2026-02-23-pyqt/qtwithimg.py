import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Image Display")
        self.setGeometry(100, 100, 600, 600)
        lbl1 = QLabel(self)
        pixmap = QPixmap("chad.jpg")
        lbl1.setPixmap(pixmap)
        lbl1.setGeometry((self.width()-lbl1.width()) // 2 , (self.height() - lbl1.height()) // 2 , 100, 100)
        lbl1.setScaledContents(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()