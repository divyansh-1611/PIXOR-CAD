import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QRect

class CircleDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.center = None
        self.radius = None
        self.setWindowTitle('Circle Arc Drawer')
        self.setGeometry(100, 100, 400, 400)

    def set_center_and_radius(self, center, radius):
        self.center = center
        self.radius = radius

    def paintEvent(self, event):
        if not all([self.center, self.radius]):
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Calculate the top-left corner of the bounding rectangle for the circle
        top_left = self.center[0] - self.radius, self.center[1] - self.radius

        # Calculate the width and height of the bounding rectangle (same for a circle)
        width = height = 2 * self.radius

        # Create a QRect representing the bounding rectangle
        bounding_rect = QRect(*top_left, width, height)

        # Draw the circular arc (360 degrees, from 0 to 5760, where 1 degree = 16 units)
        painter.drawArc(bounding_rect, 0, 5760)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircleDrawer()
    window.set_center_and_radius((200, 200), 100)  # Set center (x, y) and radius
    window.show()
    sys.exit(app.exec())
