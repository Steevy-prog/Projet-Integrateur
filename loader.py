import sys
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout


class Dot(QLabel):
    def __init__(self, size=18, color="#2ecc71"):
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {size // 2}px;
        """)


class ThreeDotWaveLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wave Dot Loader")
        self.setFixedSize(200, 100)
        self.setStyleSheet("background-color: white; border-radius: 12px;")

        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        self.dots = [Dot() for _ in range(3)]
        for dot in self.dots:
            layout.addWidget(dot)

        self.setLayout(layout)
        self.animations = []

        self.init_wave()

    def init_wave(self):
        for i, dot in enumerate(self.dots):
            anim = QPropertyAnimation(dot, b"geometry")
            anim.setDuration(700)
            anim.setStartValue(QRect(dot.x(), dot.y(), dot.width(), dot.height()))
            anim.setKeyValueAt(0.5, QRect(dot.x(), dot.y() - 20, dot.width(), dot.height()))
            anim.setEndValue(QRect(dot.x(), dot.y(), dot.width(), dot.height()))
            anim.setLoopCount(-1)
            anim.setEasingCurve(QEasingCurve.InOutSine)

            # Start each animation with a delay for wave effect
            QTimer.singleShot(i * 200, anim.start)

            self.animations.append(anim)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loader = ThreeDotWaveLoader()
    loader.show()
    sys.exit(app.exec_())