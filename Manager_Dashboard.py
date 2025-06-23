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

        #reception data 2

        reception2_datas=[]
        for i in range(20):
            reception2_datas.append({
                'identifiant du colis':f'C{i+1:04d}',
                'date prevue':datetime.date.today() + datetime.timedelta(days=random.randint(-5, 15)),
                'Statuts': random.choice(statuses)
            })
        self.reception2_df = pd.DataFrame(reception2_datas)
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

        #expedition 2 data
        expedition2_datas=[]
        for i in range(25):
            expedition2_datas.append({
                'identifiant du colis':f'C{i+1:04d}',
                'identifiant du lot':f'L{i+1:04d}',
                'idbonexpedition':f'BE{i+1:03d}',
                'dateexpedition': datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
            })
        self.expedition2_df = pd.DataFrame(expedition2_datas)

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

class RealtimeInventoryViewWidget(QWidget):
    """Widget for real-time inventory view, product details, location details, and stock movements"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Real-time Inventory View")
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
        refresh_btn.clicked.connect(self.refresh_data)

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

        # Inventory table (can be considered a detailed view for Product Details and Location Details)
        self.inventory_table = self.create_inventory_table()

        # Placeholder for Stock Movements (New section)
        stock_movements_label = QLabel("Stock Movements (Not Implemented Yet)")
        stock_movements_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        # In a real application, this would be a table or chart showing recent movements.

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        layout.addLayout(charts_layout)
        layout.addWidget(self.inventory_table)
        layout.addWidget(stock_movements_label) # Add the placeholder
        layout.addStretch() # Push everything to the top

        self.setLayout(layout)

    def refresh_data(self):
        # This method can be called to re-render the UI with fresh data
        self.clear_layout(self.layout())
        self.init_ui()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def create_category_chart(self, chart_widget):
        ax = chart_widget.figure.add_subplot(111)

        # Group by category
        category_data = []
        # Ensure that inventory_df is joined or mapped to products_df for category
        merged_df = pd.merge(self.data.inventory_df, self.data.products_df[['ID', 'Category']],
                             left_on='Product_ID', right_on='ID', how='left')
        category_summary = merged_df.groupby('Category')['Quantity'].sum()

        colors = ['#FF9800', '#4CAF50', '#2196F3', '#9C27B0']
        ax.pie(category_summary.values,
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

class StorageSpaceManagementWidget(QWidget):
    """Widget for Storage Space Management"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Storage Space Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Metric Card for Utilization
        avg_utilization = self.data.daily_metrics['Storage_Utilization'].mean()
        layout.addWidget(MetricCard("Overall Utilization", f"{avg_utilization:.1f}%", "Average Warehouse Utilization"))

        # Placeholder for sub-features
        sub_features_layout = QGridLayout()
        sub_features_layout.addWidget(QLabel("<h3>Cell Optimization</h3><p>Simulate optimal cell assignment.</p>"), 0, 0)
        sub_features_layout.addWidget(QLabel("<h3>Space Allocation</h3><p>Manage space assignments for product categories.</p>"), 0, 1)
        sub_features_layout.addWidget(QLabel("<h3>Layout Management</h3><p>Visualize and modify warehouse layout.</p>"), 1, 0, 1, 2)
        layout.addLayout(sub_features_layout)

        layout.addStretch()
        self.setLayout(layout)


class ReportsWidget(QWidget):
    """Widget for generating various reports"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Generate Reports")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        tabs = QTabWidget()

        # Stock Reports
        stock_reports_widget = QWidget()
        stock_reports_layout = QVBoxLayout()
        stock_reports_layout.addWidget(QLabel("<h4>Stock Reports</h4>"))
        stock_reports_layout.addWidget(QLabel("Generate reports on current stock levels, low stock items, and inventory value."))

        self.stock_summary_table = self.create_stock_summary_table() # Make it an instance variable
        stock_reports_layout.addWidget(self.stock_summary_table)

        # Add Save button for Stock Reports
        save_stock_btn = QPushButton("Save Stock Report to CSV")
        save_stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        save_stock_btn.clicked.connect(self.save_stock_report_to_csv)
        stock_reports_layout.addWidget(save_stock_btn)


        stock_reports_widget.setLayout(stock_reports_layout)
        tabs.addTab(stock_reports_widget, "Stock Reports")

        # Performance Reports (reusing PerformanceWidget logic)
        self.performance_reports_widget = PerformanceWidget(self.data)
        tabs.addTab(self.performance_reports_widget, "Performance Reports")

        # Exception Reports
        exception_reports_widget = QWidget()
        exception_reports_layout = QVBoxLayout()
        exception_reports_layout.addWidget(QLabel("<h4>Exception Reports</h4>"))
        exception_reports_layout.addWidget(QLabel("View reports on overdue orders, critical low stock, and discrepancies."))
        # Example: Low Stock Exception
        self.low_stock_exceptions = self.data.inventory_df[self.data.inventory_df['Quantity'] <= self.data.inventory_df['Min_Stock']] # Make it an instance variable
        if not self.low_stock_exceptions.empty:
            exception_reports_layout.addWidget(QLabel("<p style='color: red; font-weight: bold;'>Critical Low Stock Items:</p>"))
            self.low_stock_table = QTableWidget() # Make it an instance variable
            self.low_stock_table.setRowCount(len(self.low_stock_exceptions))
            self.low_stock_table.setColumnCount(3)
            self.low_stock_table.setHorizontalHeaderLabels(['Product', 'Quantity', 'Min Stock'])
            for i, (_, row) in enumerate(self.low_stock_exceptions.iterrows()):
                self.low_stock_table.setItem(i, 0, QTableWidgetItem(row['Product_Name']))
                self.low_stock_table.setItem(i, 1, QTableWidgetItem(str(row['Quantity'])))
                self.low_stock_table.setItem(i, 2, QTableWidgetItem(str(row['Min_Stock'])))
            exception_reports_layout.addWidget(self.low_stock_table)

            # Add Save button for Low Stock Exceptions
            save_low_stock_btn = QPushButton("Save Low Stock Report to CSV")
            save_low_stock_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #FB8C00;
                }
            """)
            save_low_stock_btn.clicked.connect(self.save_low_stock_report_to_csv)
            exception_reports_layout.addWidget(save_low_stock_btn)

        else:
            exception_reports_layout.addWidget(QLabel("<p>No critical low stock items.</p>"))

        exception_reports_widget.setLayout(exception_reports_layout)
        tabs.addTab(exception_reports_widget, "Exception Reports")

        layout.addWidget(tabs)
        layout.addStretch()
        self.setLayout(layout)

    def create_stock_summary_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.inventory_df))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Product', 'Category', 'Quantity', 'Min Stock', 'Current Value'])

        # Prepare data for easy CSV export
        self.stock_summary_data = []
        for i, (_, row) in enumerate(self.data.inventory_df.iterrows()):
            product_info = self.data.products_df[self.data.products_df['ID'] == row['Product_ID']].iloc[0]
            current_value = row['Quantity'] * row['Value']
            table.setItem(i, 0, QTableWidgetItem(row['Product_Name']))
            table.setItem(i, 1, QTableWidgetItem(product_info['Category']))
            table.setItem(i, 2, QTableWidgetItem(str(row['Quantity'])))
            table.setItem(i, 3, QTableWidgetItem(str(row['Min_Stock'])))
            table.setItem(i, 4, QTableWidgetItem(f"${current_value:,.2f}"))
            self.stock_summary_data.append({
                'Product': row['Product_Name'],
                'Category': product_info['Category'],
                'Quantity': row['Quantity'],
                'Min Stock': row['Min_Stock'],
                'Current Value': current_value
            })
        self.stock_summary_df = pd.DataFrame(self.stock_summary_data) # Store as DataFrame for easy export
        table.resizeColumnsToContents()
        return table

    def save_stock_report_to_csv(self):
        if not self.stock_summary_df.empty:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Stock Report", "stock_report.csv", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_name:
                try:
                    self.stock_summary_df.to_csv(file_name, index=False)
                    QMessageBox.information(self, "Success", f"Stock report saved to:\n{file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save stock report: {e}")
        else:
            QMessageBox.warning(self, "No Data", "No stock data to save.")

    def save_low_stock_report_to_csv(self):
        if not self.low_stock_exceptions.empty:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Low Stock Report", "low_stock_report.csv", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_name:
                try:
                    # Select relevant columns for the low stock report
                    report_df = self.low_stock_exceptions[['Product_Name', 'Quantity', 'Min_Stock']]
                    report_df.to_csv(file_name, index=False)
                    QMessageBox.information(self, "Success", f"Low stock report saved to:\n{file_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save low stock report: {e}")
        else:
            QMessageBox.warning(self, "No Data", "No low stock exceptions to save.")



class DailyOperationsPlanningWidget(QWidget):
    """Widget for Daily Operations Planning"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Daily Operations Planning")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Incorporate OrdersWidget as a central part of daily planning
        orders_section_label = QLabel("<h4>Order Management (Reception & Expedition)</h4>")
        layout.addWidget(orders_section_label)
        self.orders_widget = OrdersWidget(self.data)
        layout.addWidget(self.orders_widget)

        # Placeholder for other planning aspects
        planning_info_label = QLabel("<h3>Planning Tools:</h3>"
                                     "<ul>"
                                     "<li>Schedule Shipments & Receptions</li>"
                                     "<li>Allocate Workforce for Picking/Packing</li>"
                                     "<li>Forecast Demand (using historical data)</li>"
                                     "</ul>")
        layout.addWidget(planning_info_label)

        layout.addStretch()
        self.setLayout(layout)

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


class ZoneEmballage(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        container = QWidget()
        container.setStyleSheet("background-color: #f5f5f5;")
        big_layout = QGridLayout(container)
        big_layout.setVerticalSpacing(20)
        big_layout.setHorizontalSpacing(20)
        big_layout.setContentsMargins(20, 20, 20, 20)

        # Frame pour l'emballage
        emballage_frame = QFrame()
        emballage_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        emballage_layout = QVBoxLayout(emballage_frame)
        emballage_layout.setSpacing(20)

        # Titre Emballage
        emballage_title = QLabel("Emballage")
        emballage_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #2c3e50;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        emballage_layout.addWidget(emballage_title)

        # Cartes de métriques pour Emballage
        metrics_emballage_layout = QGridLayout()
        metrics_emballage_layout.setVerticalSpacing(15)
        metrics_emballage_layout.setHorizontalSpacing(15)


        # Carte 1 - Colis à emballer
        card1 = self.create_metric_card(
            title="42",
            value="En attente",
            subtitle="Dernière mise à jour: 05/03/2025",
            color="#2196F3",
            title_label="Colis à emballer",
            value_label="Statut",
            subtitle_label="Information"
        )
        metrics_emballage_layout.addWidget(card1, 0, 0)

        # Carte 2 - Colis emballés
        card2 = self.create_metric_card(
            title="128",
            value="Aujourd'hui",
            subtitle="Objectif: 150 colis/jour",
            color="#4CAF50",
            title_label="Colis emballés",
            value_label="Période",
            subtitle_label="Performance"
        )
        metrics_emballage_layout.addWidget(card2, 0, 1)

        # Carte 3 - Progression
        card3 = self.create_metric_card(
            title="70%",
            value="05/03/2025",
            subtitle="Avancement global",
            color="#FF9800",
            title_label="Progression",
            value_label="Date",
            subtitle_label="Détails",
            label_color="#FFFFFF",
            label_bg="#607D8B"
        )
        
        metrics_emballage_layout.addWidget(card3, 1, 0, 1, 2, Qt.AlignCenter)

        emballage_layout.addLayout(metrics_emballage_layout)
        emballage_layout.addStretch()

        # Frame pour le désemballage
        desemballage_frame = QFrame()
        desemballage_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        desemballage_layout = QVBoxLayout(desemballage_frame)
        desemballage_layout.setSpacing(20)

        # Titre Désemballage
        desemballage_title = QLabel("Désemballage")
        desemballage_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #2c3e50;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        desemballage_layout.addWidget(desemballage_title)

        # Cartes de métriques pour Désemballage
        metrics_desemballage_layout = QGridLayout()
        metrics_desemballage_layout.setVerticalSpacing(15)
        metrics_desemballage_layout.setHorizontalSpacing(15)

        # Carte 4 - Colis à désemballer
        card4 = self.create_metric_card(
            title="24",
            value="En attente",
            subtitle="Priorité: Moyenne",
            color="#2196F3",
            title_label="Colis à désemballer",
            value_label="Statut",
            subtitle_label="Information"
        )
        metrics_desemballage_layout.addWidget(card4, 0, 0)

        # Carte 5 - Colis désemballés
        card5 = self.create_metric_card(
            title="76",
            value="Aujourd'hui",
            subtitle="Efficacité: 85%",
            color="#4CAF50",
            title_label="Colis désemballés",
            value_label="Période",
            subtitle_label="Performance"
        )
        metrics_desemballage_layout.addWidget(card5, 0, 1)
        # Carte 6 - Progression désemballage
        card6 = self.create_metric_card(
            title="65%",
            value="05/03/2025",
            subtitle="Taux de complétion",
            color="#FF9800",
            title_label="Progression",
            value_label="Date",
            subtitle_label="Détails",
            label_color="#FFFFFF",
            label_bg="#607D8B"
        )
        
        metrics_desemballage_layout.addWidget(card6, 1, 0, 1, 2, Qt.AlignCenter)

        desemballage_layout.addLayout(metrics_desemballage_layout)
        desemballage_layout.addStretch()

        # Ajout des frames à la disposition principale
        big_layout.addWidget(emballage_frame, 0, 0)
        big_layout.addWidget(desemballage_frame, 1, 0)

        self.setLayout(big_layout)

    def create_metric_card(self, title, value, subtitle, color,
                           title_label=None, value_label=None, subtitle_label=None,
                           label_color="#555", label_bg="#f8f9fa"):
        """Crée une carte de métrique avec des labels optionnels pour chaque élément"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Style pour les labels descriptifs
        label_style = f"""
            QLabel {{
                font-size: 14px;
                color: {label_color};
                font-weight: 500;
                padding: 4px 8px;
                background-color: {label_bg};
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                margin-bottom: 2px;
            }}
        """

        # Titre avec label optionnel
        if title_label:
            title_desc = QLabel(title_label)
            title_desc.setStyleSheet(label_style)
            layout.addWidget(title_desc)

        title_widget = QLabel(title)
        title_widget.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #666;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_widget)

        # Valeur avec label optionnel
        if value_label:
            value_desc = QLabel(value_label)
            value_desc.setStyleSheet(label_style)
            layout.addWidget(value_desc)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                margin: 5px 0;
            }}
        """)
        layout.addWidget(value_widget)

        # Sous-titre avec label optionnel
        if subtitle_label:
            subtitle_desc = QLabel(subtitle_label)
            subtitle_desc.setStyleSheet(label_style)
            layout.addWidget(subtitle_desc)

        subtitle_widget = QLabel(subtitle)
        subtitle_widget.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #999;
                margin-top: 5px;
            }
        """)
        layout.addWidget(subtitle_widget)

        layout.addStretch()
        return card

class MenuExpedition(QWidget):
    def __init__(self,data):
        super().__init__()
        self.data=data
        self.init_ui()
    def init_ui(self):
        layout = QGridLayout()
        expedition_summary_table = self.create_expedition_summary_table()
        bouton = QPushButton("chatte")
        bouton.setFixedWidth(1000)
        bouton.setStyleSheet("""
                       QPushButton { background-color: #2196F3; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; 
                       width:10px;}
                       QPushButton:hover { background-color: #1976D2; }
                   """)
        layout.addWidget(expedition_summary_table,0,0)
        layout.addWidget(bouton,0,1)
        self.setLayout(layout)

    def create_expedition_summary_table(self):
        table = QTableWidget()
        
        table.setRowCount(len(self.data.expedition2_df))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['identifiant du colis', 'identifiant du lot', 'id du bon de reception',"date d'expedition"])

        for i, (_, row) in enumerate(self.data.expedition2_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['identifiant du colis']))
            table.setItem(i, 1, QTableWidgetItem(row['identifiant du lot']))
            table.setItem(i, 2, QTableWidgetItem(row['idbonexpedition']))
            table.setItem(i, 4, QTableWidgetItem(str(row['dateexpedition'])))
        table.setStyleSheet("""
                    QTableWidget { background-color: white; alternate-background-color: #f5f5f5; selection-background-color: #e3f2fd; gridline-color: #e0e0e0; }
                    QHeaderView::section { background-color: #f5f5f5; padding: 8px; border: 1px solid #e0e0e0; font-weight: bold; }
                """)
        table.resizeColumnsToContents()
        return table
class MenuReception(QWidget):
    def __init__(self,data):
        super().__init__()
        self.data=data
        self.init_ui()
    def init_ui(self):
        layout = QGridLayout()
        reception_summary_table = self.create_reception_summary_table()
        bouton = QPushButton("informer magasinier")
        bouton.setFixedWidth(1000)
        bouton.setStyleSheet("""
               QPushButton { background-color: #2196F3; color: white; border: none; padding: 50px 16px; border-radius: 15px; font-weight: bold; 
               width:10px;}
               QPushButton:hover { background-color: #1976D2; }
           """)
        layout.addWidget(bouton,0,1)
        layout.addWidget(reception_summary_table,0,0)
        self.setLayout(layout)
    def create_reception_summary_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.data.reception2_df))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['identifiant du colis','date prevue', 'Statut'])

        for i, (_, row) in enumerate(self.data.reception2_df.iterrows()):
            table.setItem(i, 0, QTableWidgetItem(row['identifiant du colis']))
            table.setItem(i, 1, QTableWidgetItem(str(row['date prevue'])))
            table.setItem(i, 2, QTableWidgetItem(row['Statuts']))
        table.setStyleSheet("""
            QTableWidget { background-color: white; alternate-background-color: #f5f5f5; selection-background-color: #e3f2fd; gridline-color: #e0e0e0; }
            QHeaderView::section { background-color: #f5f5f5; padding: 8px; border: 1px solid #e0e0e0; font-weight: bold; }
        """)
        table.resizeColumnsToContents()
        return table
class WarehouseMenuInteractionWidget(QWidget):
    """Widget principal de 'Menu interaction' qui regroupe les vues du module warehouse."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Titre
        title = QLabel("Warehouse Operations Menu")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Onglets
        tabs = QTabWidget()
        tabs.addTab(MenuReception(self.data), "menu reception")
        tabs.addTab(MenuExpedition(self.data), "menu expedition")
        tabs.addTab(ZoneEmballage(self.data),"zone d'emballage")
        layout.addWidget(tabs)
        self.setLayout(layout)
class StockManagerDashboardWidget(QWidget):
    """The central dashboard widget as per the image."""
    def __init__(self, data, main_app_window):
        super().__init__()
        self.data = data
        self.main_app_window = main_app_window # Reference to the main window for navigation
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Stock Manager Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Quick Metrics/KPIs (Summarized from underlying widgets)
        metrics_layout = QHBoxLayout()
        total_items = self.data.inventory_df['Quantity'].sum()
        low_stock_items = len(self.data.inventory_df[
            self.data.inventory_df['Quantity'] <= self.data.inventory_df['Min_Stock']
        ])
        pending_receptions = len(self.data.reception_df[self.data.reception_df['Status'] == 'Pending'])
        pending_expeditions = len(self.data.expedition_df[self.data.expedition_df['Status'] == 'Pending'])

        metrics_layout.addWidget(MetricCard("Total Stock", f"{total_items:,}", "Current Inventory"))
        metrics_layout.addWidget(MetricCard("Low Stock Alerts", str(low_stock_items), "Items needing reorder", "#FF9800"))
        metrics_layout.addWidget(MetricCard("Pending Receptions", str(pending_receptions), "Incoming Orders"))
        metrics_layout.addWidget(MetricCard("Pending Expeditions", str(pending_expeditions), "Outgoing Orders"))

        layout.addLayout(metrics_layout)
        layout.addSpacing(30)

        # Main Functionality Buttons/Links
        function_grid = QGridLayout()
        function_grid.setSpacing(20)

        # Real-time Inventory View
        inventory_btn = QPushButton("Real-time Inventory View")
        inventory_btn.setObjectName("nav_button")
        inventory_btn.clicked.connect(lambda: self.main_app_window.show_widget("Real-time Inventory View"))
        function_grid.addWidget(self.create_function_card(
            "Real-time Inventory View",
            "Monitor stock levels, product details, and movements.",
            inventory_btn
        ), 0, 0)

        # Storage Space Management
        storage_btn = QPushButton("Storage Space Management")
        storage_btn.setObjectName("nav_button")
        storage_btn.clicked.connect(lambda: self.main_app_window.show_widget("Storage Space Management"))
        function_grid.addWidget(self.create_function_card(
            "Storage Space Management",
            "Optimize cell usage and manage warehouse layout.",
            storage_btn
        ), 0, 1)
        #Menu interaction
        menu_interaction_btn = QPushButton("Menu interaction")
        menu_interaction_btn.setObjectName("nav_button")
        menu_interaction_btn.clicked.connect(lambda: self.main_app_window.show_widget("Menu interaction"))
        function_grid.addWidget(self.create_function_card(
            "Menu interaction",
            "Optimize cell usage and manage warehouse layout.",
            menu_interaction_btn
        ), 0, 2)

        # Generate Reports
        reports_btn = QPushButton("Generate Reports")
        reports_btn.setObjectName("nav_button")
        reports_btn.clicked.connect(lambda: self.main_app_window.show_widget("Generate Reports"))
        function_grid.addWidget(self.create_function_card(
            "Generate Reports",
            "Access stock, performance, and exception reports.",
            reports_btn
        ), 1, 0)

        # Daily Operations Planning
        planning_btn = QPushButton("Daily Operations Planning")
        planning_btn.setObjectName("nav_button")
        planning_btn.clicked.connect(lambda: self.main_app_window.show_widget("Daily Operations Planning"))
        function_grid.addWidget(self.create_function_card(
            "Daily Operations Planning",
            "Manage daily receptions, expeditions, and planning.",
            planning_btn
        ), 1, 1)

        layout.addLayout(function_grid)
        layout.addStretch()
        self.setLayout(layout)

    def create_function_card(self, title, description, button):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin: 5px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            QLabel + QLabel { /* description label */
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            QPushButton#nav_button {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton#nav_button:hover {
                background-color: #1976D2;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.addWidget(QLabel(title))
        card_layout.addWidget(QLabel(description))
        card_layout.addStretch()
        card_layout.addWidget(button, alignment=Qt.AlignRight)
        card.setLayout(card_layout)
        return card

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
                background-color: #f0f0f0;
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
             QPushButton#sidebar_button {
                background-color: #f0f0f0;
                color: #333;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 16px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton#sidebar_button:hover {
                background-color: #e0e0e0;
            }
            QPushButton#sidebar_button:checked {
                background-color: #e3f2fd;
                color: #2196F3;
                border-left: 5px solid #2196F3;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Main content area with sidebar
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Sidebar Navigation
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: white; border-right: 1px solid #e0e0e0;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(10)

        # Dashboard Button
        self.dashboard_btn = QPushButton("Stock Manager Dashboard")
        self.dashboard_btn.setObjectName("sidebar_button")
        self.dashboard_btn.setCheckable(True)
        self.dashboard_btn.setChecked(True) # Start with dashboard selected
        self.dashboard_btn.clicked.connect(lambda: self.show_widget("Stock Manager Dashboard"))
        sidebar_layout.addWidget(self.dashboard_btn)

        # Navigation Buttons (corresponding to the image)
        self.inventory_btn = QPushButton("Real-time Inventory View")
        self.inventory_btn.setObjectName("sidebar_button")
        self.inventory_btn.setCheckable(True)
        self.inventory_btn.clicked.connect(lambda: self.show_widget("Real-time Inventory View"))
        sidebar_layout.addWidget(self.inventory_btn)

        self.storage_btn = QPushButton("Storage Space Management")
        self.storage_btn.setObjectName("sidebar_button")
        self.storage_btn.setCheckable(True)
        self.storage_btn.clicked.connect(lambda: self.show_widget("Storage Space Management"))
        sidebar_layout.addWidget(self.storage_btn)


        self.menu_interaction_btn = QPushButton("Menu interaction")
        self.menu_interaction_btn.setObjectName("sidebar_button")
        self.menu_interaction_btn.setCheckable(True)
        self.menu_interaction_btn.clicked.connect(lambda: self.show_widget("Menu interaction"))
        sidebar_layout.addWidget(self.menu_interaction_btn)

        self.reports_btn = QPushButton("Generate Reports")
        self.reports_btn.setObjectName("sidebar_button")
        self.reports_btn.setCheckable(True)
        self.reports_btn.clicked.connect(lambda: self.show_widget("Generate Reports"))
        sidebar_layout.addWidget(self.reports_btn)

        self.planning_btn = QPushButton("Daily Operations Planning")
        self.planning_btn.setObjectName("sidebar_button")
        self.planning_btn.setCheckable(True)
        self.planning_btn.clicked.connect(lambda: self.show_widget("Daily Operations Planning"))
        sidebar_layout.addWidget(self.planning_btn)

        sidebar_layout.addStretch() # Push buttons to the top

        content_layout.addWidget(self.sidebar)

        # Stacked Widget for main content
        self.stacked_widget = QStackedWidget()

        # Create a QWidget to hold the stacked_widget to set it as scroll area's widget
        scroll_content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content_widget)
        scroll_content_layout.addWidget(self.stacked_widget)
        scroll_content_layout.setContentsMargins(0, 0, 0, 0) # Remove extra margins

        # Create QScrollArea and set the stacked widget as its widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_content_widget) # Set the scroll_content_widget as the widget for QScrollArea
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Typically, vertical scroll is sufficient for dashboards

        content_layout.addWidget(self.scroll_area)

        # Instantiate all main widgets
        self.dashboard_widget = StockManagerDashboardWidget(self.data, self)
        self.realtime_inventory_widget = RealtimeInventoryViewWidget(self.data)
        self.menu_interaction_widget = WarehouseMenuInteractionWidget(self.data)
        self.storage_management_widget = StorageSpaceManagementWidget(self.data)
        self.reports_widget = ReportsWidget(self.data)
        self.daily_planning_widget = DailyOperationsPlanningWidget(self.data)

        # Add widgets to the stacked widget
        self.stacked_widget.addWidget(self.dashboard_widget) # Index 0
        self.stacked_widget.addWidget(self.realtime_inventory_widget) # Index 1
        self.stacked_widget.addWidget(self.menu_interaction_widget)  # Index 2
        self.stacked_widget.addWidget(self.storage_management_widget) # Index 2
        self.stacked_widget.addWidget(self.reports_widget) # Index 3
        self.stacked_widget.addWidget(self.daily_planning_widget) # Index 4

        # Map button names to stacked widget indices
        self.widget_map = {
            "Stock Manager Dashboard": 0,
            "Real-time Inventory View": 1,
            "Menu interaction":2,
            "Storage Space Management": 3,
            "Generate Reports": 4,
            "Daily Operations Planning": 5
        }
        self.button_group = [
            self.dashboard_btn, self.inventory_btn, self.storage_btn, self.menu_interaction_btn,
            self.reports_btn, self.planning_btn
        ]

        # Show the initial dashboard view
        self.show_widget("Stock Manager Dashboard")


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

    def show_widget(self, widget_name):
        index = self.widget_map.get(widget_name)
        if index is not None:
            self.stacked_widget.setCurrentIndex(index)
            # Update sidebar button checked state
            for btn in self.button_group:
                btn.setChecked(False) # Uncheck all
            # Check the current button
            if widget_name == "Stock Manager Dashboard":
                self.dashboard_btn.setChecked(True)
            elif widget_name == "Real-time Inventory View":
                self.inventory_btn.setChecked(True)
            elif widget_name =="Menu interaction":
                self.menu_interaction_btn.setChecked(True)
            elif widget_name == "Storage Space Management":
                self.storage_btn.setChecked(True)
            elif widget_name == "Generate Reports":
                self.reports_btn.setChecked(True)
            elif widget_name == "Daily Operations Planning":
                self.planning_btn.setChecked(True)
        else:
            print(f"Widget '{widget_name}' not found.")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data_and_ui)
        self.timer.start(60000)  # Update every 60 seconds (1 minute)

    def update_data_and_ui(self):
        print("Updating data and UI...")
        self.data.generate_sample_data()  # Regenerate data for demonstration

        # Manually trigger updates for visible widgets if needed,
        # or re-initialize if the widget's init_ui cleans up correctly.
        # For simplicity, we'll re-init if the widget handles clearing its layout properly.
        self.dashboard_widget.init_ui() # Refresh dashboard metrics
        self.realtime_inventory_widget.init_ui() # Refresh inventory
        self.reports_widget.init_ui() # Refresh reports, including performance
        self.daily_planning_widget.init_ui() # Refresh orders within daily planning
        # StorageSpaceManagementWidget is mostly static in this example, no direct refresh needed.

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