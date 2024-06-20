import sys
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from components.current_queue import CurrentQueueApp
from components.patients_table import PatientsTableApp
from components.date_formatter import date_formatter

class PharmacyDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pharmacy Admin')
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

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Call window patient list
        self.patient_list = PatientsTableApp(isAdmin=True)
        self.patient_list.show()

        # Add left and right sections to the main layout with appropriate stretch factors
        self.main_layout.addWidget(self.patient_list,3)  # 1/3 of the space
        
        self.current_queue = CurrentQueueApp(isAdmin=True)
        self.current_queue.show()
        self.main_layout.addWidget(self.current_queue,2)

        self.screen_layout.addLayout(self.main_layout)

        self.setCentralWidget(main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())
