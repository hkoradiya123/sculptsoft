from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QPainter
class MyWidget(QtWidgets.QWidget):
   def paintEvent(self, event):
      painter = QPainter(self)
    #   painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    #   painter.setPen(QtCore.Qt.GlobalColor.white)
      painter.drawRect(100, 100, 300, 200)

app = QtWidgets.QApplication([])
widget = MyWidget()
widget.show()
app.exec()