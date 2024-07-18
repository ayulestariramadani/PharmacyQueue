import sys
import qtawesome as qta
from pathlib import Path
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QGraphicsDropShadowEffect, QGraphicsDropShadowEffect, QHeaderView
from PyQt5.QtGui import QPixmap, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from services.jsonParser import combine_pharmacy_data, combine_pharmacy_admin, add_antrian_farmasi, delete_antrian_farmasi, update_antrian_farmasi
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
        self.selected_row = None
        
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

        # Setup QTimer to reload data every 1 seconds 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(3000)  # 1000 milliseconds = 1 seconds

        self.orders = []
        self.queue = 0

    def removeText(self):
        self.search_bar.setText("")
        
    def load_data(self):
        if self.isAdmin:
            self.orders, self.queue = combine_pharmacy_admin()
        else:
            self.orders = combine_pharmacy_data()
        self.populate_table()
        

    def initSocketClient(self):
        self.socket_client = SocketClient()
        # self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()
    
    @pyqtSlot(list)
    def send_message(self, patient_data):
        message = f"NORM: {patient_data[0]}; Name: {patient_data[1]}; ID: {patient_data[2]}"
        self.socket_client.send_message(message)
        
        # self.name_text.clear()
    
    def add_data(self, data):
        status_antrian = data[0] if data[0] is not None else ''
        norm = data[1] if data[1] is not None else ''
        nama_lengkap = data[2] if data[2] is not None else ''
        dokter = data[3] if data[3] is not None else ''
        asal = data[4] if data[4] is not None else ''
        self.load_data()

        add_antrian_farmasi(status_antrian, norm, nama_lengkap, dokter, asal)
    
    def delete_data(self, id):
        delete_antrian_farmasi(id=id)
        self.selected_row = None
        self.load_data()
    
    def update_data(self, id):
        update_antrian_farmasi(id=id, is_active=self.queue+1)
        self.load_data()

    def panggil_pasien(self, patient_data, row):
        self.send_message(patient_data=patient_data)
        if self.selected_row is not None:
            color = QColor(0,52,104)  
            # Set the background and foreground colors for the selected row
            for c in range(self.patient_table.columnCount()+1):
                item = self.patient_table.item(self.selected_row, c)
                if item:
                    item.setBackground(QBrush(color))

        self.selected_row = row
        self.apply_row_style(row)
        
        
    def apply_row_style(self, row):
        color = QColor(207,171,122) 
        # Set the background and foreground colors for the selected row
        for c in range(self.patient_table.columnCount()+1):
            item = self.patient_table.item(row, c)
            if item:
                item.setBackground(QBrush(color))

        # Update the table widget to reflect the color change
        self.patient_table.viewport().repaint()

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
                

                antrian_button = CustomButton(' Antri', "assets/add.png")
                antrian_button.setObjectName('antrian_button')
                antrian_button.setMinimumHeight(25)
                

                selesai_button = CustomButton(' Selesai', "assets/check.png")
                selesai_button.setObjectName('selesai_button')
                selesai_button.setMinimumHeight(25)
                # if 'ID' in order:
                #     button.clicked.connect(partial(self.send_message, [order['NORM'], order['NAMA_LENGKAP'], order['ID']]))
                #     selesai_button.clicked.connect(partial(self.delete_data, order['ID']))

                # Create a drop shadow effect
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(4)  # Set a smaller blur radius for a sharper shadow
                shadow.setXOffset(0)     # Offset shadow to the right
                shadow.setYOffset(5)     # Offset shadow to the bottom
                shadow.setColor(QColor(0, 0, 0, 100))  # RGBA

                
                
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(button)
                button_layout.addWidget(selesai_button)
                button_layout.setAlignment(Qt.AlignCenter)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_widget.setLayout(button_layout)

                button_widget.setGraphicsEffect(shadow)

                null_text = QLabel("")
                if 'STATUS_ORDER_RESEP' in order:
                    if order['STATUS_FARMASI'] == '2' and order['STATUS_ORDER_RESEP'] == '2':
                        self.patient_table.setCellWidget(row, 4, null_text)
                            
                    else:
                        if order['STATUS_ORDER_RESEP'] == '1':
                            antrian_button.setEnabled(False)
                        self.patient_table.setCellWidget(row, 4, antrian_button)
                        antrian_button.clicked.connect(partial(self.add_data, [order['QUEUE'], order['NORM'], order['NAMA_LENGKAP'], order['DOKTER'], order['ASAL_PASIEN']]))
                elif 'ID' in order:
                    button.clicked.connect(partial(self.panggil_pasien, [order['NORM'], order['NAMA_LENGKAP'], order['ID']], row))
                    selesai_button.clicked.connect(partial(self.delete_data, order['ID']))
                    if order['IS_ACTIVE'] == 0:
                        self.patient_table.setCellWidget(row, 4, antrian_button)
                        antrian_button.clicked.connect(partial(self.update_data, order['ID']))
                    else:
                        self.patient_table.setCellWidget(row, 4, button_widget)

                
                    
                        
        if self.isAdmin:
            print(self.search_bar.text)
            if self.selected_row is not None and self.search_bar.text=="":
                    self.apply_row_style(self.selected_row)
            self.patient_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.patient_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.patient_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.patient_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.patient_table.setStyleSheet("border: none;")
        header = self.patient_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        if self.isAdmin:
            header.setSectionResizeMode(4, QHeaderView.Fixed)
            self.patient_table.setColumnWidth(4, 200)
            
        self.patient_table.resizeRowsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_window = PatientsListApp(isAdmin=True)
    main_window.show()
    sys.exit(app.exec_())
