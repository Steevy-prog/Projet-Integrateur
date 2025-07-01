import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import QRect

class StorageCell(QFrame):
    def __init__(self, cell_id, status="Empty", is_selected=False, is_occupied=False):
        super().__init__()
        self.cell_id = cell_id
        self.status = status
        self.is_selected = is_selected
        self.is_occupied = is_occupied
        
        self.setFixedSize(140, 120)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Cell ID label
        id_label = QLabel(self.cell_id)
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Status label
        status_label = QLabel(self.status)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setFont(QFont("Arial", 10))
        
        layout.addWidget(id_label)
        layout.addWidget(status_label)
        
        self.setLayout(layout)
        
        # Set style based on state
        if self.is_occupied:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e6e6ff;
                    border: 2px solid #8080ff;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333333;
                    background: transparent;
                }
            """)
        elif self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e6f3ff;
                    border: 3px solid #4da6ff;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333333;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f0f8f0;
                    border: 2px solid #b3d9b3;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333333;
                    background: transparent;
                }
            """)

class WarehouseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("Cellule d'Entreposage (2D View)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333333; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Aisle headers
        aisle_layout = QHBoxLayout()
        aisle_layout.setSpacing(20)
        
        # Empty space for row labels
        aisle_layout.addWidget(QLabel(""))
        
        # Aisle labels
        aisles = ["Aisle A", "Aisle B", "Aisle C", "Aisle D"]
        for aisle in aisles:
            aisle_label = QLabel(aisle)
            aisle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            aisle_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            aisle_label.setStyleSheet("color: #555555; margin-bottom: 10px;")
            aisle_layout.addWidget(aisle_label)
        
        main_layout.addLayout(aisle_layout)
        
        # Storage grid
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(15)
        
        # Row 1
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)
        
        row1_label = QLabel("Row 1")
        row1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row1_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        row1_label.setStyleSheet("color: #555555;")
        row1_label.setFixedWidth(80)
        row1_layout.addWidget(row1_label)
        
        row1_layout.addWidget(StorageCell("A1-3", "Empty"))
        row1_layout.addWidget(StorageCell("B1-3", "Empty"))
        row1_layout.addWidget(StorageCell("C1-2", "Empty"))
        row1_layout.addWidget(StorageCell("D1-2", "Empty"))
        
        grid_layout.addLayout(row1_layout)
        
        # Row 2
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)
        
        row2_label = QLabel("Row 2")
        row2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row2_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        row2_label.setStyleSheet("color: #555555;")
        row2_label.setFixedWidth(80)
        row2_layout.addWidget(row2_label)
        
        row2_layout.addWidget(StorageCell("A2-3", "Empty"))
        row2_layout.addWidget(StorageCell("B2-3", "Empty", is_selected=True))  # Selected cell
        row2_layout.addWidget(StorageCell("C2-2", "Empty"))
        row2_layout.addWidget(StorageCell("D2-2", "Empty"))
        
        grid_layout.addLayout(row2_layout)
        
        # Row 3
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(20)
        
        row3_label = QLabel("Row 3")
        row3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row3_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        row3_label.setStyleSheet("color: #555555;")
        row3_label.setFixedWidth(80)
        row3_layout.addWidget(row3_label)
        
        row3_layout.addWidget(StorageCell("A3-3", "200x", is_occupied=True))  # Occupied cell
        row3_layout.addWidget(StorageCell("B3-3", "Empty"))
        row3_layout.addWidget(StorageCell("C3-2", "Empty"))
        row3_layout.addWidget(StorageCell("D3-2", "Empty"))
        
        grid_layout.addLayout(row3_layout)
        
        main_layout.addLayout(grid_layout)
        
        # Add stretch to center content
        main_layout.addStretch()
        
        self.setLayout(main_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Storage Layout")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create and set the central widget
        warehouse_widget = WarehouseWidget()
        self.setCentralWidget(warehouse_widget)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f8f8;
            }
            QWidget {
                background-color: #f8f8f8;
            }
        """)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()