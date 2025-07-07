import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
import datetime
import random

class WorkerData:
    """Data generator and manager for warehouse worker operations"""

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        # Products data
        products = [
            ("P001", "Laptop Dell XPS", "Electronics", "Dell", 1500, "A1-15", 45),
            ("P002", "Office Chair", "Furniture", "Herman Miller", 350, "B2-08", 12),
            ("P003", "Smartphone iPhone", "Electronics", "Apple", 800, "A2-22", 78),
            ("P004", "Desk Lamp", "Furniture", "IKEA", 45, "C1-05", 156),
            ("P005", "Wireless Mouse", "Electronics", "Logitech", 25, "A1-33", 234),
            ("P006", "Monitor 24\"", "Electronics", "Samsung", 250, "A2-18", 67),
            ("P007", "Standing Desk", "Furniture", "Varidesk", 400, "B1-12", 23),
            ("P008", "Keyboard Mechanical", "Electronics", "Corsair", 120, "A1-27", 89),
            ("P009", "Bookshelf", "Furniture", "IKEA", 80, "C2-09", 45),
            ("P010", "Tablet iPad", "Electronics", "Apple", 600, "A2-31", 56)
        ]

        self.products_df = pd.DataFrame(products,
                                      columns=['ID', 'Name', 'Category', 'Brand', 'Value', 'Location', 'Stock'])

        # Expedition tasks (orders to be picked and packed)
        self.expedition_tasks = []
        priorities = ['High', 'Medium', 'Low']
        statuses = ['Pending', 'In Progress', 'Completed']
        
        for i in range(15):
            task_items = random.sample(products, random.randint(1, 4))
            total_items = sum([random.randint(1, 5) for _ in task_items])
            
            self.expedition_tasks.append({
                'Order_ID': f'WO{i+1:03d}',
                'Priority': random.choice(priorities),
                'Status': random.choice(statuses),
                'Items_Count': total_items,
                'Due_Time': datetime.datetime.now() + datetime.timedelta(hours=random.randint(1, 8)),
                'Assigned_Worker': 'Current Worker' if random.random() > 0.3 else 'Other Worker',
                'Items': task_items,
                'Customer': f'Customer_{i+1:02d}',
                'Estimated_Time': random.randint(15, 90)  # minutes
            })

        # Product movement tracking
        self.movement_history = []
        movement_types = ['Pick', 'Pack', 'Move', 'Count']
        
        for i in range(50):
            product = random.choice(products)
            self.movement_history.append({
                'Timestamp': datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 24)),
                'Product_ID': product[0],
                'Product_Name': product[1],
                'Movement_Type': random.choice(movement_types),
                'Quantity': random.randint(1, 10),
                'From_Location': product[5],
                'To_Location': product[5] if random.random() > 0.3 else f"{random.choice(['A1', 'A2', 'B1', 'B2'])}-{random.randint(10, 35):02d}",
                'Worker': 'Current Worker' if random.random() > 0.4 else f'Worker_{random.randint(1, 5)}'
            })

        # Exception reports
        self.exceptions = []
        exception_types = ['Product Not Found', 'Damaged Item', 'Quantity Mismatch', 'Wrong Location']
        
        for i in range(8):
            product = random.choice(products)
            self.exceptions.append({
                'ID': f'EX{i+1:03d}',
                'Type': random.choice(exception_types),
                'Product_ID': product[0],
                'Product_Name': product[1],
                'Location': product[5],
                'Reported_Time': datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 12)),
                'Status': random.choice(['Open', 'In Review', 'Resolved']),
                'Description': f'Issue with {product[1]} at location {product[5]}'
            })

class TaskCard(QFrame):
    """Card widget for displaying individual tasks"""
    
    task_selected = pyqtSignal(dict)
    
    def __init__(self, task_data, card_type="expedition"):
        super().__init__()
        self.task_data = task_data
        self.card_type = card_type
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(120)
        
        # Color coding based on priority or status
        if self.card_type == "expedition":
            color = self.get_priority_color(self.task_data['Priority'])
        else:
            color = "#38A169"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border: 2px solid {color};
            }}
        """)

        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        order_label = QLabel(self.task_data['Order_ID'])
        order_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        
        if self.card_type == "expedition":
            priority_label = QLabel(self.task_data['Priority'])
            priority_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")
            header_layout.addWidget(order_label)
            header_layout.addStretch()
            header_layout.addWidget(priority_label)
        else:
            header_layout.addWidget(order_label)
            header_layout.addStretch()

        # Details
        if self.card_type == "expedition":
            details_text = f"Items: {self.task_data['Items_Count']} | Est. Time: {self.task_data['Estimated_Time']}min"
            due_text = f"Due: {self.task_data['Due_Time'].strftime('%H:%M')}"
        else:
            details_text = f"Customer: {self.task_data.get('Customer', 'N/A')}"
            due_text = f"Status: {self.task_data.get('Status', 'Pending')}"
            
        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 13px; color: #666;")
        
        due_label = QLabel(due_text)
        due_label.setStyleSheet("font-size: 13px; color: #666;")

        # Action button
        action_btn = QPushButton("View Details" if self.card_type == "expedition" else "Start Task")
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        action_btn.clicked.connect(self.on_action_clicked)

        layout.addLayout(header_layout)
        layout.addWidget(details_label)
        layout.addWidget(due_label)
        layout.addStretch()
        layout.addWidget(action_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def get_priority_color(self, priority):
        colors = {
            'High': '#E53E3E',
            'Medium': '#E77E23', 
            'Low': '#38A169'
        }
        return colors.get(priority, '#38A169')

    def on_action_clicked(self):
        self.task_selected.emit(self.task_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.task_selected.emit(self.task_data)

class ExpeditionManagementWidget(QWidget):
    """Widget for managing expedition tasks (picking and packing)"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Expedition Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")

        refresh_btn = QPushButton("Refresh Tasks")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        # Quick stats
        stats_layout = QHBoxLayout()
        
        pending_tasks = len([t for t in self.data.expedition_tasks if t['Status'] == 'Pending'])
        in_progress_tasks = len([t for t in self.data.expedition_tasks if t['Status'] == 'In Progress'])
        completed_today = len([t for t in self.data.expedition_tasks if t['Status'] == 'Completed'])
        
        stats_layout.addWidget(self.create_stat_card("Pending", pending_tasks, "#E77E23"))
        stats_layout.addWidget(self.create_stat_card("In Progress", in_progress_tasks, "#006775"))
        stats_layout.addWidget(self.create_stat_card("Completed", completed_today, "#38A169"))

        # Task sections
        sections_layout = QHBoxLayout()
        
        # High Priority Tasks
        high_priority_section = self.create_task_section("High Priority", 
            [t for t in self.data.expedition_tasks if t['Priority'] == 'High' and t['Status'] != 'Completed'])
        
        # My Current Tasks
        my_tasks_section = self.create_task_section("My Current Tasks",
            [t for t in self.data.expedition_tasks if t['Assigned_Worker'] == 'Current Worker' and t['Status'] != 'Completed'])
        
        sections_layout.addWidget(high_priority_section)
        sections_layout.addWidget(my_tasks_section)

        layout.addLayout(header_layout)
        layout.addLayout(stats_layout)
        layout.addLayout(sections_layout)
        
        self.setLayout(layout)

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666; font-weight: bold;")
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card

    def create_task_section(self, title, tasks):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Scrollable task list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(400)

        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)

        for task in tasks[:5]:  # Show top 5 tasks
            task_card = TaskCard(task, "expedition")
            task_card.task_selected.connect(self.on_task_selected)
            task_layout.addWidget(task_card)

        if not tasks:
            no_tasks_label = QLabel("No tasks available")
            no_tasks_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            task_layout.addWidget(no_tasks_label)

        task_layout.addStretch()
        scroll_area.setWidget(task_widget)
        layout.addWidget(scroll_area)
        
        section.setLayout(layout)
        return section

    def on_task_selected(self, task_data):
        # Open task detail dialog
        dialog = TaskDetailDialog(task_data, self)
        dialog.exec_()

class ProductMovementTrackingWidget(QWidget):
    """Widget for tracking product movements and location updates"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Product Movement Tracking")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        
        new_movement_btn = QPushButton("Record Movement")
        new_movement_btn.setStyleSheet("""
            QPushButton {
                background-color: #38A169;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        new_movement_btn.clicked.connect(self.record_new_movement)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_movement_btn)

        # Quick search
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Product:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter product ID or name...")
        self.search_input.textChanged.connect(self.filter_movements)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        # Movement types filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All', 'Pick', 'Pack', 'Move', 'Count'])
        self.type_combo.currentTextChanged.connect(self.filter_movements)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.type_combo)
        filter_layout.addStretch()

        # Recent movements table
        self.movements_table = self.create_movements_table()

        layout.addLayout(header_layout)
        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.movements_table)
        
        self.setLayout(layout)

    def create_movements_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['Time', 'Product', 'Type', 'Quantity', 'From', 'To', 'Worker'])
        
        # Sort movements by timestamp (most recent first)
        sorted_movements = sorted(self.data.movement_history, 
                                key=lambda x: x['Timestamp'], reverse=True)
        
        table.setRowCount(len(sorted_movements))
        
        for i, movement in enumerate(sorted_movements):
            table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M')))
            table.setItem(i, 1, QTableWidgetItem(movement['Product_Name'][:25] + '...' if len(movement['Product_Name']) > 25 else movement['Product_Name']))
            
            # Color code movement types
            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_colors = {
                'Pick': '#E77E23',
                'Pack': '#38A169', 
                'Move': '#006775',
                'Count': '#9C27B0'
            }
            type_item.setBackground(QColor(type_colors.get(movement['Movement_Type'], '#D3DCE0')))
            table.setItem(i, 2, type_item)
            
            table.setItem(i, 3, QTableWidgetItem(str(movement['Quantity'])))
            table.setItem(i, 4, QTableWidgetItem(movement['From_Location']))
            table.setItem(i, 5, QTableWidgetItem(movement['To_Location']))
            
            worker_item = QTableWidgetItem(movement['Worker'])
            if movement['Worker'] == 'Current Worker':
                worker_item.setBackground(QColor('#E8F5E8'))
            table.setItem(i, 6, worker_item)

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #D3DCE0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #D3DCE0;
                font-weight: bold;
            }
        """)
        
        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        
        return table

    def filter_movements(self):
        search_text = self.search_input.text().lower()
        movement_type = self.type_combo.currentText()
        
        # Filter data based on search and type
        filtered_movements = []
        for movement in self.data.movement_history:
            # Check search filter
            if search_text and search_text not in movement['Product_Name'].lower() and search_text not in movement['Product_ID'].lower():
                continue
                
            # Check type filter
            if movement_type != 'All' and movement['Movement_Type'] != movement_type:
                continue
                
            filtered_movements.append(movement)
        
        # Update table with filtered data
        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        sorted_movements = sorted(movements, key=lambda x: x['Timestamp'], reverse=True)
        self.movements_table.setRowCount(len(sorted_movements))
        
        for i, movement in enumerate(sorted_movements):
            self.movements_table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M')))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement['Product_Name'][:25] + '...' if len(movement['Product_Name']) > 25 else movement['Product_Name']))
            
            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_colors = {
                'Pick': '#E77E23',
                'Pack': '#38A169', 
                'Move': '#006775',
                'Count': '#9C27B0'
            }
            type_item.setBackground(QColor(type_colors.get(movement['Movement_Type'], '#D3DCE0')))
            self.movements_table.setItem(i, 2, type_item)
            
            self.movements_table.setItem(i, 3, QTableWidgetItem(str(movement['Quantity'])))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement['From_Location']))
            self.movements_table.setItem(i, 5, QTableWidgetItem(movement['To_Location']))
            
            worker_item = QTableWidgetItem(movement['Worker'])
            if movement['Worker'] == 'Current Worker':
                worker_item.setBackground(QColor('#E8F5E8'))
            self.movements_table.setItem(i, 6, worker_item)

    def record_new_movement(self):
        dialog = NewMovementDialog(self.data, self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the movements table
            self.movements_table = self.create_movements_table()
            self.layout().replaceWidget(self.layout().itemAt(-1).widget(), self.movements_table)

class ExceptionReportsWidget(QWidget):
    """Widget for viewing and managing exception reports"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Exception Reports")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        
        report_exception_btn = QPushButton("Report Exception")
        report_exception_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        report_exception_btn.clicked.connect(self.report_new_exception)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(report_exception_btn)

        # Exception stats
        stats_layout = QHBoxLayout()
        
        open_exceptions = len([e for e in self.data.exceptions if e['Status'] == 'Open'])
        in_review = len([e for e in self.data.exceptions if e['Status'] == 'In Review'])
        resolved_today = len([e for e in self.data.exceptions if e['Status'] == 'Resolved'])
        
        stats_layout.addWidget(self.create_exception_stat_card("Open", open_exceptions, "#E53E3E"))
        stats_layout.addWidget(self.create_exception_stat_card("In Review", in_review, "#E77E23"))
        stats_layout.addWidget(self.create_exception_stat_card("Resolved", resolved_today, "#38A169"))

        # Exceptions table
        self.exceptions_table = self.create_exceptions_table()

        layout.addLayout(header_layout)
        layout.addLayout(stats_layout)
        layout.addWidget(self.exceptions_table)
        
        self.setLayout(layout)

    def create_exception_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #D3DCE0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666; font-weight: bold;")
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card

    def create_exceptions_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID', 'Type', 'Product', 'Location', 'Time', 'Status'])
        
        # Sort exceptions by time (most recent first)
        sorted_exceptions = sorted(self.data.exceptions, 
                                 key=lambda x: x['Reported_Time'], reverse=True)
        
        table.setRowCount(len(sorted_exceptions))
        
        for i, exception in enumerate(sorted_exceptions):
            table.setItem(i, 0, QTableWidgetItem(exception['ID']))
            table.setItem(i, 1, QTableWidgetItem(exception['Type']))
            table.setItem(i, 2, QTableWidgetItem(exception['Product_Name'][:20] + '...' if len(exception['Product_Name']) > 20 else exception['Product_Name']))
            table.setItem(i, 3, QTableWidgetItem(exception['Location']))
            table.setItem(i, 4, QTableWidgetItem(exception['Reported_Time'].strftime('%m/%d %H:%M')))
            
            # Color code status
            status_item = QTableWidgetItem(exception['Status'])
            status_colors = {
                'Open': '#FFEBEE',
                'In Review': '#FFF3E0',
                'Resolved': '#E8F5E8'
            }
            status_item.setBackground(QColor(status_colors.get(exception['Status'], '#f5f5f5')))
            table.setItem(i, 5, status_item)

        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #D3DCE0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #D3DCE0;
                font-weight: bold;
            }
        """)
        
        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        table.cellDoubleClicked.connect(self.view_exception_details)
        
        return table

    def view_exception_details(self, row, column):
        exception_id = self.exceptions_table.item(row, 0).text()
        exception_data = next((e for e in self.data.exceptions if e['ID'] == exception_id), None)
        
        if exception_data:
            dialog = ExceptionDetailDialog(exception_data, self)
            dialog.exec_()

    def report_new_exception(self):
        dialog = NewExceptionDialog(self.data, self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the exceptions table
            self.exceptions_table = self.create_exceptions_table()
            self.layout().replaceWidget(self.layout().itemAt(-1).widget(), self.exceptions_table)

class WorkerMainDashboard(QWidget):
    """Main dashboard widget for warehouse workers"""

    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Welcome header
        header_layout = QHBoxLayout()
        welcome_label = QLabel("Warehouse Worker Dashboard")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")

        time_label = QLabel(f"Today: {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        time_label.setStyleSheet("font-size: 14px; color: #666;")

        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        # Quick stats
        stats_layout = QHBoxLayout()

        my_pending_tasks = len([t for t in self.data.expedition_tasks if t['Assigned_Worker'] == 'Current Worker' and t['Status'] == 'Pending'])
        completed_today = len([t for t in self.data.expedition_tasks if t['Assigned_Worker'] == 'Current Worker' and t['Status'] == 'Completed'])
        my_movements = len([m for m in self.data.movement_history if m['Worker'] == 'Current Worker'])
        open_exceptions = len([e for e in self.data.exceptions if e['Status'] == 'Open'])

        stats_layout.addWidget(self.create_dashboard_card("My Pending Tasks", my_pending_tasks, "#E77E23", "Tasks assigned to me"))
        stats_layout.addWidget(self.create_dashboard_card("Completed Today", completed_today, "#38A169", "Tasks finished today"))
        stats_layout.addWidget(self.create_dashboard_card("My Movements", my_movements, "#006775", "Product movements logged"))
        stats_layout.addWidget(self.create_dashboard_card("Open Exceptions", open_exceptions, "#E53E3E", "Issues requiring attention"))

        # Quick actions
        quick_actions_group = QGroupBox("Quick Actions")
        quick_actions_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; margin-top: 10px; }"
                                         "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }"
                                         "QGroupBox { border: 1px solid #D3DCE0; border-radius: 8px; padding-top: 20px; }")
        quick_actions_layout = QHBoxLayout()

        pick_pack_btn = QPushButton("View Pick/Pack Tasks")
        pick_pack_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        pick_pack_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.expedition_widget))

        record_movement_btn = QPushButton("Record New Movement")
        record_movement_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        record_movement_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.movement_widget))

        report_exception_btn = QPushButton("Report an Exception")
        report_exception_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        report_exception_btn.clicked.connect(lambda: self.main_window.navigate_to_widget(self.main_window.exception_widget))

        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #555;
            }
            QPushButton:hover {
                background-color: #D3DCE0;
                border: 1px solid #c0c0c0;
            }
        """
        pick_pack_btn.setStyleSheet(button_style)
        record_movement_btn.setStyleSheet(button_style)
        report_exception_btn.setStyleSheet(button_style)

        quick_actions_layout.addWidget(pick_pack_btn)
        quick_actions_layout.addWidget(record_movement_btn)
        quick_actions_layout.addWidget(report_exception_btn)
        quick_actions_group.setLayout(quick_actions_layout)

        # Recent activities (simplified - showing latest 5 movements)
        recent_activity_group = QGroupBox("Recent Activities")
        recent_activity_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; margin-top: 10px; }"
                                          "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }"
                                          "QGroupBox { border: 1px solid #D3DCE0; border-radius: 8px; padding-top: 20px; }")
        recent_activity_layout = QVBoxLayout()

        latest_movements = sorted(self.data.movement_history, key=lambda x: x['Timestamp'], reverse=True)[:5]
        if latest_movements:
            for movement in latest_movements:
                activity_label = QLabel(f"- {movement['Timestamp'].strftime('%H:%M')} | {movement['Movement_Type']} of {movement['Quantity']}x {movement['Product_Name']} by {movement['Worker']}")
                activity_label.setStyleSheet("font-size: 13px; color: #444; padding: 2px 0;")
                recent_activity_layout.addWidget(activity_label)
        else:
            no_activity_label = QLabel("No recent activities.")
            no_activity_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
            recent_activity_layout.addWidget(no_activity_label)

        recent_activity_group.setLayout(recent_activity_layout)

        layout.addLayout(header_layout)
        layout.addLayout(stats_layout)
        layout.addWidget(quick_actions_group)
        layout.addWidget(recent_activity_group)
        layout.addStretch() # Pushes content to the top

        self.setLayout(layout)

    def create_dashboard_card(self, title, value, color, description):
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #D3DCE0;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")

        description_label = QLabel(description)
        description_label.setStyleSheet("font-size: 10px; color: #999;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        card.setLayout(layout)

        return card

class TaskDetailDialog(QDialog):
    """Dialog to display details of a selected task"""
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setWindowTitle(f"Task Details: {self.task_data['Order_ID']}")
        self.setFixedSize(450, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                margin-bottom: 5px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #000;
                margin-bottom: 15px;
            }
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QListWidget {
                border: 1px solid #D3DCE0;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)

        # Title
        title_label = QLabel(f"Order: {self.task_data['Order_ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        # Details
        details_form_layout = QFormLayout()
        details_form_layout.addRow("Priority:", QLabel(self.task_data['Priority']))
        details_form_layout.addRow("Status:", QLabel(self.task_data['Status']))
        details_form_layout.addRow("Items Count:", QLabel(str(self.task_data['Items_Count'])))
        details_form_layout.addRow("Due Time:", QLabel(self.task_data['Due_Time'].strftime('%Y-%m-%d %H:%M')))
        details_form_layout.addRow("Estimated Time:", QLabel(f"{self.task_data['Estimated_Time']} minutes"))
        details_form_layout.addRow("Assigned Worker:", QLabel(self.task_data['Assigned_Worker']))
        details_form_layout.addRow("Customer:", QLabel(self.task_data['Customer']))
        layout.addLayout(details_form_layout)

        # Items list
        items_label = QLabel("Items to Pick:")
        items_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(items_label)

        items_list_widget = QListWidget()
        for item_data in self.task_data['Items']:
            list_item = QListWidgetItem(f"{item_data[1]} ({item_data[0]}) - Loc: {item_data[5]}")
            items_list_widget.addItem(list_item)
        items_list_widget.setFixedSize(400, 150)
        layout.addWidget(items_list_widget)

        # Action buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

class NewMovementDialog(QDialog):
    """Dialog to record a new product movement"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Record New Product Movement")
        self.setFixedSize(400, 350)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #38A169;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton#cancelButton {
                background-color: #E53E3E;
            }
            QPushButton#cancelButton:hover {
                background-color: #d32f2f;
            }
        """)

        # Product selection
        product_names = [p[1] for p in self.data.products_df.values]
        self.product_combo = QComboBox()
        self.product_combo.addItems(product_names)
        layout.addRow("Product:", self.product_combo)

        # Movement Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Pick', 'Pack', 'Move', 'Count'])
        layout.addRow("Movement Type:", self.type_combo)

        # Quantity
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 1000)
        self.quantity_spinbox.setValue(1)
        layout.addRow("Quantity:", self.quantity_spinbox)

        # From Location
        self.from_location_input = QLineEdit()
        self.from_location_input.setPlaceholderText("e.g., A1-15")
        layout.addRow("From Location:", self.from_location_input)

        # To Location
        self.to_location_input = QLineEdit()
        self.to_location_input.setPlaceholderText("e.g., B2-08 (optional)")
        layout.addRow("To Location:", self.to_location_input)

        # Worker
        self.worker_input = QLineEdit("Current Worker")
        self.worker_input.setDisabled(True)
        layout.addRow("Worker:", self.worker_input)

        # Buttons
        button_box = QHBoxLayout()
        submit_btn = QPushButton("Record Movement")
        submit_btn.clicked.connect(self.record_movement)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        button_box.addStretch()
        button_box.addWidget(submit_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)

        self.setLayout(layout)

    def record_movement(self):
        product_name = self.product_combo.currentText()
        product_id = self.data.products_df[self.data.products_df['Name'] == product_name]['ID'].iloc[0]
        movement_type = self.type_combo.currentText()
        quantity = self.quantity_spinbox.value()
        from_location = self.from_location_input.text()
        to_location = self.to_location_input.text() if self.to_location_input.text() else from_location # Default to_location
        worker = self.worker_input.text()

        if not from_location:
            QMessageBox.warning(self, "Input Error", "Please provide a 'From Location'.")
            return

        new_movement = {
            'Timestamp': datetime.datetime.now(),
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Movement_Type': movement_type,
            'Quantity': quantity,
            'From_Location': from_location,
            'To_Location': to_location,
            'Worker': worker
        }
        self.data.movement_history.append(new_movement)
        QMessageBox.information(self, "Success", "Product movement recorded successfully!")
        self.accept()

class ExceptionDetailDialog(QDialog):
    """Dialog to display and manage exception report details"""
    def __init__(self, exception_data, parent=None):
        super().__init__(parent)
        self.exception_data = exception_data
        self.setWindowTitle(f"Exception Details: {self.exception_data['ID']}")
        self.setFixedSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                margin-bottom: 5px;
            }
            QLabel.title {
                font-size: 18px;
                font-weight: bold;
                color: #000;
                margin-bottom: 15px;
            }
            QTextEdit {
                border: 1px solid #D3DCE0;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #006775;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#resolveButton {
                background-color: #38A169;
            }
            QPushButton#resolveButton:hover {
                background-color: #43A047;
            }
        """)

        # Title
        title_label = QLabel(f"Exception: {self.exception_data['ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        # Details
        details_form_layout = QFormLayout()
        details_form_layout.addRow("Type:", QLabel(self.exception_data['Type']))
        details_form_layout.addRow("Product:", QLabel(f"{self.exception_data['Product_Name']} ({self.exception_data['Product_ID']})"))
        details_form_layout.addRow("Location:", QLabel(self.exception_data['Location']))
        details_form_layout.addRow("Reported Time:", QLabel(self.exception_data['Reported_Time'].strftime('%Y-%m-%d %H:%M')))
        details_form_layout.addRow("Status:", QLabel(self.exception_data['Status']))
        layout.addLayout(details_form_layout)

        # Description
        description_label = QLabel("Description:")
        description_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(description_label)
        description_text = QTextEdit()
        description_text.setPlainText(self.exception_data['Description'])
        description_text.setReadOnly(True)
        layout.addWidget(description_text)

        # Action buttons
        button_layout = QHBoxLayout()
        if self.exception_data['Status'] != 'Resolved':
            resolve_btn = QPushButton("Mark as Resolved")
            resolve_btn.setObjectName("resolveButton")
            resolve_btn.clicked.connect(self.resolve_exception)
            button_layout.addWidget(resolve_btn)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def resolve_exception(self):
        reply = QMessageBox.question(self, "Resolve Exception",
                                     "Are you sure you want to mark this exception as 'Resolved'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.exception_data['Status'] = 'Resolved'
            QMessageBox.information(self, "Success", "Exception marked as resolved.")
            self.accept()

class NewExceptionDialog(QDialog):
    """Dialog to report a new exception"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Report New Exception")
        self.setFixedSize(400, 450)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton#cancelButton {
                background-color: #9E9E9E;
            }
            QPushButton#cancelButton:hover {
                background-color: #757575;
            }
        """)

        # Exception Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Product Not Found', 'Damaged Item', 'Quantity Mismatch', 'Wrong Location', 'Other'])
        layout.addRow("Exception Type:", self.type_combo)

        # Product selection
        product_names = [p[1] for p in self.data.products_df.values]
        self.product_combo = QComboBox()
        self.product_combo.addItems(product_names)
        layout.addRow("Product:", self.product_combo)

        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., A1-15")
        layout.addRow("Location:", self.location_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Provide a detailed description of the exception...")
        self.description_input.setFixedHeight(120)
        layout.addRow("Description:", self.description_input)

        # Buttons
        button_box = QHBoxLayout()
        report_btn = QPushButton("Report Exception")
        report_btn.clicked.connect(self.report_exception)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        button_box.addStretch()
        button_box.addWidget(report_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)

        self.setLayout(layout)

    def report_exception(self):
        exception_type = self.type_combo.currentText()
        product_name = self.product_combo.currentText()
        product_id = self.data.products_df[self.data.products_df['Name'] == product_name]['ID'].iloc[0]
        location = self.location_input.text()
        description = self.description_input.toPlainText()

        if not location or not description:
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields (Location, Description).")
            return

        new_exception = {
            'ID': f'EX{len(self.data.exceptions) + 1:03d}',
            'Type': exception_type,
            'Product_ID': product_id,
            'Product_Name': product_name,
            'Location': location,
            'Reported_Time': datetime.datetime.now(),
            'Status': 'Open',
            'Description': description
        }
        self.data.exceptions.append(new_exception)
        QMessageBox.information(self, "Success", "Exception reported successfully!")
        self.accept()

class MainWindow(QMainWindow):
    """Main application window with navigation"""
    def __init__(self):
        super().__init__()
        self.data = WorkerData()
        self.setWindowTitle("Warehouse Worker Operations Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.create_sidebar()
        self.create_content_area()

        self.apply_global_styles()

        # Set initial view
        self.navigate_to_widget(self.dashboard_widget)

    def apply_global_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #333;
                color: white;
            }
            QMenuBar::item {
                background-color: #333;
                color: white;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QStatusBar {
                background-color: #eee;
                color: #333;
            }
        """)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50; /* Darker blue-grey */
                color: white;
                border-right: 1px solid #1a242f;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                padding: 15px 10px;
                text-align: left;
                font-size: 16px;
                border-bottom: 1px solid #34495e;
            }
            QPushButton:hover {
                background-color: #34495e; /* Slightly lighter on hover */
            }
            QPushButton:checked {
                background-color: #1abc9c; /* Teal for active state */
                font-weight: bold;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo/Title
        logo_label = QLabel("Warehouse Ops")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px 0; background-color: #34495e;")
        sidebar_layout.addWidget(logo_label)

        # Navigation buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.expedition_btn = QPushButton("Expedition Management")
        self.movement_btn = QPushButton("Product Movements")
        self.exceptions_btn = QPushButton("Exception Reports")

        self.dashboard_btn.setCheckable(True)
        self.expedition_btn.setCheckable(True)
        self.movement_btn.setCheckable(True)
        self.exceptions_btn.setCheckable(True)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.dashboard_btn)
        self.button_group.addButton(self.expedition_btn)
        self.button_group.addButton(self.movement_btn)
        self.button_group.addButton(self.exceptions_btn)

        self.dashboard_btn.clicked.connect(lambda: self.navigate_to_widget(self.dashboard_widget))
        self.expedition_btn.clicked.connect(lambda: self.navigate_to_widget(self.expedition_widget))
        self.movement_btn.clicked.connect(lambda: self.navigate_to_widget(self.movement_widget))
        self.exceptions_btn.clicked.connect(lambda: self.navigate_to_widget(self.exception_widget))

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.expedition_btn)
        sidebar_layout.addWidget(self.movement_btn)
        sidebar_layout.addWidget(self.exceptions_btn)
        sidebar_layout.addStretch()

        self.main_layout.addWidget(self.sidebar)

    def create_content_area(self):
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f5f5; padding: 20px;")

        self.dashboard_widget = WorkerMainDashboard(self.data, self)
        self.expedition_widget = ExpeditionManagementWidget(self.data)
        self.movement_widget = ProductMovementTrackingWidget(self.data)
        self.exception_widget = ExceptionReportsWidget(self.data)

        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.expedition_widget)
        self.content_stack.addWidget(self.movement_widget)
        self.content_stack.addWidget(self.exception_widget)

        self.main_layout.addWidget(self.content_stack)

    def navigate_to_widget(self, target_widget):
        self.content_stack.setCurrentWidget(target_widget)
        # Uncheck all buttons and then check the corresponding one
        for button in self.button_group.buttons():
            button.setChecked(False)
        if target_widget == self.dashboard_widget:
            self.dashboard_btn.setChecked(True)
        elif target_widget == self.expedition_widget:
            self.expedition_btn.setChecked(True)
        elif target_widget == self.movement_widget:
            self.movement_btn.setChecked(True)
        elif target_widget == self.exception_widget:
            self.exceptions_btn.setChecked(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # A modern style
    main_window = MainWindow()
    main_window.showMaximized() # Start maximized for a better experience
    sys.exit(app.exec_())