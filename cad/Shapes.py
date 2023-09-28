import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(250, 400, 400, 700)
        self.setWindowTitle('Rectangle in PyQt')

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawRect(250, 50, 500, 100)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
