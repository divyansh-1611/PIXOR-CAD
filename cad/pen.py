from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen

WIDTH = 2
COLOR = Qt.black
STYLE = Qt.SolidLine

ACTIVE_WIDTH = 5
ACTIVE_COLOR = Qt.red 
ACTIVE_STYLE = STYLE

line = QPen(COLOR, WIDTH, STYLE)
point = QPen(line.color(), WIDTH * 2, line.style())

activeLine = QPen(ACTIVE_COLOR, ACTIVE_WIDTH, ACTIVE_STYLE)
activePoint = QPen(ACTIVE_COLOR, ACTIVE_WIDTH * 2, ACTIVE_STYLE)
