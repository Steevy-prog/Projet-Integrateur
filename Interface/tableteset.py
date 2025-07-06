import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)

class TestTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Table Headers")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(1, 5)  # 1 row, 5 columns
        self.table.setHorizontalHeaderLabels(['ID', 'Type', 'Related Product', 'Time', 'Status'])

        # Add sample data
        self.table.setItem(0, 0, QTableWidgetItem("INQ001"))
        self.table.setItem(0, 1, QTableWidgetItem("Support"))
        self.table.setItem(0, 2, QTableWidgetItem("RAM 16GB"))
        self.table.setItem(0, 3, QTableWidgetItem("06/30 15:30"))
        self.table.setItem(0, 4, QTableWidgetItem("Open"))

        # Ensure headers are visible and styled
        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestTable()
    window.show()
    sys.exit(app.exec())