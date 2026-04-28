import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel,QVBoxLayout,QHBoxLayout, QWidget,QGridLayout
from PyQt6.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initui()

    def initui(self):
        self.setWindowTitle("PyQt Layout Managers")
        self.setGeometry(self.screen().availableGeometry().width() // 2 - 300, self.screen().availableGeometry().height() // 2 - 200, 600, 400)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        Label1  = QLabel("Label 1",self)
        Label2  = QLabel("Label 2",self)
        Label3  = QLabel("Label 3",self)
        Label4  = QLabel("Label 4",self)
        Label5  = QLabel("Label 5",self)
        Label6  = QLabel("Label 6",self)
        Label7  = QLabel("Label 7",self)

        Label1.setStyleSheet("color: black; background-color: lightblue;")
        Label2.setStyleSheet("color: black; background-color: lightgreen;")
        Label3.setStyleSheet("color: black; background-color: lightcoral;")
        Label4.setStyleSheet("color: black; background-color: lightyellow;")
        Label5.setStyleSheet("color: black; background-color: lightgray;")
        Label6.setStyleSheet("color: black; background-color: lightpink;")
        Label7.setStyleSheet("color: black; background-color: lightcyan;")

        # vbox = QVBoxLayout()
        # vbox.addWidget(Label1)
        # vbox.addWidget(Label2)
        # vbox.addWidget(Label3)
        # vbox.addWidget(Label4)
        # vbox.addWidget(Label5)
        # vbox.addWidget(Label6)
        # vbox.addWidget(Label7)

        # self.centralWidget.setLayout(vbox)

        # Hbox = QHBoxLayout()

        # Hbox.addWidget(Label1)
        # Hbox.addWidget(Label2)
        # Hbox.addWidget(Label3)
        # Hbox.addWidget(Label4)
        # Hbox.addWidget(Label5)
        # Hbox.addWidget(Label6)
        # Hbox.addWidget(Label7)

        # self.centralWidget.setLayout(Hbox)


        grid = QGridLayout()
        grid.addWidget(Label1, 0, 0)
        grid.addWidget(Label2, 0, 1)
        grid.addWidget(Label3, 0, 2)
        grid.addWidget(Label4, 1, 0)
        grid.addWidget(Label5, 1, 1)
        grid.addWidget(Label6, 1, 2)
        grid.addWidget(Label7, 2, 0,1,3)

        self.centralWidget.setLayout(grid)
        # self.centralWidget.setlayout(grid)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()