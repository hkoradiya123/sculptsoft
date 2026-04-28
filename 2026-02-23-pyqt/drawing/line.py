from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QPainter
class MyWidget(QtWidgets.QWidget):
   def paintEvent(self, event):
      painter = QtGui.QPainter(self)
      painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
      painter.setPen(QtCore.Qt.GlobalColor.green)
      painter.setBrush(QtCore.Qt.GlobalColor.white)
      painter.drawLine(100, 100, 400, 100)
      painter.drawLine(100, 200, 500, 200)

app = QtWidgets.QApplication([])
widget = MyWidget()
widget.show()
app.exec()