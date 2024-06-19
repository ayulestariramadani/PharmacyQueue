import sys
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from components.current_queue import CurrentQueueApp
from components.patients_list import PatientsListApp
from datetime import datetime


class PharmacyDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pharmacy Display')
        self.showFullScreen()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        current_date = datetime.now().date()
        

        # Call window patient list
        self.patient_list = PatientsListApp()
        self.patient_list.show()
        
        # Call window current queue
        self.current_queue = CurrentQueueApp(isAdmin=False)
        self.current_queue.show()

        # Add left and right sections to the main layout with appropriate stretch factors
        main_layout.addWidget(self.patient_list, 1)
        main_layout.addWidget(self.current_queue, 1)  

        self.setCentralWidget(main_widget)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())
