import sys
from pathlib import Path 
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from components.current_queue import CurrentQueueApp
from components.patients_table import PatientsTableApp
from components.header_queue import HeaderQueueApp
from components.custom_button import CustomButton
from services.client import SocketClient
from services.jsonParser import delete_antrian_farmasi, get_antrian_farmasi


class PharmacyDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initSocketClient()

        self.setWindowTitle('Pharmacy Admin')
        self.showFullScreen()

        # Main widget and layout
        main_widget = QWidget()
        self.screen_layout = QVBoxLayout(main_widget)
        self.screen_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_layout.setSpacing(0)
        
        self.header_queue = HeaderQueueApp()
        self.header_queue.show()
        self.screen_layout.addWidget(self.header_queue)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Call window patient list
        self.patient_list = PatientsTableApp(isAdmin=True)
        self.patient_list.show()

        # Add left and right sections to the main layout with appropriate stretch factors
        self.main_layout.addWidget(self.patient_list,3)  # 1/3 of the space
        
        self.right_layout = QVBoxLayout()
        
        self.current_queue = CurrentQueueApp(isAdmin=True)
        self.current_queue.show()

        button_widget = QWidget()
        button_widget.setObjectName('button_widget')
        buttons_layout = QVBoxLayout(button_widget)
        buttons_layout.setSpacing(50)
        buttons_layout.setContentsMargins(200, 100, 200, 200)


        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)
        button_layout.setContentsMargins(0, 0, 0, 0)
        self.data = []
        # Add Panggil Button
        self.panggil_button = CustomButton(" Panggil", "assets/speaker.png")
        self.panggil_button.setObjectName('panggil_button')
        self.panggil_button.clicked.connect(self.send_data)
        # self.panggil_button.clicked.connect(partial(self.patient_list.send_message, [self.current_queue.norm_label.text(), self.current_queue.name_label.text()]))


        # Add Refresh Button
        refresh_button = CustomButton(" Refresh", "assets/refresh.png")
        refresh_button.setObjectName('refresh_button')
        refresh_button.clicked.connect(self.patient_list.load_data)

        selesai_button = CustomButton(" Selesai", "assets/check.png")
        selesai_button.setObjectName('selesai_button')
        selesai_button.setFixedSize(150,25)
        selesai_button.clicked.connect(self.delete_data)


        button_layout.addWidget(refresh_button)
        button_layout.addWidget(self.panggil_button)

        buttons_layout.addLayout(button_layout)
        buttons_layout.addWidget(selesai_button, alignment=Qt.AlignCenter)
        
        self.right_layout.addWidget(self.current_queue)
        self.right_layout.addWidget(button_widget)

        self.main_layout.addLayout(self.right_layout,2)

        self.screen_layout.addLayout(self.main_layout)

        self.setCentralWidget(main_widget)

        # Create a timer to update labels periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
    
    def initSocketClient(self):
        self.socket_client = SocketClient()
        # self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()
    
    @pyqtSlot(list)
    def send_message(self, patient_data):
        message = f"NORM: {patient_data[0]}; Name: {patient_data[1]}; ID: {patient_data[2]}"
        print(message)
        self.socket_client.send_message(message)
        # self.name_text.clear()
    
    def delete_data(self):
        delete_antrian_farmasi(self.data[2])
        data = get_antrian_farmasi()
        if data !=[]:
            current_data = data[0]
            self.current_queue.data = [current_data['NORM'], current_data['NAMA_LENGKAP'], current_data['ID']]
            
        else:
            self.current_queue.data = ["-","-","-"]

        self.current_queue.norm_label.setText(self.current_queue.data[0])
        self.current_queue.name_label.setText(self.current_queue.data[1])
        print(self.data)


    def update_data(self):
        # Handle the label text change
        self.data = self.current_queue.data
    
    def send_data(self):
        self.send_message(self.data)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Exit full screen mode
            self.showNormal()
            self.isFullScreen = False
        elif event.key() == Qt.Key_F5:
            if self.isFullScreen:
                # Exit full screen mode if currently in full screen
                self.showNormal()
            else:
                # Enter full screen mode if currently not in full screen
                self.showFullScreen()
            self.isFullScreen = not self.isFullScreen


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())
