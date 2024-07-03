import sys
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from components.current_queue import CurrentQueueApp
from components.patients_table_refraksi import PatientsTableApp
from components.date_formatter import date_formatter
from components.header_queue import HeaderQueueApp


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

        self.header_queue = HeaderQueueApp()
        self.header_queue.show()
        self.screen_layout.addWidget(self.header_queue)

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
