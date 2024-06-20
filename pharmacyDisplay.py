import sys
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from components.current_queue import CurrentQueueApp
from components.patients_table import PatientsTableApp
from components.date_formatter import date_formatter


class PharmacyDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pharmacy Display')
        self.showFullScreen()

        # Main widget and layout
        main_widget = QWidget()

        self.screen_layout = QVBoxLayout(main_widget)
        self.screen_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_layout.setSpacing(0)

        current_date = date_formatter()

        # Add a label for title
        date_txt = QLabel(f"{current_date}")
        date_txt.setObjectName('date_txt')
        date_txt.setAlignment(Qt.AlignRight)
        # Add date_txt to main layout

        self.screen_layout.addWidget(date_txt)


        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        

        # Call window patient list
        self.patient_list = PatientsTableApp()
        self.patient_list.show()
        
        # Call window current queue
        self.current_queue = CurrentQueueApp(isAdmin=False)
        self.current_queue.show()

        # Add left and right sections to the main layout with appropriate stretch factors
        main_layout.addWidget(self.patient_list, 1)
        main_layout.addWidget(self.current_queue, 1)  

        self.screen_layout.addLayout(main_layout)
        self.setCentralWidget(main_widget)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())
