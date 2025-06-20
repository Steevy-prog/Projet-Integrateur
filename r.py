import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import datetime
import random

class LogisticsData:
    """Data generator and manager for logistics operations"""

    def __init__(self):
        self.generate_sample_data()

    def generate_sample_data(self):
        # Orders data
        orders = []
        customers = ['Amazon', 'Walmart', 'Target', 'Best Buy', 'Home Depot', 'Costco', 'FedEx', 'UPS']
        order_statuses = ['Pending', 'Processing', 'In Transit', 'Delivered', 'Cancelled']
        priorities = ['Low', 'Medium', 'High', 'Critical']

        for i in range(50):
            orders.append({
                'Order_ID': f'LO{i+1:04d}',
                'Customer': random.choice(customers),
                'Origin': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'Destination': random.choice(['Miami', 'Seattle', 'Denver', 'Atlanta', 'Boston']),
                'Order_Date': datetime.date.today() - datetime.timedelta(days=random.randint(0, 30)),
                'Expected_Delivery': datetime.date.today() + datetime.timedelta(days=random.randint(1, 15)),
                'Status': random.choice(order_statuses),
                'Priority': random.choice(priorities),
                'Value': random.randint(1000, 50000),
                'Weight': random.randint(10, 5000),
                'Items_Count': random.randint(1, 20)
            })

        self.orders_df = pd.DataFrame(orders)

        # Shipments data
        shipments = []
        carriers = ['FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics']
        transport_modes = ['Ground', 'Air', 'Sea', 'Rail']

        for i in range(75):
            shipments.append({
                'Shipment_ID': f'SH{i+1:04d}',
                'Order_ID': f'LO{random.randint(1, 50):04d}',
                'Carrier': random.choice(carriers),
                'Transport_Mode': random.choice(transport_modes),
                'Current_Location': random.choice(['Distribution Center', 'In Transit', 'Local Facility', 'Out for Delivery']),
                'Departure_Date': datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                'ETA': datetime.date.today() + datetime.timedelta(days=random.randint(0, 7)),
                'Status': random.choice(['Picked Up', 'In Transit', 'Delivered', 'Delayed', 'Exception']),
                'Tracking_Number': f'TRK{random.randint(100000, 999999)}',
                'Cost': random.randint(50, 2000)
            })

        self.shipments_df = pd.DataFrame(shipments)

        # Resources data
        resources = []
        vehicle_types = ['Truck', 'Van', 'Cargo Plane', 'Container Ship']
        resource_statuses = ['Available', 'In Use', 'Maintenance', 'Out of Service']

        for i in range(30):
            resources.append({
                'Resource_ID': f'RES{i+1:03d}',
                'Type': random.choice(vehicle_types),
                'Capacity': random.randint(1000, 50000),
                'Current_Load': random.randint(0, 40000),
                'Status': random.choice(resource_statuses),
                'Location': random.choice(['Warehouse A', 'Warehouse B', 'Distribution Center', 'Customer Site']),
                'Driver': f'Driver {i+1}',
                'Fuel_Level': random.randint(20, 100),
                'Next_Maintenance': datetime.date.today() + datetime.timedelta(days=random.randint(1, 90))
            })

        self.resources_df = pd.DataFrame(resources)

        # Performance metrics
        dates = pd.date_range(start='2024-01-01', end='2024-06-19', freq='D')
        self.daily_metrics = pd.DataFrame({
            'Date': dates,
            'Orders_Processed': np.random.poisson(25, len(dates)),
            'Shipments_Delivered': np.random.poisson(30, len(dates)),
            'On_Time_Delivery_Rate': np.random.uniform(85, 98, len(dates)),
            'Resource_Utilization': np.random.uniform(60, 95, len(dates)),
            'Average_Delivery_Time': np.random.uniform(2.5, 8.0, len(dates)),
            'Cost_Per_Shipment': np.random.uniform(150, 400, len(dates))
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

class OrderProcessingWidget(QWidget):
    """Widget for order processing management"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Order Processing")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        refresh_btn = QPushButton("Refresh Orders")
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

        total_orders = len(self.data.orders_df)
        pending_orders = len(self.data.orders_df[self.data.orders_df['Status'] == 'Pending'])
        processing_orders = len(self.data.orders_df[self.data.orders_df['Status'] == 'Processing'])
        total_value = self.data.orders_df['Value'].sum()

        metrics_layout.addWidget(MetricCard("Total Orders", str(total_orders), "All Orders"))
        metrics_layout.addWidget(MetricCard("Pending", str(pending_orders), "Awaiting Processing", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Processing", str(processing_orders), "In Progress", "#2196F3"))
        metrics_layout.addWidget(MetricCard("Total Value", f"${total_value:,.0f}", "Order Worth"))

        # Charts section
        charts_layout = QHBoxLayout()

        # Order status pie chart
        status_chart = ChartWidget()
        self.create_order_status_chart(status_chart)

        # Priority distribution
        priority_chart = ChartWidget()
        self.create_priority_chart(priority_chart)

        charts_layout.addWidget(status_chart)
        charts_layout.addWidget(priority_chart)

        # Orders table
        self.orders_table = self.create_orders_table()

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(self.orders_table)

        self.setLayout(layout)

    def create_order_status_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        status_counts = self.data.orders_df['Status'].value_counts()
        colors = ['#4CAF50', '#FF9800', '#2196F3', '#9C27B0', '#F44336']

        ax.pie(status_counts.values,
               labels=status_counts.index,
               autopct='%1.1f%%',
               colors=colors[:len(status_counts)])

        ax.set_title('Orders by Status', fontsize=14, fontweight='bold', pad=20)
        chart_widget.canvas.draw()

    def create_priority_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        priority_counts = self.data.orders_df['Priority'].value_counts()
        colors = {'Critical': '#F44336', 'High': '#FF9800', 'Medium': '#2196F3', 'Low': '#4CAF50'}

        bars = ax.bar(priority_counts.index, priority_counts.values,
                      color=[colors.get(p, '#888888') for p in priority_counts.index])

        ax.set_title('Orders by Priority', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Orders')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')

        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

    def create_orders_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.orders_df))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['Order ID', 'Customer', 'Destination', 'Status', 'Priority', 'Value', 'Expected Delivery'])

        for i, (_, row) in enumerate(self.data.orders_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Order_ID']))
            table.setItem(i, 1, QTableWidgetItem(row['Customer']))
            table.setItem(i, 2, QTableWidgetItem(row['Destination']))

            # Status with color coding
            status_item = QTableWidgetItem(row['Status'])
            if row['Status'] == 'Pending':
                status_item.setBackground(QColor('#FFF3E0'))
            elif row['Status'] == 'Processing':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Delivered':
                status_item.setBackground(QColor('#E8F5E8'))

            table.setItem(i, 3, status_item)

            # Priority with color coding
            priority_item = QTableWidgetItem(row['Priority'])
            if row['Priority'] == 'Critical':
                priority_item.setBackground(QColor('#FFEBEE'))
            elif row['Priority'] == 'High':
                priority_item.setBackground(QColor('#FFF3E0'))

            table.setItem(i, 4, priority_item)
            table.setItem(i, 5, QTableWidgetItem(f"${row['Value']:,.0f}"))
            table.setItem(i, 6, QTableWidgetItem(str(row['Expected_Delivery'])))

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

class ShipmentTrackingWidget(QWidget):
    """Widget for shipment tracking"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Shipment Tracking")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        # Search functionality
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter tracking number or shipment ID...")
        search_btn = QPushButton("Track")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)

        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)

        # Metrics cards
        metrics_layout = QHBoxLayout()

        total_shipments = len(self.data.shipments_df)
        in_transit = len(self.data.shipments_df[self.data.shipments_df['Status'] == 'In Transit'])
        delivered = len(self.data.shipments_df[self.data.shipments_df['Status'] == 'Delivered'])
        delayed = len(self.data.shipments_df[self.data.shipments_df['Status'] == 'Delayed'])

        metrics_layout.addWidget(MetricCard("Total Shipments", str(total_shipments), "Active Shipments"))
        metrics_layout.addWidget(MetricCard("In Transit", str(in_transit), "Currently Moving", "#2196F3"))
        metrics_layout.addWidget(MetricCard("Delivered", str(delivered), "Completed", "#4CAF50"))
        metrics_layout.addWidget(MetricCard("Delayed", str(delayed), "Need Attention", "#F44336"))

        # Charts section
        charts_layout = QHBoxLayout()

        # Shipment status chart
        status_chart = ChartWidget()
        self.create_shipment_status_chart(status_chart)

        # Carrier performance chart
        carrier_chart = ChartWidget()
        self.create_carrier_chart(carrier_chart)

        charts_layout.addWidget(status_chart)
        charts_layout.addWidget(carrier_chart)

        # Shipments table
        self.shipments_table = self.create_shipments_table()

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(self.shipments_table)

        self.setLayout(layout)

    def create_shipment_status_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        status_counts = self.data.shipments_df['Status'].value_counts()
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0']

        bars = ax.bar(status_counts.index, status_counts.values,
                      color=colors[:len(status_counts)])

        ax.set_title('Shipments by Status', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Shipments')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')

        plt.xticks(rotation=45)
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

    def create_carrier_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        carrier_counts = self.data.shipments_df['Carrier'].value_counts()
        colors = ['#FF9800', '#4CAF50', '#2196F3', '#9C27B0', '#F44336']

        ax.pie(carrier_counts.values,
               labels=carrier_counts.index,
               autopct='%1.1f%%',
               colors=colors[:len(carrier_counts)])

        ax.set_title('Shipments by Carrier', fontsize=14, fontweight='bold', pad=20)
        chart_widget.canvas.draw()

    def create_shipments_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.shipments_df))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['Shipment ID', 'Tracking Number', 'Carrier', 'Current Location', 'Status', 'ETA', 'Cost'])

        for i, (_, row) in enumerate(self.data.shipments_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Shipment_ID']))
            table.setItem(i, 1, QTableWidgetItem(row['Tracking_Number']))
            table.setItem(i, 2, QTableWidgetItem(row['Carrier']))
            table.setItem(i, 3, QTableWidgetItem(row['Current_Location']))

            # Status with color coding
            status_item = QTableWidgetItem(row['Status'])
            if row['Status'] == 'Delivered':
                status_item.setBackground(QColor('#E8F5E8'))
            elif row['Status'] == 'In Transit':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Delayed':
                status_item.setBackground(QColor('#FFEBEE'))

            table.setItem(i, 4, status_item)
            table.setItem(i, 5, QTableWidgetItem(str(row['ETA'])))
            table.setItem(i, 6, QTableWidgetItem(f"${row['Cost']:,.0f}"))

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

class ResourceAllocationWidget(QWidget):
    """Widget for resource allocation management"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        title = QLabel("Resource Allocation")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Metrics cards
        metrics_layout = QHBoxLayout()

        total_resources = len(self.data.resources_df)
        available = len(self.data.resources_df[self.data.resources_df['Status'] == 'Available'])
        in_use = len(self.data.resources_df[self.data.resources_df['Status'] == 'In Use'])
        maintenance = len(self.data.resources_df[self.data.resources_df['Status'] == 'Maintenance'])

        metrics_layout.addWidget(MetricCard("Total Resources", str(total_resources), "Fleet Size"))
        metrics_layout.addWidget(MetricCard("Available", str(available), "Ready for Use", "#4CAF50"))
        metrics_layout.addWidget(MetricCard("In Use", str(in_use), "Currently Active", "#2196F3"))
        metrics_layout.addWidget(MetricCard("Maintenance", str(maintenance), "Under Service", "#FF9800"))

        # Charts section
        charts_layout = QHBoxLayout()

        # Resource status chart
        status_chart = ChartWidget()
        self.create_resource_status_chart(status_chart)

        # Resource utilization chart
        utilization_chart = ChartWidget()
        self.create_utilization_chart(utilization_chart)

        charts_layout.addWidget(status_chart)
        charts_layout.addWidget(utilization_chart)

        # Resources table
        self.resources_table = self.create_resources_table()

        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(self.resources_table)

        self.setLayout(layout)

    def create_resource_status_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        status_counts = self.data.resources_df['Status'].value_counts()
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336']

        ax.pie(status_counts.values,
               labels=status_counts.index,
               autopct='%1.1f%%',
               colors=colors[:len(status_counts)])

        ax.set_title('Resources by Status', fontsize=14, fontweight='bold', pad=20)
        chart_widget.canvas.draw()

    def create_utilization_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        # Calculate utilization percentage for each resource
        self.data.resources_df['Utilization'] = (self.data.resources_df['Current_Load'] /
                                                 self.data.resources_df['Capacity'] * 100)
        
        # Group by resource type and get average utilization
        type_utilization = self.data.resources_df.groupby('Type')['Utilization'].mean()

        bars = ax.bar(type_utilization.index, type_utilization.values)

        # Color bars based on utilization level
        for i, util in enumerate(type_utilization.values):
            if util > 80:
                bars[i].set_color('#F44336')  # Red for high utilization
            elif util > 60:
                bars[i].set_color('#FF9800')  # Orange for medium utilization
            else:
                bars[i].set_color('#4CAF50')  # Green for low utilization

        ax.set_title('Average Utilization by Resource Type', fontsize=14, fontweight='bold')
        ax.set_ylabel('Utilization %')
        ax.set_ylim(0, 100)

        # Add percentage labels on bars
        for bar, util in zip(bars, type_utilization.values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{util:.1f}%', ha='center', va='bottom')

        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

    def create_resources_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.resources_df))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['Resource ID', 'Type', 'Status', 'Utilization', 'Location', 'Driver', 'Next Maintenance'])

        for i, (_, row) in enumerate(self.data.resources_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['Resource_ID']))
            table.setItem(i, 1, QTableWidgetItem(row['Type']))

            # Status with color coding
            status_item = QTableWidgetItem(row['Status'])
            if row['Status'] == 'Available':
                status_item.setBackground(QColor('#E8F5E8'))
            elif row['Status'] == 'In Use':
                status_item.setBackground(QColor('#E3F2FD'))
            elif row['Status'] == 'Maintenance':
                status_item.setBackground(QColor('#FFF3E0'))

            table.setItem(i, 2, status_item)

            # Utilization
            utilization = (row['Current_Load'] / row['Capacity']) * 100
            util_item = QTableWidgetItem(f"{utilization:.1f}%")
            if utilization > 80:
                util_item.setBackground(QColor('#FFEBEE'))
            table.setItem(i, 3, util_item)

            table.setItem(i, 4, QTableWidgetItem(row['Location']))
            table.setItem(i, 5, QTableWidgetItem(row['Driver']))
            table.setItem(i, 6, QTableWidgetItem(str(row['Next_Maintenance'])))

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

class PerformanceMonitoringWidget(QWidget):
    """Widget for performance monitoring and analytics"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Performance Monitoring")
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
        avg_delivery_time = recent_data['Average_Delivery_Time'].mean()
        on_time_rate = recent_data['On_Time_Delivery_Rate'].mean()
        resource_util = recent_data['Resource_Utilization'].mean()
        avg_cost = recent_data['Cost_Per_Shipment'].mean()

        kpi_layout.addWidget(MetricCard("Avg Delivery Time", f"{avg_delivery_time:.1f} days", "Last 30 days"))
        kpi_layout.addWidget(MetricCard("On-Time Rate", f"{on_time_rate:.1f}%", "Delivery Performance"))
        kpi_layout.addWidget(MetricCard("Resource Utilization", f"{resource_util:.1f}%", "Fleet Efficiency"))
        kpi_layout.addWidget(MetricCard("Avg Cost/Shipment", f"${avg_cost:.0f}", "Cost Efficiency"))

        # Charts
        charts_layout = QGridLayout()

        # Delivery performance trend
        performance_chart = ChartWidget()
        self.create_performance_chart(performance_chart)
        charts_layout.addWidget(performance_chart, 0, 0)

        # Cost analysis
        cost_chart = ChartWidget()
        self.create_cost_chart(cost_chart)
        charts_layout.addWidget(cost_chart, 0, 1)

        # Resource utilization trend
        utilization_chart = ChartWidget()
        self.create_utilization_trend_chart(utilization_chart)
        charts_layout.addWidget(utilization_chart, 1, 0, 1, 2)

        layout.addLayout(header_layout)
        layout.addLayout(kpi_layout)
        layout.addLayout(charts_layout)

        self.setLayout(layout)

    def create_performance_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        recent_data = self.data.daily_metrics.tail(30)

        ax.plot(recent_data['Date'], recent_data['On_Time_Delivery_Rate'],
                label='On-Time Rate', color='#4CAF50', linewidth=2)
        ax.plot(recent_data['Date'], recent_data['Average_Delivery_Time'] * 10, # Scale for visualization
                label='Delivery Time (×10)', color='#2196F3', linewidth=2)

        ax.set_title('Delivery Performance Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Percentage / Days')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

    def create_cost_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        recent_data = self.data.daily_metrics.tail(30)

        ax.plot(recent_data['Date'], recent_data['Cost_Per_Shipment'],
                label='Cost Per Shipment', color='#FF9800', linewidth=2)

        ax.set_title('Cost Per Shipment Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cost ($)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()

    def create_utilization_trend_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        recent_data = self.data.daily_metrics.tail(30)

        ax.plot(recent_data['Date'], recent_data['Resource_Utilization'],
                label='Resource Utilization', color='#9C27B0', linewidth=2)

        ax.set_title('Resource Utilization Trend', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Utilization %')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        chart_widget.figure.tight_layout()
        chart_widget.canvas.draw()


class MainDashboard(QMainWindow):
    """Main application window for the Logistics Dashboard"""

    def __init__(self):
        super().__init__()
        self.data = LogisticsData()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Logistics Management Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Set a professional and modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5; /* Light gray background */
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0; /* Subtle border for tab content */
                background-color: #ffffff; /* White background for tab content */
                border-radius: 8px; /* Rounded corners for the tab pane */
            }
            QTabBar::tab {
                background: #e0e0e0; /* Light gray for inactive tabs */
                border: 1px solid #c0c0c0;
                border-bottom-color: #c0c0c0; /* Same as pane border */
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 100px;
                padding: 8px;
                font-weight: bold;
                color: #555; /* Darker text for inactive tabs */
            }
            QTabBar::tab:selected {
                background: #ffffff; /* White for active tab */
                border-color: #c0c0c0;
                border-bottom-color: #ffffff; /* Matches pane background */
                color: #333; /* Even darker text for active tab */
            }
            QLabel {
                color: #333; /* Dark gray for general labels */
            }
        """)

        self.create_menu_bar()
        self.create_central_widget()

        # Set up a timer to refresh data periodically (e.g., every 5 minutes)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard_data)
        self.timer.start(300000) # 300000 ms = 5 minutes

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Data Menu
        data_menu = menu_bar.addMenu("Data")
        refresh_action = QAction("Refresh Data", self)
        refresh_action.triggered.connect(self.refresh_dashboard_data)
        data_menu.addAction(refresh_action)

        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_central_widget(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.order_widget = OrderProcessingWidget(self.data)
        self.tab_widget.addTab(self.order_widget, "Order Processing")

        self.shipment_widget = ShipmentTrackingWidget(self.data)
        self.tab_widget.addTab(self.shipment_widget, "Shipment Tracking")

        self.resource_widget = ResourceAllocationWidget(self.data)
        self.tab_widget.addTab(self.resource_widget, "Resource Allocation")

        self.performance_widget = PerformanceMonitoringWidget(self.data)
        self.tab_widget.addTab(self.performance_widget, "Performance Monitoring")

    def refresh_dashboard_data(self):
        # Regenerate sample data
        self.data.generate_sample_data()

        # Refresh individual widgets
        self.order_widget.init_ui() # Re-initialize to refresh all elements
        self.shipment_widget.init_ui()
        self.resource_widget.init_ui()
        self.performance_widget.init_ui()

        QMessageBox.information(self, "Data Refresh", "Logistics data has been refreshed!")

    def show_about_dialog(self):
        QMessageBox.about(self, "About Logistics Dashboard",
                          "This is a sample Logistics Management Dashboard built with PyQt5 and Matplotlib."
                          "\n\nVersion 1.0")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Apply a modern fusion style for a cleaner look
    app.setStyle("Fusion")

    # Set up a global palette for consistent colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#f0f2f5')) # Background of main window
    palette.setColor(QPalette.WindowText, QColor('#333333'))
    palette.setColor(QPalette.Base, QColor('#ffffff')) # Background of input fields, tables
    palette.setColor(QPalette.AlternateBase, QColor('#f5f5f5')) # Alternate row color in tables
    palette.setColor(QPalette.ToolTipBase, QColor('#ffffff'))
    palette.setColor(QPalette.ToolTipText, QColor('#333333'))
    palette.setColor(QPalette.Text, QColor('#333333'))
    palette.setColor(QPalette.Button, QColor('#e0e0e0'))
    palette.setColor(QPalette.ButtonText, QColor('#333333'))
    palette.setColor(QPalette.BrightText, QColor('#ff0000'))
    palette.setColor(QPalette.Link, QColor('#2196F3'))
    palette.setColor(QPalette.Highlight, QColor('#2196F3')) # Selection color
    palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    app.setPalette(palette)

    ex = MainDashboard()
    ex.show()
    sys.exit(app.exec_())