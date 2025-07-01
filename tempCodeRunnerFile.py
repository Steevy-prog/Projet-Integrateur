        for item_data in self.order_data['Items']:
            items_list.addItem(f"- {item_data[2]} (ID: {item_data[0]}), Price: ${item_data[4]:.2f}")
        layout.addWidget(items_list)

        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #999999;")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

class ProductCreationPopup(QDialog):