import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush

class CubeLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Cube Loader")
        self.setFixedSize(200, 200)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() // 2, self.height() // 2)
        painter.rotate(self.angle)
        
        size = 75
        side = size // 2
        depth = 37  # Approximate Z depth

        faces = [
            QColor(40, 180, 180),
            QColor(60, 160, 160),
            QColor(80, 140, 140),
            QColor(100, 120, 120)
        ]

        for i in range(4):
            painter.save()
            painter.rotate(i * 90)
            painter.translate(depth, 0)
            painter.setBrush(QBrush(faces[i]))
            painter.drawRect(-side, -side, size, size)
            painter.restore()

        # Top face (simulate cube top)
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRect(-side, -side, size, size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CubeLoader()
    window.show()
    sys.exit(app.exec_())