import sys
import qtawesome as qta
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from services.jsonParser import combine_pharmacy_data, combine_pharmacy_admin
from services.client import SocketClient
from functools import partial
from components.custom_button import CustomButton  

class PatientsTableApp(QWidget):
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
        self.layout.setContentsMargins(40, 40, 40, 20)

        self.setLayout(self.layout)
        
        # Create and add the search bar
        if self.isAdmin:
            
            self.search_widget = QWidget()
            self.search_widget.setObjectName('search_widget')
            self.searchLayout = QHBoxLayout(self.search_widget)
            self.searchLayout.setContentsMargins(15, 7, 15, 7)
            self.searchLayout.setSpacing(0)
            
            search_label = QLabel()
            pixmap = QPixmap('assets/search.png')
            search_pixmap = pixmap.scaledToWidth(20, Qt.SmoothTransformation)
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

        # Create table widget
        self.patient_table = QTableWidget()
        self.patient_table.setShowGrid(False)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.setWordWrap(False)
        self.layout.addWidget(self.patient_table)

        # Add a label for title
        copyright_txt = QLabel("Copyright © 2024 by Tim IT RS Mata Makassar")
        copyright_txt.setObjectName('ext_txt')
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
        if self.isAdmin:
            self.orders = combine_pharmacy_admin()
        else:
            self.orders = combine_pharmacy_data()
        self.populate_table()

    def initSocketClient(self):
        self.socket_client = SocketClient()
        # self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()
    
    @pyqtSlot(list)
    def send_message(self, patient_data):
        message = f"NORM: {patient_data[0]}; Name: {patient_data[1]}; isCall: 1"
        self.socket_client.send_message(message)
        # self.name_text.clear()

    def populate_table(self):
        # Clear the table
        self.patient_table.clear()

        # Set the column count and headers
        headers = ['NORM', 'NAMA PASIEN', 'DOKTER', 'ASAL PASIEN']
        if self.isAdmin:
            headers.append('AKSI')
        self.patient_table.setColumnCount(len(headers))
        self.patient_table.setHorizontalHeaderLabels(headers)

        if self.isAdmin:
            filter_text = self.search_bar.text().lower()
        else:
            filter_text = ""

        # Filter orders based on search text matching NAMA_LENGKAP or NORM
        filtered_orders = [order for order in self.orders if filter_text in order['NAMA_LENGKAP'].lower() or filter_text in order['NORM'].lower()]

        self.patient_table.setRowCount(len(filtered_orders))

        for row, order in enumerate(filtered_orders):
            self.patient_table.setItem(row, 0, QTableWidgetItem(order['NORM']))
            self.patient_table.setItem(row, 1, QTableWidgetItem(order['NAMA_LENGKAP']))
            self.patient_table.setItem(row, 2, QTableWidgetItem(order['DOKTER']))

            asal_patient = QTableWidgetItem(order['ASAL_PASIEN'])
            asal_patient.setTextAlignment(Qt.AlignCenter)
            self.patient_table.setItem(row, 3, asal_patient)
            
            if self.isAdmin:
                button = CustomButton(' Panggil', "assets/speaker.png")
                button.setObjectName('panggil_button')
                button.setMinimumHeight(25)
                button.clicked.connect(partial(self.send_message, [order['NORM'], order['NAMA_LENGKAP']]))

                # Create a drop shadow effect
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(4)  # Set a smaller blur radius for a sharper shadow
                shadow.setXOffset(0)     # Offset shadow to the right
                shadow.setYOffset(5)     # Offset shadow to the bottom
                shadow.setColor(QColor(0, 0, 0, 100))  # RGBA

                
                
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(button)
                button_layout.setAlignment(Qt.AlignCenter)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_widget.setLayout(button_layout)

                button_widget.setGraphicsEffect(shadow)

                null_text = QLabel("")
                if order['STATUS_FARMASI'] == '2':
                    self.patient_table.setCellWidget(row, 4, null_text)
                        
                else:
                    if order['STATUS_ORDER_RESEP'] == '1':
                        button.setEnabled(False)
                    self.patient_table.setCellWidget(row, 4, button_widget)
                    
                        

        header = self.patient_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        if self.isAdmin:
            header.setSectionResizeMode(4, QHeaderView.Fixed)
            self.patient_table.setColumnWidth(4, 115)
            
        self.patient_table.resizeRowsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_window = PatientsListApp(isAdmin=True)
    main_window.show()
    sys.exit(app.exec_())
