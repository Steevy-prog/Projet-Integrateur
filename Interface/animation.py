from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPainter, QBrush
import sys
from PyQt6.QtWidgets import QApplication, QLabel


class Highlight(QWidget):
    def __init__(self, parent=None, color=QColor(0, 120, 215, 180), radius=20):
        super().__init__(parent)
        self.color = color
        self.radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)


class AnimatedNavBar(QWidget):
    selected = pyqtSignal(int, str)  # (index, label)

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(0)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.button_layout)

        self.buttons = []
        for i, label in enumerate(items):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    font-size: 16px;
                    color: #444;
                    padding: 10px 25px;
                }
                QPushButton:hover {
                    color: #0078d7;
                }
                QPushButton:checked {
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(self._handle_click)
            self.button_layout.addWidget(btn)
            self.buttons.append(btn)

        self.highlight = Highlight(self)
        self.highlight.raise_()
        self.anim = QPropertyAnimation(self.highlight, b"geometry")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        QTimer.singleShot(0, self._init_highlight)

    def _init_highlight(self):
        if self.buttons:
            self.buttons[0].setChecked(True)
            self._move_highlight(self.buttons[0], instant=True)
            self.selected.emit(0, self.buttons[0].text())

    def _handle_click(self):
        clicked = self.sender()
        for btn in self.buttons:
            btn.setChecked(False)
        clicked.setChecked(True)

        index = self.buttons.index(clicked)
        self._move_highlight(clicked)
        self.selected.emit(index, clicked.text())

    def _move_highlight(self, button, instant=False):
        global_pos = button.mapToGlobal(button.rect().topLeft())
        local_pos = self.mapFromGlobal(global_pos)
        rect = QRect(local_pos, button.size())

        if instant:
            self.highlight.setGeometry(rect)
        else:
            self.anim.stop()
            self.anim.setStartValue(self.highlight.geometry())
            self.anim.setEndValue(rect)
            self.anim.start()

    def set_selected(self, index: int):
        if 0 <= index < len(self.buttons):
            self.buttons[index].click()

    def get_selected_label(self):
        for btn in self.buttons:
            if btn.isChecked():
                return btn.text()
        return None


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App with AnimatedNavBar")
        self.resize(600, 300)

        self.layout = QVBoxLayout(self)

        self.navbar = AnimatedNavBar(["Home", "Profile", "Settings", "Logout"])
        self.layout.addWidget(self.navbar)

        self.label = QLabel("Selected: Home", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.label)

        self.navbar.selected.connect(self.update_label)

    def update_label(self, index, label):
        self.label.setText(f"Selected: {label}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())