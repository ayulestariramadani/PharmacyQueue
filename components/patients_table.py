import sys
import os
import qtawesome as qta
from pathlib import Path
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QGraphicsDropShadowEffect, QGraphicsDropShadowEffect, QHeaderView
from PyQt5.QtGui import QPixmap, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from services.jsonParser import combine_pharmacy_data, combine_pharmacy_admin, delete_antrian_farmasi, update_antrian_farmasi
from services.client import SocketClient
from functools import partial
from components.custom_button import CustomButton
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import SheetTitleException
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime
import logging
import pandas as pd

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
        title = QLabel("Antrian Resep Apotik")
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
        message = f"NORM: {patient_data[0]}; Name: {patient_data[1]}; ID: {patient_data[2]}; Call_Name: {patient_data[3]}"
        self.socket_client.send_message(message)
        
        # self.name_text.clear()
    
    def delete_data(self, id):
        delete_antrian_farmasi(id=id)
        self.selected_row = None
        self.load_data()
    
    def update_data(self, id, status_antrian, nama_lengkap):
        update_antrian_farmasi(id=id, is_active=self.queue+1)
        self.add_data_to_excel(status_antrian, nama_lengkap)
        self.load_data()

    def panggil_pasien(self, patient_data, row, queue):
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
        self.update_data_in_excel(queue)
        
        
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

                call_name  = CustomButton('', "assets/speaker.png")
                call_name.setObjectName('call_name')
                call_name.setMinimumHeight(25)

                # Create a drop shadow effect
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(4)  # Set a smaller blur radius for a sharper shadow
                shadow.setXOffset(0)     # Offset shadow to the right
                shadow.setYOffset(5)     # Offset shadow to the bottom
                shadow.setColor(QColor(0, 0, 0, 100))  # RGBA

                
                
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(call_name)
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
                elif 'ID' in order:
                    call_name.clicked.connect(partial(self.panggil_pasien, [order['NORM'], order['NAMA_LENGKAP'], order['ID'], "1"], row, order['QUEUE']))
                    button.clicked.connect(partial(self.panggil_pasien, [order['NORM'], order['NAMA_LENGKAP'], order['ID'], "0"], row, order['QUEUE']))
                    selesai_button.clicked.connect(partial(self.delete_data, order['ID']))
                    if order['IS_ACTIVE'] == 0:
                        self.patient_table.setCellWidget(row, 4, antrian_button)
                        antrian_button.clicked.connect(partial(self.update_data, order['ID'], order['QUEUE'], order['NAMA_LENGKAP']))
                    else:
                        self.patient_table.setCellWidget(row, 4, button_widget)
              
        if self.isAdmin:
            if self.selected_row is not None and self.search_bar.text()=="":
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
            self.patient_table.setColumnWidth(4, 250)
            
        self.patient_table.resizeRowsToContents()
    
    def add_data_to_excel(self, queue, name):
        print('-------------------ADD DATA----------------')
        print('-------------------ADD DATA----------------')
        print('-------------------ADD DATA----------------')
        now = datetime.now()
        year_str = now.strftime('%Y')
        month_str = now.strftime('%m ANTRIAN APOTEK %B %Y').upper()
        today_str = now.strftime('%d')
        arrive = now.strftime("%H:%M")
        # Define the folder name based on the current year
        folder_name = year_str

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Define the Excel file name based on the current month
        file_name = os.path.join(folder_name, f'{month_str}.xlsx')

        # Check if the file exists and load or create a new DataFrame
        if not os.path.exists(file_name):
            df = pd.DataFrame(columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=today_str, index=False)
        else:
            try:
                df = pd.read_excel(file_name, sheet_name=today_str, dtype={'Queue': str})
            except ValueError:
                df = pd.DataFrame(columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])

        queue_str = f'{int(queue):04}'
        # Append the new data to the DataFrame
        new_data = pd.DataFrame([[None ,queue_str, name, arrive, None, None]], columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
        
        # Add index and update the DataFrame
        if df.empty:
            new_data['No'] = [1]
        else:
            new_data['No'] = [df['No'].max() + 1]
        df = pd.concat([df, new_data], ignore_index=True)

        # Remove old total and average rows if they exist
        df = df[df['Queue'] != 'Total']
        df = df[df['Queue'] != 'Average']

        # Calculate total and average waiting time
        total_waiting_time = df['Lama Waktu Tunggu (menit)'].sum(skipna=True)
        average_waiting_time = df['Lama Waktu Tunggu (menit)'].mean(skipna=True)

        total_row = pd.DataFrame([[None, 'Total', None, None, None, total_waiting_time]], columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
        average_row = pd.DataFrame([[None, 'Average', None, None, None, average_waiting_time]], columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
        df = pd.concat([df, total_row, average_row], ignore_index=True)

        # Save the DataFrame back to the Excel file, specifying the sheet name
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name=today_str, index=False)
    
    def update_data_in_excel(self, queue):
        print('-------------------UPDATE DATA----------------')
        print('-------------------UPDATE DATA----------------')
        print('-------------------UPDATE DATA----------------')

        now = datetime.now()
        arrive = now.strftime("%H:%M")

        year_str = now.strftime('%Y')
        month_str = now.strftime('%m ANTRIAN APOTEK %B %Y').upper()
        today_str = now.strftime('%d')

        folder_name = year_str
        file_name = os.path.join(folder_name, f'{month_str}.xlsx')

        if not os.path.exists(file_name):
            print(f'File {file_name} does not exist.')
            return

        try:
            df = pd.read_excel(file_name, sheet_name=today_str, dtype={'Queue': str})
        except ValueError:
            print(f'Sheet {today_str} does not exist in {file_name}.')
            return

        queue_str = f'{int(queue):04}'

        if queue_str in df['Queue'].values:
            idx = df.index[df['Queue'] == queue_str].tolist()
            if idx:
                row_index = idx[0]
                if pd.isna(df.at[row_index, 'Penyerahan Obat']):
                    df.at[row_index, 'Penyerahan Obat'] = arrive

                    arrive_time = datetime.strptime(df.at[row_index, 'Pengumpulan Resep'], "%H:%M")
                    penyerahan_time = datetime.strptime(arrive, "%H:%M")
                    delta = penyerahan_time - arrive_time
                    df.at[row_index, 'Lama Waktu Tunggu (menit)'] = delta.total_seconds() / 60.0

                    # Remove old total and average rows if they exist
                    df = df[df['Queue'] != 'Total']
                    df = df[df['Queue'] != 'Average']

                    # Calculate total and average waiting time
                    total_waiting_time = df['Lama Waktu Tunggu (menit)'].sum(skipna=True)
                    average_waiting_time = df['Lama Waktu Tunggu (menit)'].mean(skipna=True)

                    total_row = pd.DataFrame([[None, 'Total', None, None, None, total_waiting_time]], columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
                    average_row = pd.DataFrame([[None, 'Average', None, None, None, average_waiting_time]], columns=['No', 'Queue', 'Nama', 'Pengumpulan Resep', 'Penyerahan Obat', 'Lama Waktu Tunggu (menit)'])
                    df = pd.concat([df, total_row, average_row], ignore_index=True)

                    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, sheet_name=today_str, index=False)

                    print(f'Data for Queue {queue_str} updated successfully.')
                else:
                    print(f'Queue {queue_str} already has a Penyerahan Obat entry.')
            else:
                print(f'Queue {queue_str} not found.')
        else:
            print(f'Queue {queue_str} not found in the data.')
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_window = PatientsListApp(isAdmin=True)
    main_window.show()
    sys.exit(app.exec_())
