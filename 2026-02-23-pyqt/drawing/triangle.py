from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QPainter, QPainterPath
class MyWidget(QtWidgets.QWidget):
   def paintEvent(self, event):
      painter = QPainter()
      path = QPainterPath()
      painter.begin(self)
      painter.setRenderHint(QPainter.RenderHint.Antialiasing)
      painter.setPen(QtCore.Qt.GlobalColor.red)
      path.moveTo(100, 200)
      path.lineTo(200, 100)
      path.lineTo(300, 200)
      path.lineTo(100, 200)
      painter.drawPath(path)
app = QtWidgets.QApplication([])
widget = MyWidget()
widget.show()
app.exec()