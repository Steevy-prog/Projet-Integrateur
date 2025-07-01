import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import QRect

class BuildingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 900)
        self.setStyleSheet("background-color: #f5f5f5;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Colors
        building_color = QColor(30, 30, 30)
        elevator_shaft_color = QColor(100, 180, 230)
        floor_color = QColor(150, 220, 180)
        floor_divider_color = QColor(100, 150, 200)
        
        # Pens and brushes
        building_brush = QBrush(building_color)
        elevator_brush = QBrush(elevator_shaft_color)
        floor_brush = QBrush(floor_color)
        divider_pen = QPen(floor_divider_color, 3)
        
        # Building dimensions
        building_width = 600
        building_height = 700
        building_x = (self.width() - building_width) // 2
        building_y = 80
        
        # Draw main building structure
        painter.setBrush(building_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Main building body
        main_rect = QRect(building_x, building_y + 200, building_width, building_height - 200)
        painter.drawRoundedRect(main_rect, 15, 15)
        
        # Left tower
        left_tower = QRect(building_x, building_y, 120, 500)
        painter.drawRoundedRect(left_tower, 15, 15)
        
        # Right tower
        right_tower = QRect(building_x + building_width - 120, building_y, 120, 500)
        painter.drawRoundedRect(right_tower, 15, 15)
        
        # Central elevator shaft
        central_shaft_width = 80
        central_shaft_x = building_x + (building_width - central_shaft_width) // 2
        central_shaft = QRect(central_shaft_x, building_y - 50, central_shaft_width, 400)
        painter.drawRoundedRect(central_shaft, 15, 15)
        
        # Draw elevator shafts (blue areas)
        painter.setBrush(elevator_brush)
        
        # Left elevator shaft
        left_elevator = QRect(building_x + 20, building_y + 50, 80, 380)
        painter.drawRoundedRect(left_elevator, 10, 10)
        
        # Central elevator shaft interior
        central_elevator = QRect(central_shaft_x + 10, building_y - 40, 60, 380)
        painter.drawRoundedRect(central_elevator, 10, 10)
        
        # Right elevator shaft
        right_elevator = QRect(building_x + building_width - 100, building_y + 50, 80, 380)
        painter.drawRoundedRect(right_elevator, 10, 10)
        
        # Bottom floor area
        bottom_floor = QRect(building_x + 50, building_y + 450, building_width - 100, 180)
        painter.drawRoundedRect(bottom_floor, 10, 10)
        
        # Draw floor grids
        painter.setBrush(floor_brush)
        
        # Function to draw floor grid
        def draw_floor_grid(x, y, width, height, rows, cols):
            cell_width = width // cols
            cell_height = height // rows
            
            for row in range(rows):
                for col in range(cols):
                    cell_x = x + col * cell_width
                    cell_y = y + row * cell_height
                    cell_rect = QRect(cell_x + 2, cell_y + 2, cell_width - 4, cell_height - 4)
                    painter.drawRoundedRect(cell_rect, 5, 5)
        
        # Left elevator floors
        draw_floor_grid(building_x + 25, building_y + 60, 70, 360, 9, 2)
        
        # Central elevator floors
        draw_floor_grid(central_shaft_x + 15, building_y - 30, 50, 360, 12, 2)
        
        # Right elevator floors
        draw_floor_grid(building_x + building_width - 95, building_y + 60, 70, 360, 9, 2)
        
        # Bottom floor grid
        draw_floor_grid(building_x + 60, building_y + 460, building_width - 120, 160, 4, 8)
        
        # Draw floor dividers
        painter.setPen(divider_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Vertical dividers for left elevator
        left_center_x = building_x + 60
        painter.drawLine(left_center_x, building_y + 60, left_center_x, building_y + 420)
        
        # Vertical dividers for central elevator
        central_center_x = central_shaft_x + 40
        painter.drawLine(central_center_x, building_y - 30, central_center_x, building_y + 330)
        
        # Vertical dividers for right elevator
        right_center_x = building_x + building_width - 60
        painter.drawLine(right_center_x, building_y + 60, right_center_x, building_y + 420)
        
        # Horizontal dividers for bottom floor
        for i in range(1, 8):
            divider_x = building_x + 60 + i * ((building_width - 120) // 8)
            painter.drawLine(divider_x, building_y + 460, divider_x, building_y + 620)
        
        for i in range(1, 4):
            divider_y = building_y + 460 + i * (160 // 4)
            painter.drawLine(building_x + 60, divider_y, building_x + building_width - 60, divider_y)
        
        # Add labels
        painter.setPen(QPen(QColor(200, 80, 80), 2))
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        
        # E1 label
        painter.drawText(building_x + 40, building_y + 250, "E1")
        
        # E0 label
        painter.drawText(central_shaft_x + 25, building_y + 150, "E0")
        
        # E3 label
        painter.drawText(building_x + building_width - 80, building_y + 250, "E3")
        
        # E2 label
        painter.drawText(building_x + building_width // 2 - 10, building_y + 550, "E2")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Building Structure with Elevators")
        self.setGeometry(100, 100, 900, 1000)
        
        # Create and set the central widget
        building_widget = BuildingWidget()
        self.setCentralWidget(building_widget)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
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