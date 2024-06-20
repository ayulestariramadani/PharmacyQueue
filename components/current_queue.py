import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from services.client import SocketClient
from components.education_video import VideoPlayer
from playsound import playsound

# Define a worker thread to play sound
class SoundThread(QThread):
    def __init__(self, sound_file):
        super().__init__()
        self.sound_file = sound_file

    def run(self):
        playsound(self.sound_file)

class CurrentQueueApp(QWidget):
    def __init__(self, isAdmin=True):
        super().__init__()
        self.initSocketClient()
        self.isAdmin = isAdmin
        self.setObjectName('current_queue')

        # Define the box is vertical stack
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        
        if not self.isAdmin:
            self.education_video = VideoPlayer()
            self.education_video.show()

            layout.addWidget(self.education_video,1)


        logo_label = QLabel()
        pixmap = QPixmap('assets/1.png')
        logo_pixmap = pixmap.scaledToWidth(248,Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo_label)

        # Add a label for title
        queue_title = QLabel("Antrian yang Dilayani")
        queue_title.setObjectName('queue_title')
        queue_title.setAlignment(Qt.AlignCenter)
        # Add queue_title to main layout
        layout.addWidget(queue_title)

        # Add Label Current Number
        self.norm_label = QLabel("-")
        self.norm_label.setObjectName('norm_label')
        self.norm_label.setContentsMargins(0, 0, 0, 0)
        self.norm_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.norm_label.setMinimumHeight(self.norm_label.sizeHint().height()+100)

        self.norm_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.norm_label)

        # Add Label Current Number
        self.name_label = QLabel("-")
        self.name_label.setObjectName('name_label')
        self.name_label.setContentsMargins(0, 0, 0, 0)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        # Add current number to main layout
        layout.addWidget(self.name_label)

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)

        # Add Panggil Button
        panggil_button = QPushButton("Panggil ini")
        panggil_button.setObjectName('panggil_button')


        # Add Refresh Button
        refresh_button = QPushButton("Refresh ini")

        button_layout.addWidget(panggil_button)
        button_layout.addWidget(refresh_button)

        if self.isAdmin:
            layout.addWidget(button_widget)
        self.setStyleSheet('background-color: white')
        self.setLayout(layout)
    
    def initSocketClient(self):
        self.socket_client = SocketClient()
        self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()

    @pyqtSlot(str)
    def update_label(self, message):
        # Parse the message
        try:
            # Split the message by commas
            parts = message.split(',')
            order_data = {}
            for part in parts:
                key, value = part.split(':')
                order_data[key.strip()] = value.strip()

            # Check if all required keys are in the order_data
            required_keys = ['NORM', 'Name', 'isCall']
            if all(key in order_data for key in required_keys):
                self.name_label.setText(f"{order_data['Name']}")
                self.norm_label.setText(f"{order_data['NORM']}") 
                if not self.isAdmin:
                    self.play_sound()
            else:
                print("Message missing required keys")
        except Exception as e:
            print(f"Error parsing message: {e}")

    def play_sound(self):
        number_list = self.angka_ke_nominal(self.norm_label.text())
        sound_sequence = ['bell', 'nomor_rekam_medik'] + number_list.split()

        self.play_sounds_in_sequence(sound_sequence, 0)

    def play_sounds_in_sequence(self, sound_sequence, index):
        self.education_video.mediaPlayer.setMuted(True)
        if index >= len(sound_sequence):
            self.education_video.mediaPlayer.setMuted(False)
            return
        
        sound_file = 'audio/' + sound_sequence[index] + '.wav'
        self.sound_thread = SoundThread(sound_file)
        self.sound_thread.finished.connect(lambda: self.play_sounds_in_sequence(sound_sequence, index + 1))
        self.sound_thread.start()
        
    def angka_ke_nominal(self, angka):
        nominal = {
            '0': 'nol',
            '1': 'satu',
            '2': 'dua',
            '3': 'tiga',
            '4': 'empat',
            '5': 'lima',
            '6': 'enam',
            '7': 'tujuh',
            '8': 'delapan',
            '9': 'sembilan'
        }

        hasil = []
        angka = str(angka)
        for i in angka:
            hasil.append(nominal[i])

        return ' '.join(hasil)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = CurrentQueueApp(['16039', 'Hamba Allah'])
    main_win.show()
    sys.exit(app.exec_())