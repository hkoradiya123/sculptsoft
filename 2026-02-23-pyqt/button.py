import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget



app = QApplication(sys.argv)


window = QMainWindow()


window.setWindowTitle("PyQt Major Classes Demo")

# Create QLabel
label = QLabel("Hello, PyQt!")

# Create QPushButton
button = QPushButton("Click Me")
button.clicked.connect(lambda: onButtonClick(window))

# Create a vertical layout
layout = QVBoxLayout()
layout.addWidget(label)
layout.addWidget(button)

# Create a central widget and set the layout
central_widget = QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

def onButtonClick(window):
    print("Button clicked!")
window.show()
sys.exit(app.exec())