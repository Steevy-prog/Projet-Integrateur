
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QTabWidget,
                           QScrollArea, QFrame, QProgressBar, QComboBox,
                           QDateEdit, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import datetime
import random

class WarehouseData:
    """Data generator and manager for warehouse operations"""
    
    def __init__(self):
        self.generate_sample_data()
    
    def generate_sample_data(self):
        # Products data
        products = [
            ("P001", "Laptop Dell XPS", "Electronics", "Dell", 1500),
            ("P002", "Office Chair", "Furniture", "Herman Miller", 350),
            ("P003", "Smartphone iPhone", "Electronics", "Apple", 800),
            ("P004", "Desk Lamp", "Furniture", "IKEA", 45),
            ("P005", "Wireless Mouse", "Electronics", "Logitech", 25),
            ("P006", "Monitor 24\"", "Electronics", "Samsung", 250),
            ("P007", "Standing Desk", "Furniture", "Varidesk", 400),
            ("P008", "Keyboard Mechanical", "Electronics", "Corsair", 120),
            ("P009", "Bookshelf", "Furniture", "IKEA", 80),
            ("P010", "Tablet iPad", "Electronics", "Apple", 600)
        ]
        
        self.products_df = pd.DataFrame(products, 
                                      columns=['ID', 'Name', 'Category', 'Brand', 'Value'])
        
        # Inventory data
        inventory_data = []
        storage_zones = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']
        
        for _, product in self.products_df.iterrows():
            inventory_data.append({
                'Product_ID': product['ID'],
                'Product_Name': product['Name'],
                'Quantity': random.randint(10, 500),
                'Zone': random.choice(storage_zones),
                'Last_Updated': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30)),
                'Min_Stock': random.randint(5, 50),
                'Value': product['Value']
            })
        
        self.inventory_df = pd.DataFrame(inventory_data)
        
        # Reception orders
        reception_data = []
        suppliers = ['Dell Corp', 'Apple Inc', 'IKEA', 'Samsung', 'Logitech']
        statuses = ['Pending', 'In Transit', 'Received', 'Processing']
        
        for i in range(20):
            reception_data.append({
                'Order_ID': f'RO{i+1:03d}',
                'Supplier': random.choice(suppliers),
                'Expected_Date': datetime.date.today() + datetime.timedelta(days=random.randint(-5, 15)),
                'Items_Count': random.randint(1, 10),
                'Status': random.choice(statuses),
                'Total_Value': random.randint(1000, 50000)
            })
        
        self.reception_df = pd.DataFrame(reception_data)
        
        # Expedition orders
        expedition_data = []
        destinations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        
        for i in range(25):
            expedition_data.append({
                'Order_ID': f'EO{i+1:03d}',
                'Destination': random.choice(destinations),
                'Request_Date': datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                'Items_Count': random.randint(1, 8),
                'Status': random.choice(statuses),
                'Total_Value': random.randint(500, 25000)
            })
        
        self.expedition_df = pd.DataFrame(expedition_data)
        
        # Generate time series data for performance metrics
        dates = pd.date_range(start='2024-01-01', end='2024-06-19', freq='D')
        self.daily_metrics = pd.DataFrame({
            'Date': dates,
            'Items_Received': np.random.poisson(50, len(dates)),
            'Items_Shipped': np.random.poisson(45, len(dates)),
            'Storage_Utilization': np.random.uniform(60, 95, len(dates)),
            'Order_Fulfillment_Rate': np.random.uniform(85, 99, len(dates))
        })

class ChartWidget(QWidget):
    """Custom widget for matplotlib charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear_plot(self):
        self.figure.clear()
        self.canvas.draw()

class MetricCard(QFrame):
    """Card widget for displaying key metrics"""
    
    def __init__(self, title, value, subtitle="", color="#4CAF50"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 10px; color: #999;")
            layout.addWidget(subtitle_label)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setSpacing(5)
        
        self.setLayout(layout)

class InventoryWidget(QWidget):
    """Widget for inventory management"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Inventory Overview")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
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
        
        # Metrics cards
        metrics_layout = QHBoxLayout()
        
        total_items = self.data.inventory_df['Quantity'].sum()
        total_value = (self.data.inventory_df['Quantity'] * self.data.inventory_df['Value']).sum()
        low_stock_items = len(self.data.inventory_df[
            self.data.inventory_df['Quantity'] <= self.data.inventory_df['Min_Stock']
        ])
        zones_used = self.data.inventory_df['Zone'].nunique()
        
        metrics_layout.addWidget(MetricCard("Total Items", f"{total_items:,}", "In Stock"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "Inventory Worth"))
        metrics_layout.addWidget(MetricCard("Low Stock", str(low_stock_items), "Items Below Min", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Storage Zones", str(zones_used), "Active Zones"))
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Stock by category pie chart
        category_chart = ChartWidget()
        self.create_category_chart(category_chart)
        
        # Stock levels bar chart
        stock_chart = ChartWidget()
        self.create_stock_levels_chart(stock_chart)
        
        charts_layout.addWidget(category_chart)
        charts_layout.addWidget(stock_chart)
        
        # Inventory table
        table = self.create_inventory_table()
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(table)
        
        self.setLayout(layout)
    
    def create_category_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)
        
        # Group by category
        category_data = []
        for _, product in self.data.products_df.iterrows():
            inventory_item = self.data.inventory_df[
                self.data.inventory_df['Product_ID'] == product['ID']
            ].iloc[0]
            category_data.append({
                'Category': product['Category'],
                'Quantity': inventory_item['Quantity']
            })
        
        category_df = pd.DataFrame(category_data)
        category_summary = category_df.groupby('Category')['Quantity'].sum()
        
        colors = ['#FF9800', '#4CAF50', '#2196F3', '#9C27B0']
        wedges, texts, autotexts = ax.pie(category_summary.values, 
                                         labels=category_summary.index,
                                         autopct='%1.1f%%',
                                         colors=colors[:len(category_summary)])
        
        ax.set_title('Inventory by Category', fontsize=14, fontweight='bold', pad=20)
        chart_widget.canvas.draw()
    
    def create_stock_levels_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)
        
        # Top products by quantity
        top_products = self.data.inventory_df.nlargest(8, 'Quantity')
        
        bars = ax.bar(range(len(top_products)), top_products['Quantity'])
        
        # Color bars based on stock level
        for i, (_, row) in enumerate(top_products.iterrows()):
            if row['Quantity'] <= row['Min_Stock']:
                bars[i].set_color('#F44336')  # Red for low stock
            elif row['Quantity'] <= row['Min_Stock'] * 2:
                bars[i].set_color('#FF9800')  # Orange for medium stock
            else:
                bars[i].set_color('#4CAF50')  # Green for good stock
        
        ax.set_title('Stock Levels - Top Products', fontsize=14, fontweight='bold')
        ax.set_xlabel('Products')
        ax.set_ylabel('Quantity')
        ax.set_xticks(range(len(top_products)))
        ax.set_xticklabels([name[:15] + '...' if len(name) > 15 else name 
                           for name in top_products['Product_Name']], 
                          rotation=45, ha='right')
        
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()
    
    def create_inventory_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.inventory_df))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['Product', 'Quantity', 'Zone', 'Min Stock', 'Status', 'Value'])
        
        for i, (_, row) in enumerate(self.data.inventory_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Product_Name']))
            table.setItem(i, 1, QTableWidgetItem(str(row['Quantity'])))
            table.setItem(i, 2, QTableWidgetItem(row['Zone']))
            table.setItem(i, 3, QTableWidgetItem(str(row['Min_Stock'])))
            
            # Status based on stock level
            if row['Quantity'] <= row['Min_Stock']:
                status = "Low Stock"
                status_item = QTableWidgetItem(status)
                status_item.setBackground(QColor('#FFEBEE'))
            else:
                status = "In Stock"
                status_item = QTableWidgetItem(status)
                status_item.setBackground(QColor('#E8F5E8'))
            
            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Value']:,.2f}"))
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        
        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        
        return table

class OrdersWidget(QWidget):
    """Widget for order management (reception and expedition)"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tab widget for different order types
        tabs = QTabWidget()
        
        # Reception orders tab
        reception_widget = self.create_reception_tab()
        tabs.addTab(reception_widget, "Reception Orders")
        
        # Expedition orders tab
        expedition_widget = self.create_expedition_tab()
        tabs.addTab(expedition_widget, "Expedition Orders")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_reception_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Reception Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        pending_orders = len(self.data.reception_df[self.data.reception_df['Status'] == 'Pending'])
        total_value = self.data.reception_df['Total_Value'].sum()
        avg_items = self.data.reception_df['Items_Count'].mean()
        
        metrics_layout.addWidget(MetricCard("Pending Orders", str(pending_orders), "Awaiting Receipt"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))
        
        # Chart and table
        content_layout = QHBoxLayout()
        
        # Status chart
        status_chart = ChartWidget()
        self.create_status_chart(status_chart, self.data.reception_df, "Reception Orders by Status")
        
        # Orders table
        table = self.create_orders_table(self.data.reception_df)
        
        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table, 2)
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_expedition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header with metrics
        header_layout = QHBoxLayout()
        title = QLabel("Expedition Orders")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        pending_orders = len(self.data.expedition_df[self.data.expedition_df['Status'] == 'Pending'])
        total_value = self.data.expedition_df['Total_Value'].sum()
        avg_items = self.data.expedition_df['Items_Count'].mean()
        
        metrics_layout.addWidget(MetricCard("Pending Orders", str(pending_orders), "Ready to Ship"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "All Orders"))
        metrics_layout.addWidget(MetricCard("Avg Items", f"{avg_items:.1f}", "Per Order"))
        
        # Chart and table
        content_layout = QHBoxLayout()
        
        # Status chart
        status_chart = ChartWidget()
        self.create_status_chart(status_chart, self.data.expedition_df, "Expedition Orders by Status")
        
        # Orders table
        table = self.create_orders_table(self.data.expedition_df, is_expedition=True)
        
        content_layout.addWidget(status_chart, 1)
        content_layout.addWidget(table, 2)
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(content_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_chart(self, chart_widget, df, title):
        ax = chart_widget.figure.add_subplot(111)
        
        status_counts = df['Status'].value_counts()
        colors = ['#4CAF50', '#FF9800', '#2196F3', '#9C27B0']
        
        bars = ax.bar(status_counts.index, status_counts.values, color=colors[:len(status_counts)])
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Orders')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom')
        
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()
    
    def create_orders_table(self, df, is_expedition=False):
        table = QTableWidget()
        table.setRowCount(len(df))
        
        if is_expedition:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Destination', 'Request Date', 'Items', 'Status', 'Value'])
            date_col = 'Request_Date'
            location_col = 'Destination'
        else:
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Order ID', 'Supplier', 'Expected Date', 'Items', 'Status', 'Value'])
            date_col = 'Expected_Date'
            location_col = 'Supplier'
        
        for i, (_, row) in enumerate(df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Order_ID']))
            table.setItem(i, 1, QTableWidgetItem(row[location_col]))
            table.setItem(i, 2, QTableWidgetItem(str(row[date_col])))
            table.setItem(i, 3, QTableWidgetItem(str(row['Items_Count'])))
            
            # Status with color coding
            status_item = QTableWidgetItem(row['Status'])
            if row['Status'] == 'Pending':
                status_item.setBackground(QColor('#FFF3E0'))
            elif row['Status'] == 'Processing':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Received' or row['Status'] == 'In Transit':
                status_item.setBackground(QColor('#E8F5E8'))
            
            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Total_Value']:,.0f}"))
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        
        table.setAlternatingRowColors(True)
        table.resizeColumnsToContents()
        
        return table

class PerformanceWidget(QWidget):
    """Widget for performance metrics and analytics"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Performance Analytics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        # Date range selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        from_date = QDateEdit(QDate.currentDate().addDays(-30))
        from_date.setCalendarPopup(True)
        date_layout.addWidget(from_date)
        
        date_layout.addWidget(QLabel("To:"))
        to_date = QDateEdit(QDate.currentDate())
        to_date.setCalendarPopup(True)
        date_layout.addWidget(to_date)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(date_layout)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        # Calculate KPIs from recent data
        recent_data = self.data.daily_metrics.tail(30)
        avg_received = recent_data['Items_Received'].mean()
        avg_shipped = recent_data['Items_Shipped'].mean()
        avg_utilization = recent_data['Storage_Utilization'].mean()
        avg_fulfillment = recent_data['Order_Fulfillment_Rate'].mean()
        
        kpi_layout.addWidget(MetricCard("Daily Received", f"{avg_received:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Daily Shipped", f"{avg_shipped:.0f}", "Avg Last 30 days"))
        kpi_layout.addWidget(MetricCard("Storage Utilization", f"{avg_utilization:.1f}%", "Current Average"))
        kpi_layout.addWidget(MetricCard("Fulfillment Rate", f"{avg_fulfillment:.1f}%", "Order Success"))
        
        # Charts
        charts_layout = QGridLayout()
        
        # Daily operations trend
        trend_chart = ChartWidget()
        self.create_trend_chart(trend_chart)
        charts_layout.addWidget(trend_chart, 0, 0)
        
        # Storage utilization
        utilization_chart = ChartWidget()
        self.create_utilization_chart(utilization_chart)
        charts_layout.addWidget(utilization_chart, 0, 1)
        
        # Fulfillment rate trend
        fulfillment_chart = ChartWidget()
        self.create_fulfillment_chart(fulfillment_chart)
        charts_layout.addWidget(fulfillment_chart, 1, 0, 1, 2)
        
        layout.addLayout(header_layout)
        layout.addLayout(kpi_layout)
        layout.addLayout(charts_layout)
        
        self.setLayout(layout)
    
    def create_trend_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)
        
        recent_data = self.data.daily_metrics.tail(30)
        
        ax.plot(recent_data['Date'], recent_data['Items_Received'], 
               label='Received', color='#4CAF50', linewidth=2)
        ax.plot(recent_data['Date'], recent_data['Items_Shipped'], 
               label='Shipped', color='#2196F3', linewidth=2)
        
        ax.set_title('Daily Operations Trend (Last 30 Days)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Items Count')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format dates on x-axis
        ax.tick_params(axis='x', rotation=45)
        
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()
    
    def create_utilization_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)
        
        # Storage utilization by zone (simulated)
        zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
        utilization = [85, 72, 91, 68]
        colors = ['#FF5722' if u > 85 else '#FF9800' if u > 75 else '#4CAF50' for u in utilization]
        
        bars = ax.bar(zones, utilization, color=colors)
        
        # Add percentage labels on bars
        for bar, util in zip(bars, utilization):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{util}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Storage Utilization by Zone', fontsize=14, fontweight='bold')
        ax.set_ylabel('Utilization %')
        ax.set_ylim(0, 100)
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Target (80%)')
        ax.legend()
        
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()
    
    def create_fulfillment_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)
        
        # Weekly fulfillment rate
        weekly_data = self.data.daily_metrics.tail(42).groupby(
            self.data.daily_metrics.tail(42)['Date'].dt.isocalendar().week
        ).agg({
            'Order_Fulfillment_Rate': 'mean'
        }).reset_index()
        
        weeks = [f'Week {i}' for i in range(len(weekly_data))]
        
        ax.fill_between(range(len(weekly_data)), 
                       weekly_data['Order_Fulfillment_Rate'], 
                       alpha=0.3, color='#4CAF50')
        ax.plot(range(len(weekly_data)), weekly_data['Order_Fulfillment_Rate'], 
               color='#4CAF50', linewidth=3, marker='o', markersize=6)
        
        ax.set_title('Order Fulfillment Rate Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Fulfillment Rate %')
        ax.set_xticks(range(len(weekly_data)))
        ax.set_xticklabels(weeks, rotation=45)
        ax.set_ylim(80, 100)
        ax.grid(True, alpha=0.3)
        
        # Add target line
        ax.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='Target (95%)')
        ax.legend()
        
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

class WarehouseDashboard(QMainWindow):
    """Main dashboard window"""
    
    def __init__(self):
        super().__init__()
        self.data = WarehouseData()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        self.setWindowTitle("Warehouse Management System - Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
class WarehouseDashboard(QMainWindow):
    """Main dashboard window"""

    def __init__(self):
        super().__init__()
        self.data = WarehouseData()
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowTitle("Warehouse Management System - Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Main content tabs
        tabs = QTabWidget()
        self.inventory_widget = InventoryWidget(self.data)
        self.orders_widget = OrdersWidget(self.data)
        self.performance_widget = PerformanceWidget(self.data)

        tabs.addTab(self.inventory_widget, "Inventory")
        tabs.addTab(self.orders_widget, "Orders")
        tabs.addTab(self.performance_widget, "Performance")

        layout.addWidget(tabs)
        central_widget.setLayout(layout)

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        
        # Logo or Title
        logo_label = QLabel("Warehouse Hub")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        
        # Search Bar (optional)
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search products, orders...")
        search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # User Profile/Settings (optional)
        user_label = QLabel("Welcome, Admin!")
        user_label.setStyleSheet("font-size: 14px; color: #555;")
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)
        header_layout.addStretch()
        header_layout.addWidget(user_label)
        
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: white; padding: 10px; border-bottom: 1px solid #e0e0e0;")
        
        return header_widget

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data_and_ui)
        self.timer.start(60000)  # Update every 60 seconds (1 minute)

    def update_data_and_ui(self):
        print("Updating data and UI...")
        self.data.generate_sample_data()  # Regenerate data for demonstration
        self.inventory_widget.init_ui() # Reinitialize to refresh data and charts
        self.orders_widget.init_ui()
        self.performance_widget.init_ui()
        print("UI update complete.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Apply a modern style (optional)
    app.setStyle("Fusion") 
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.WindowText, QColor("#333333"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, QColor("#333333"))
    palette.setColor(QPalette.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ButtonText, QColor("#333333"))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor("#2196F3"))
    palette.setColor(QPalette.Highlight, QColor("#2196F3"))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    dashboard = WarehouseDashboard()
    dashboard.show()
    sys.exit(app.exec_())