import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from services.client import SocketClient
from components.education_video import VideoPlayer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class CurrentQueueApp(QWidget):
    def __init__(self, isAdmin=True):
        super().__init__()
        self.initSocketClient()
        self.isAdmin = isAdmin
        self.setObjectName('current_queue')

        self.data = []
        # Create the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a wrapper widget for the layout with background color
        wrapper_widget = QWidget()
        wrapper_widget.setObjectName('wrapper_widget')
        layout = QVBoxLayout(wrapper_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.custom_widget = QWidget()
        
        if not self.isAdmin:

            video_layout = QHBoxLayout()
            
            self.custom_widget.setStyleSheet("background-color: #003468")
            self.custom_widget.setMinimumSize(5, 5)
            self.custom_widget.paintEvent = self.paintEvent
            video_layout.addWidget(self.custom_widget)
            
            self.education_video = VideoPlayer("video")
            self.education_video.show()

            video_layout.addWidget(self.education_video)

            layout.addLayout(video_layout,4)

        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.stateChanged.connect(self.handle_media_state_changed)

        # Add a label for title
        queue_title = QLabel("Antrian yang Dilayani")
        queue_title.setObjectName('queue_title')
        queue_title.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        # Add queue_title to main layout
        layout.addWidget(queue_title, 1)

        # Add Label Current Numbers
        self.norm_label = QLabel("-")
        self.norm_label.setObjectName('norm_label')
        self.norm_label.setContentsMargins(0, 0, 0, 0)
        self.norm_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.norm_label.setMinimumHeight(self.norm_label.sizeHint().height()+100)

        self.norm_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.norm_label, 1)

        # Add Label Current Number
        self.name_label = QLabel("-")
        self.name_label.setObjectName('name_label')
        self.name_label.setContentsMargins(0, 0, 0, 0)
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.name_label.setWordWrap(True)
        # Add current number to main layout
        layout.addWidget(self.name_label, 1)
        
        main_layout.addWidget(wrapper_widget)
        self.setLayout(main_layout)
    
    def paintEvent(self, event):
        painter = QPainter(self.custom_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.custom_widget.width(), 0)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 150))  # Middle color
        gradient.setColorAt(0.5, QColor(0, 0, 0, 100))  # Middle color
        gradient.setColorAt(1.0, QColor(0, 0, 0, 10))  # End with transparent color

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        # Draw a rectangle to fill the widget area with gradient
        painter.drawRect(0, 0, self.custom_widget.width(), self.custom_widget.height())

    def initSocketClient(self):
        self.socket_client = SocketClient()
        self.socket_client.message_received.connect(self.update_label)
        self.socket_client.start()

    @pyqtSlot(str)
    def update_label(self, message):
        # Parse the message
        try:
            # Split the message by commas
            parts = message.split(';')
            order_data = {}
            for part in parts:
                key, value = part.split(':')
                order_data[key.strip()] = value.strip()

            # Check if all required keys are in the order_data
            required_keys = ['NORM', 'Name', 'ID']
            if all(key in order_data for key in required_keys):
                self.name_label.setText(f"{order_data['Name']}")
                self.norm_label.setText(f"{order_data['NORM']}")
                self.data = [order_data['NORM'], order_data['Name'], order_data['ID']] 
                if not self.isAdmin:
                    self.play_sound()
            else:
                print("Message missing required keys")
        except Exception as e:
            print(f"Error parsing message: {e}")

    def play_sound(self):
        number_list = self.angka_ke_nominal(self.norm_label.text())
        sound_sequence = ['bell', 'nomorrm'] + number_list.split()

        self.play_sounds_in_sequence(sound_sequence, 0)

    def play_sounds_in_sequence(self, sound_sequence, start_index):
        self.sound_sequence = sound_sequence
        self.index = start_index
        self.play_next_sound()
    
    def play_next_sound(self):
        # self.education_video.mediaPlayer.audio_set_mute(True)
        if self.index < len(self.sound_sequence):
            sound_file = rf"audio\{self.sound_sequence[self.index]}.wav"
            url = QUrl.fromLocalFile(sound_file)
            content = QMediaContent(url)
            self.mediaPlayer.setMedia(content)
            self.mediaPlayer.play()
            self.index += 1
        else:
            self.mediaPlayer.setMedia(QMediaContent())
            self.index = 0
            # self.education_video.mediaPlayer.audio_set_mute(False)

    def handle_media_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            self.play_next_sound()

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