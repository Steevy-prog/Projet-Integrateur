class ShipmentTrackingWidget(QWidget):
    """Widget for tracking client's shipments."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("Shipment Tracking")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color:#6C63FF;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        filter_search_layout = QHBoxLayout()
        filter_search_layout.setSpacing(15)

        search_label = QLabel("Search Package:")
        search_label.setStyleSheet("font-size: 15px; color: #FFFFFF;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter package ID or product name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #6C63FF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_movements)

        type_label = QLabel("Filter by type:")
        type_label.setStyleSheet("font-size: 15px; color: #666;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All', 'Outbound', 'In Transit', 'Received', 'Return'])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 20px;
            }
        """)
        self.type_combo.currentTextChanged.connect(self.filter_movements)

        filter_search_layout.addWidget(search_label)
        filter_search_layout.addWidget(self.search_input, 3)
        filter_search_layout.addWidget(type_label)
        filter_search_layout.addWidget(self.type_combo, 1)
        filter_search_layout.addStretch()

        layout.addLayout(filter_search_layout)

        self.movements_table = self.create_movements_table()
        layout.addWidget(self.movements_table)

        self.setLayout(layout)
        self.update_movements_table(self.data.movement_history) # Initial population

    def create_movements_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Timestamp', 'Package ID', 'Type', 'Location', 'Description'])

        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #E6E6FF;
                selection-color: #333333;
                gridline-color: #F0F2F5;
            }
            QHeaderView::section {
                background-color: #6C63FF;
                color: #FFFFFF;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                text-align: left;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #6C63FF;
                color: #FFFFFF;
            }
        """)

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()

        return table

    def filter_movements(self):
        search_text = self.search_input.text().lower()
        movement_type = self.type_combo.currentText()

        filtered_movements = []
        for movement in self.data.movement_history:
            if search_text and search_text not in movement['Package_ID'].lower() and search_text not in movement['Product_Name'].lower():
                continue
            if movement_type != 'All' and movement['Movement_Type'] != movement_type:
                continue
            filtered_movements.append(movement)

        self.update_movements_table(filtered_movements)

    def update_movements_table(self, movements):
        sorted_movements = sorted(movements, key=lambda x: x['Timestamp'], reverse=True)
        self.movements_table.setRowCount(len(sorted_movements))

        accent_color = "#6C63FF"

        for i, movement in enumerate(sorted_movements):
            self.movements_table.setItem(i, 0, QTableWidgetItem(movement['Timestamp'].strftime('%H:%M %b %d')))
            self.movements_table.setItem(i, 1, QTableWidgetItem(movement['Package_ID']))

            type_item = QTableWidgetItem(movement['Movement_Type'])
            type_item.setBackground(QColor(accent_color))
            type_item.setForeground(QColor('#FFFFFF'))
            self.movements_table.setItem(i, 2, type_item)

            self.movements_table.setItem(i, 3, QTableWidgetItem(movement['Location']))
            self.movements_table.setItem(i, 4, QTableWidgetItem(movement['Description']))

        self.movements_table.resizeColumnsToContents()


class InquiryDetailDialog(QDialog):
    """Dialog to display details of an inquiry and allow status update."""
    def __init__(self, inquiry_data, parent=None):
        super().__init__(parent)
        self.inquiry_data = inquiry_data
        self.setWindowTitle(f"Inquiry Details: {self.inquiry_data['ID']}")
        self.setFixedSize(500, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLabel.title {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTextEdit, QComboBox {
                padding: 20px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QTextEdit:focus, QComboBox:focus {
                border: 1px solid #F44336;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        title_label = QLabel(f"Inquiry: {self.inquiry_data['ID']}")
        title_label.setProperty("class", "title")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.addRow("Type:", QLabel(self.inquiry_data['Type']))
        form_layout.addRow("Related Product:", QLabel(self.inquiry_data['Related_Product']))
        form_layout.addRow("Reported By:", QLabel(self.inquiry_data['Reported_By_Org']))
        form_layout.addRow("Reported Time:", QLabel(self.inquiry_data['Reported_Time'].strftime('%Y-%m-%d %H:%M')))

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        description_text = QTextEdit()
        description_text.setText(self.inquiry_data['Description'])
        description_text.setReadOnly(True)
        layout.addWidget(description_text)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Update Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Open', 'In Progress', 'Resolved', 'Closed'])
        self.status_combo.setCurrentText(self.inquiry_data['Status'])
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Status")
        save_button.clicked.connect(self.save_status)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #6C63FF;")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_status(self):
        new_status = self.status_combo.currentText()
        if new_status != self.inquiry_data['Status']:
            # In a real app, this would update the database
            self.inquiry_data['Status'] = new_status # Update in-memory data
            QMessageBox.information(self, "Status Updated", f"Inquiry {self.inquiry_data['ID']} status updated to {new_status}.")
            self.accept()
        else:
            self.accept()

class NewInquiryDialog(QDialog):
    """Dialog to report a new inquiry."""
    def __init__(self, data, client_id, parent=None):
        super().__init__(parent)
        self.data = data
        self.client_id = client_id
        self.setWindowTitle("Report New Inquiry")
        self.setFixedSize(450, 500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #F44336;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
        """)

        self.inquiry_type_combo = QComboBox()
        self.inquiry_type_combo.addItems(['Missing Package', 'Damaged Item', 'Incorrect Order', 'Billing Issue', 'General Support', 'Other'])
        layout.addRow("Inquiry Type:", self.inquiry_type_combo)

        self.related_product_combo = QComboBox()
        self.related_product_combo.addItem("— None (General Inquiry) —", None)
        for product in self.data.products_df.itertuples():
            self.related_product_combo.addItem(product.Name, product.ID)
        layout.addRow("Related Product:", self.related_product_combo)

        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Provide detailed information about your inquiry...")
        layout.addWidget(self.description_text)

        button_layout = QHBoxLayout()
        report_button = QPushButton("Submit Inquiry")
        report_button.clicked.connect(self.report_inquiry)
        button_layout.addWidget(report_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #CCCCCC;")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addChildLayout(button_layout)
        self.setLayout(layout)

    def report_inquiry(self):
        inquiry_type = self.inquiry_type_combo.currentText()
        related_product_id = self.related_product_combo.currentData()
        related_product_name = self.related_product_combo.currentText() if related_product_id else "N/A"
        description = self.description_text.toPlainText()

        if not description:
            QMessageBox.warning(self, "Input Error", "Please provide a detailed description for your inquiry.")
            return

        new_inquiry = {
            'ID': f'INQ{len(self.data.inquiries) + 1:03d}',
            'Type': inquiry_type,
            'Related_Product': related_product_name,
            'Reported_By_Org': self.client_id,
            'Reported_Time': datetime.datetime.now(),
            'Status': 'Open',
            'Description': description
        }
        self.data.inquiries.append(new_inquiry) # Add to in-memory list
        QMessageBox.information(self, "Success", "Inquiry reported successfully!")
        self.accept()

class ClientInquiriesWidget(QWidget):
    """Widget for viewing and managing client inquiries."""

    def __init__(self, data, client_id):
        super().__init__()
        self.data = data
        self.client_id = client_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        title = QLabel("My Inquiries")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6C63FF;")

        report_inquiry_btn = QPushButton("Submit New Inquiry")
        report_inquiry_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(244, 67, 54, 0.2);
                transition: all 0.2s ease-in-out;
            }
            QPushButton:hover {
                background-color: #5247D6;
                transform: translateY(-2px);
            }
        """)
        report_inquiry_btn.clicked.connect(self.report_new_inquiry)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(report_inquiry_btn)
        layout.addLayout(header_layout)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        open_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Open'])
        in_progress_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'In Progress'])
        resolved_inquiries = len([i for i in self.data.inquiries if i['Status'] == 'Resolved' or i['Status'] == 'Closed'])

        stats_layout.addWidget(self.create_inquiry_stat_card("Open Inquiries", open_inquiries, "#F44336"))
        stats_layout.addWidget(self.create_inquiry_stat_card("In Progress", in_progress_inquiries, "#FFC107"))
        stats_layout.addWidget(self.create_inquiry_stat_card("Resolved/Closed", resolved_inquiries, "#4CAF50"))
        layout.addLayout(stats_layout)
        self.inquiries_table = self.create_inquiries_table()
        layout.addWidget(self.inquiries_table)

        self.setLayout(layout)
        self.update_inquiries_table(self.data.inquiries) # Initial population

    def create_inquiry_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 18px 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666666; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        return card

    def create_inquiries_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'Type', 'Related Product', 'Time', 'Status'])
    
    # Set header visibility BEFORE styling
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().setMinimumHeight(45)  # Ensure header has proper height
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(40)

        table.setStyleSheet("""
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            font-size: 14px;
            selection-background-color: #FFEBEE;
            selection-color: #333333;
            gridline-color: #F0F2F5;
        }
        QHeaderView::section {
            background-color: #6C63FF;
            color: #FFFFFF;
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 15px;
            text-align: left;
            height: 90px;
            min-height: 45px;
        }
        QHeaderView::section:first {
            border-top-left-radius: 10px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 10px;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QTableWidget::item:selected {
            background-color: #FFEBEE;
            color: #333333;
        }
    """)

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.cellDoubleClicked.connect(self.view_inquiry_details)
    
    # Remove the test row - it's not needed and might interfere
    # The table will be populated by update_inquiries_table()
    
        return table

    def update_inquiries_table(self, inquiries):
        sorted_inquiries = sorted(inquiries, key=lambda x: x['Reported_Time'], reverse=True)
        self.inquiries_table.setRowCount(len(sorted_inquiries))

        for i, inquiry in enumerate(sorted_inquiries):
            self.inquiries_table.setItem(i, 0, QTableWidgetItem(inquiry['ID']))
            self.inquiries_table.setItem(i, 1, QTableWidgetItem(inquiry['Type']))
            self.inquiries_table.setItem(i, 2, QTableWidgetItem(inquiry['Related_Product']))
            self.inquiries_table.setItem(i, 3, QTableWidgetItem(inquiry['Reported_Time'].strftime('%m/%d %H:%M')))

            status_item = QTableWidgetItem(inquiry['Status'])
            status_colors = {
                'Open': '#F44336',
                'In Progress': '#FFC107',
                'Resolved': '#4CAF50',
                'Closed': '#9E9E9E' # Grey for closed
            }
            status_item.setBackground(QColor(status_colors.get(inquiry['Status'], '#E0E0E0')))
            status_item.setForeground(QColor('#FFFFFF'))
            if inquiry['Status'] == 'In Progress':
                status_item.setForeground(QColor('#333333'))
            self.inquiries_table.setItem(i, 4, status_item)
        self.inquiries_table.resizeColumnsToContents()


    def view_inquiry_details(self, row, column):
        inquiry_id = self.inquiries_table.item(row, 0).text()
        inquiry_data = next((i for i in self.data.inquiries if i['ID'] == inquiry_id), None)

        if inquiry_data:
            dialog = InquiryDetailDialog(inquiry_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.update_inquiries_table(self.data.inquiries) # Refresh table if status changed

    def report_new_inquiry(self):
        dialog = NewInquiryDialog(self.data, self.client_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_inquiries_table(self.data.inquiries)
            
class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        from helpbot import ChatBot
        
        # --- Card 1: AI Assistant Placeholder --
        ai_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #F8F0FA;
                border-radius: 16px;
                border: 1px solid #E0E0E0
                padding: 20px;
                box-shadow: 0 4px 5px rgba(108,99,255,0.07)
            }
        """)
        ai_layout = QVBoxLayout(ai_card)
        ai_title = QLabel("🤖 AI Assistant ")
        ai_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #6C63FF;")
        ai_desc = QLabel("An Intelligent assistant that will answer all your questions about the platform.")
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("font-size: 18px; color:#333")
        ai_btn = QPushButton("Ask your questions")
        ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5247D6;;
            }
        """)
        ai_btn.clicked.connect(self.open_helpbot_dialog)  # Placeholder for AI chat functionality
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(ai_desc)
        ai_layout.addWidget(ai_btn)
        ai_layout.addWidget(ai_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        ai_layout.addStretch()
        
        # --- Card 2: Report a Bug ---
        bug_card = QFrame()
        ai_card.setStyleSheet("""
            QFrame {
                background-color: #F8F0FA;
                border-radius: 16px;
                border: 1px solid #E0E0E0
                padding: 20px;
                box-shadow: 0 4px 5px rgba(108,99,255,0.07)
            }
        """)
        bug_layout= QVBoxLayout(bug_card)
        bug_title = QLabel("🐞 Report a Bug")
        bug_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
        bug_desc = QLabel("If you encounter a problem or bug, please let our IT support know so we can fix it quickly.")
        bug_desc.setWordWrap(True)
        bug_desc.setStyleSheet("font-size: 18px; color: #333;")
        report_btn = QPushButton("Report a Bug")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 12x 20px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        report_btn.clicked.connect(self.open_bug_report_dialog)
        bug_layout.addWidget(bug_title)
        bug_layout.addWidget(bug_title)
        bug_layout.addWidget(bug_desc)
        bug_layout.addWidget(report_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        bug_layout.addStretch()
        
        layout.addWidget(ai_card)
        layout.addWidget(bug_card)
        layout.addStretch()
        
    def open_helpbot_dialog(self):
        self.chatbot_window = ChatBot()
        self.chatbot_window.show()
        
    def open_bug_report_dialog(self):
        dialog = BugReportDialog(self)
        dialog.exec()
        
class BugReportDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Report a Bug")
        self.setFixedSize(450,350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        self.setStyleSheet(""""
            QDialog{
                background-color: #FFFDE7;
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #333px;
            }
            QTextEdit {
                border: 1px solid #FFD180;
                border-radius: 8px;
                font-size: 15px;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 10 24px;
            }
        """)
        label = QLabel("Describe the bug you encounter:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Please provide as much details as possible")
        
        self.send_btn  = QPushButton("Send to IT Support")
        self.send_btn.clicked.connect(self.send_bug_report)
        
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addStretch()
        layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignRight)
       
    def send_bug_report(self):
        import smtplib
        from email.mime.text import MIMEText

        bug_text = self.text_edit.toPlainText().strip()
        if not bug_text:
            QMessageBox.warning(self, "Input Error", "Please describe the bug before sending.")
            return

        # --- Email sending logic (update with your IT support email) ---
        support_email = "steevy.tongoue@2029.ucac-icam.com"
        subject = "Bug Report from Client Dashboard"
        body = bug_text

        try:
            
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "scarobotinterne@gmail.com"
            smtp_password = "vzeokmezwltpoqbt"

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = support_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [support_email], msg.as_string())

            QMessageBox.information(self, "Sent", "Your bug report has been sent to IT support. Thank you!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send bug report.\n\n{e}")