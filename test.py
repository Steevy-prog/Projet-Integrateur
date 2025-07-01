import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QFormLayout,
    QPushButton, QHBoxLayout, QListWidget
)

class TaskDetailDialog(QDialog):
    """Dialog to display details of a selected task with new design."""
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setWindowTitle(f"Task Details: {self.task_data['Task_id']}")
        self.setFixedSize(500, 550)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border-radius: 15px;
            }
            QLabel {
                font-size: 15px;
                color: #212121;
                margin-bottom: 7px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #212121;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #5247D6;
            }
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                min-height: 150px;
                color: #333333;
            }
            QListWidget::item {
                padding: 5px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                color: #212121;
            }
        """)

        title_label = QLabel(f"Task: {self.task_data['Task_id']}")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # Task detail form
        form_layout = QFormLayout()
        # Simulated product name list
        product_names = ["Box", "Tape", "Scissors"]
        form_layout.addRow("Product(s):", QLabel(", ".join(product_names)))
        form_layout.addRow("Items Count:", QLabel(str(self.task_data['Items_Count'])))
        form_layout.addRow("Estimated Time (min):", QLabel(str(self.task_data['duree'])))

        status_label = QLabel(self.task_data['status'])
        status_label.setStyleSheet("color: #000000; font-weight: bold;")
        form_layout.addRow("Status:", status_label)

        form_layout.addRow("Priority:", QLabel(self.task_data['priority']))
        form_layout.addRow("Due Time:", QLabel(str(self.task_data['date-ech'])))
        layout.addLayout(form_layout)

        # Items list
        items_list_label = QLabel("Items to Pick/Pack:")
        layout.addWidget(items_list_label)
        items_list = QListWidget()
        items_list.addItem("- Check quality")
        items_list.addItem("- Scan barcode")
        layout.addWidget(items_list)

        # Buttons
        button_layout = QHBoxLayout()

        complete_button = QPushButton("Mark as Completed")
        complete_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(complete_button)

        cancel_button = QPushButton("Cancel Task")
        cancel_button.setStyleSheet("background-color: #F44336; color: white;")
        button_layout.addWidget(cancel_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #999999; color: white;")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

# ---------- Main test driver ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dummy_task_data = {
        "Task_id": "TABCD1",
        "Colis": "COLIS456",
        "Items_Count": 2,
        "duree": 45,
        "status": "Pending",
        "priority": "High",
        "date-ech": "2025-07-05"
    }

    dialog = TaskDetailDialog(dummy_task_data)
    dialog.exec()