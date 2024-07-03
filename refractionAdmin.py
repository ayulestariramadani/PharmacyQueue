import sys
from pathlib import Path
from functools import partial 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer
from components.current_queue import CurrentQueueApp
from components.patients_table_refraksi import PatientsTableApp
from components.header_queue import HeaderQueueApp


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

        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(50)
        button_layout.setContentsMargins(50, 0, 50, 200)

        self.data = ["-","-"]

        # Add Panggil Button
        self.panggil_button = QPushButton("Panggil")
        self.panggil_button.setObjectName('panggil_button')
        # panggil_button.clicked.connect(partial(self.patient_list.send_message, [self.current_queue.norm_label.text(), self.current_queue.name_label.text()]))


        # Add Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName('refresh_button')

        button_layout.addWidget(self.panggil_button)
        button_layout.addWidget(refresh_button)
        
        self.right_layout.addWidget(self.current_queue)
        self.right_layout.addWidget(button_widget)

        self.main_layout.addLayout(self.right_layout,2)

        self.screen_layout.addLayout(self.main_layout)

        self.setCentralWidget(main_widget)

        # Create a timer to update labels periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
    
    def update_data(self):
        # Handle the label text change
        self.data = [self.current_queue.norm_label.text(), self.current_queue.name_label.text()]
        self.panggil_button.clicked.connect(partial(self.patient_list.send_message, self.data))

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
