import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import locale
from datetime import datetime

class HeaderQueueApp(QWidget):
    def __init__(self):
        super().__init__()

        # Create the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a wrapper widget for the layout with background color
        header_widget = QWidget()
        header_widget.setObjectName('header_widget')
        layout = QHBoxLayout(header_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        logo_label = QLabel()
        pixmap = QPixmap('D:/PharmacyQueue/PharmacyQueue/assets/1.png')
        logo_pixmap = pixmap.scaledToWidth(200,Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignLeft)

        # Add a label for title
        self.date_txt = QLabel(self.date_formatter())
        self.date_txt.setObjectName('date_txt')
        self.date_txt.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        layout.addWidget(logo_label)
        layout.addWidget(self.date_txt)

        main_layout.addWidget(header_widget)

        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

    def date_formatter(self):
        # Set the locale
        try:
            locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
        except locale.Error as e:
            print(f"Error setting locale: {e}")
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        
        # Get the current date and time
        current_datetime = datetime.now()

        # Format the datetime object to the desired output format
        output_date_str = current_datetime.strftime('%A, %d %B %Y %H:%M:%S')

        return output_date_str
    
    def update_time(self):
        self.date_txt.setText(self.date_formatter())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = HeaderQueueApp()
    main_win.show()
    sys.exit(app.exec_())