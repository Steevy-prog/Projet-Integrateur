from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QPushButton, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MinimalStorageTestWidget(QWidget):
    """Minimal test widget to check if cells appear"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        title = QLabel("Storage Test - Should Show Cells")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Main zones layout
        self.main_zones_layout = QVBoxLayout()
        self.populate_test_zones()
        
        main_widget = QWidget()
        main_widget.setLayout(self.main_zones_layout)
        scroll_area.setWidget(main_widget)
        
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def populate_test_zones(self):
        zones = ['Zone A', 'Zone B']  # Just 2 zones for testing
        cells_per_zone = 6  # Fewer cells for testing
        
        for zone_name in zones:
            print(f"Creating zone: {zone_name}")
            
            # Create group box for zone
            zone_group_box = QGroupBox(zone_name)
            zone_group_box.setStyleSheet("""
                QGroupBox {
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #0000FF;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #F0F0F0;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                }
            """)
            
            # Create grid layout for cells
            grid_layout = QGridLayout()
            grid_layout.setSpacing(5)
            
            # Create cells
            for i in range(cells_per_zone):
                cell_id = f"{zone_name}-{i+1}"
                print(f"Creating cell: {cell_id}")
                
                # Create simple button
                cell_button = QPushButton(cell_id)
                cell_button.setFixedSize(80, 60)
                cell_button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFF00;
                        border: 2px solid #FF0000;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #FFAA00;
                    }
                """)
                cell_button.clicked.connect(lambda checked, cid=cell_id: self.cell_clicked(cid))
                
                # Add to grid (3 columns)
                row = i // 3
                col = i % 3
                grid_layout.addWidget(cell_button, row, col)
                print(f"Added cell {cell_id} to grid at ({row}, {col})")
            
            zone_group_box.setLayout(grid_layout)
            self.main_zones_layout.addWidget(zone_group_box)
            print(f"Added zone {zone_name} to main layout")
        
        print("populate_test_zones completed")

    def cell_clicked(self, cell_id):
        print(f"Cell clicked: {cell_id}")


# Test script to run this widget
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = MinimalStorageTestWidget()
    widget.show()
    widget.resize(400, 300)
    sys.exit(app.exec())