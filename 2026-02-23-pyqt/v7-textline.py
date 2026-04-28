import sys
from PyQt6.QtWidgets  import   QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget   

app = QApplication(sys.argv)
window = QMainWindow()  

window.setWindowTitle("PyQt Line Edit Example")
window.setGeometry(100, 100, 400, 200)

box = QLineEdit(window)
box.setPlaceholderText("Enter your name")
box.setGeometry(100, 50, 200, 30)

button = QPushButton("Submit", window)
button.setGeometry(150, 100, 100, 30)
counter = 0

label_counter = QLabel(f"Counter: {counter}", window)
label_counter.setGeometry(150, 150, 100, 30)

button.clicked.connect(lambda: onButtonClick(box))
def onButtonClick(box):
    name = box.text()
    print(f"Hello, {name}!")
    global counter
    counter += 1
    label_counter.setText(f"Counter: {counter}")


window.show()
sys.exit(app.exec())