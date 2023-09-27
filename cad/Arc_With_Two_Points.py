import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QPoint, QRectF
import math

class ArcDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.center = None
        self.start_point = None
        self.end_point = None
        self.setWindowTitle('Arc Drawer')
        self.setGeometry(100, 100, 400, 400)

    def set_center_and_points(self, center, start_point, end_point):
        self.center = center
        self.start_point = start_point
        self.end_point = end_point

    def paintEvent(self, event):
        if not all([self.center, self.start_point, self.end_point]):
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Calculate the radius
        radius = math.dist(self.center, self.start_point)

        # Calculate the start angle and span angle in degrees
        start_angle = math.degrees(math.atan2(self.start_point[1] - self.center[1], self.start_point[0] - self.center[0]))
        end_angle = math.degrees(math.atan2(self.end_point[1] - self.center[1], self.end_point[0] - self.center[0]))

        # Ensure that the angles are in the correct range (0 to 360 degrees)
        start_angle %= 360
        end_angle %= 360

        # PyQt uses a coordinate system with the origin at the top-left corner,
        # so we need to adjust the angles accordingly.
        start_angle = 90 - start_angle
        end_angle = 90 - end_angle

        # Create a QRectF for drawing the arc
        rect = QRectF(self.center[0] - radius, self.center[1] - radius, 2 * radius, 2 * radius)

        # Draw the arc
        painter.drawArc(rect, int(start_angle * 16), int((end_angle - start_angle) * 16))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ArcDrawer()
    window.set_center_and_points((200, 200), (300, 200), (200, 300))  # Set center and two points
    window.show()
    sys.exit(app.exec())
