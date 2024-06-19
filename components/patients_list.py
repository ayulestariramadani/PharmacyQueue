# file: display_data.py
import sys
import json
import qtawesome as qta
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from services.jsonParser import combine_pharmacy_data
from services.client import SocketClient
from functools import partial  

class PatientsListApp(QWidget):
    # Define custom signal
    order_selected = pyqtSignal(object)

    def __init__(self, isAdmin=False):
        super().__init__()
        self.initSocketClient()

        self.isAdmin = isAdmin
        self.setObjectName('PatientsListApp')

        self.setWindowTitle("Pharmacy Orders")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        if self.isAdmin:
            # Create and add the search bar
            self.search_widget = QWidget()
            self.search_widget.setObjectName('search_widget')
            self.searchLayout = QHBoxLayout(self.search_widget)
            self.searchLayout.setContentsMargins(15, 7, 15, 7)
            self.searchLayout.setSpacing(0)
            
            search_label = QLabel()
            pixmap = QPixmap('search.png')
            search_pixmap = pixmap.scaled(20, 20)
            search_label.setPixmap(search_pixmap)

            close_button = QPushButton()
            close_button.setObjectName('close_button')
            close_button.setIcon(qta.icon('fa.close', color='#919191'))
            close_button.setToolTip('Delete')
            close_button.clicked.connect(self.removeText)

            self.search_bar = QLineEdit(self)
            self.search_bar.setObjectName('search_bar')
            self.search_bar.setPlaceholderText("Search patients by Name or NORM...")
            self.search_bar.textChanged.connect(self.populate_table)

            self.searchLayout.addWidget(search_label)
            self.searchLayout.addWidget(self.search_bar)
            self.searchLayout.addWidget(close_button)

            self.layout.addWidget(self.search_widget)

        
        # Add a label for title
        title = QLabel("Antrian Order Resep")
        title.setObjectName('title')
        title.setAlignment(Qt.AlignLeft)
        # Add title to main layout
        self.layout.addWidget(title)

        # Create a QListWidget
        self.patient_list = QListWidget()
        self.patient_list.setSpacing(0)
        self.layout.addWidget(self.patient_list)

        # Add a label for title
        copyright_txt = QLabel("Copyright © 2024 by Tim IT RS Mata Makassar")
        copyright_txt.setAlignment(Qt.AlignLeft)
        # Add copyright_txt to main layout
        self.layout.addWidget(copyright_txt)
        
        # Load data automatically when the app starts
        self.load_data()

        # Setup QTimer to reload data every 3 seconds 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(3000)  # 3000 milliseconds = 3 seconds

        self.orders = []

    def removeText(self):
        self.search_bar.setText("")
    def load_data(self):
        self.orders = combine_pharmacy_data()
        self.populate_table()

    def initSocketClient(self):
        self.socket_client = SocketClient()
        # self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()
    
    @pyqtSlot(list)
    def send_message(self, patient_data):
        message = f"NORM: {patient_data[0]}, Name: {patient_data[1]}, isCall: 1"
        self.socket_client.send_message(message)
        # self.name_text.clear()

    def populate_table(self):
        # Clear list when update_filter is accessed
        self.patient_list.clear()

        if self.isAdmin:
            filter_text = self.search_bar.text().lower()
        else:
            filter_text = ""
        
        # Filter orders based on search text matching NAMA_LENGKAP or NORM
        filtered_orders = [order for order in self.orders if filter_text in order['NAMA_LENGKAP'].lower() or filter_text in order['NORM'].lower()]

        if filtered_orders:
            for order in filtered_orders:
                list_item = QListWidgetItem()

                list_widget = QWidget()
                list_widget.setObjectName('list_widget')

                list_layout = QHBoxLayout()
                list_layout.setContentsMargins(0, 0, 0, 0)
                list_layout.setSpacing(0)

                # Add a label for norm
                norm_text = QLabel(f"{order['NORM']}")
                norm_text.setObjectName('patient_list_item')
                norm_text.setFixedSize(100, 30)

                list_layout.addWidget(norm_text)

                # Add a label for name_text
                name_text = QLabel(f"{order['NAMA_LENGKAP']}")
                name_text.setObjectName('patient_list_item')
                name_text.setFixedSize(250, 30)

                list_layout.addWidget(name_text)

                if self.isAdmin:
                    # Add a label for asal_text
                    asal_text = QLabel(f"{order['ASAL_PASIEN']}")
                    asal_text.setObjectName('patient_list_item')
                    asal_text.setFixedSize(200, 30)
                    asal_text.setAlignment(Qt.AlignCenter)

                    list_layout.addWidget(asal_text)

                    # Add a button
                    panggil_button = QPushButton("Panggil")
                    panggil_button.setObjectName('panggil_button')
                    panggil_button.setFixedSize(100, 30)

                    # Connect button to slot to emit order data
                    panggil_button.clicked.connect(partial(self.send_message, [order['NORM'], order['NAMA_LENGKAP']]))

                    list_layout.addWidget(panggil_button)

                list_layout.addStretch()

                # Set size for list item
                list_layout.setSizeConstraint(QLayout.SetFixedSize)
                list_widget.setLayout(list_layout)
                list_item.setSizeHint(list_widget.sizeHint())

                # Create list item to List widget
                self.patient_list.addItem(list_item)
                self.patient_list.setItemWidget(list_item, list_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_window = PatientsListApp(isAdmin=True)
    main_window.show()
    sys.exit(app.exec_())
