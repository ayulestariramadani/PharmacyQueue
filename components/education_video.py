import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStyle, QHBoxLayout
from PyQt5.QtCore import QTimer, QEvent
import vlc

class VideoPlayer(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()

        self.setWindowTitle("PyQt VLC Video Player")
        # self.setGeometry(100, 100, 600, 460)

        self.instance = vlc.Instance()
        self.mediaPlayer = self.instance.media_player_new()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ui)

        self.video_frame = QWidget(self)
        # self.video_frame.setGeometry(10, 10, 500, 500)

        self.controlLayout = QHBoxLayout()

        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.playBtn.setObjectName('video_button')
        self.playBtn.setToolTip('Play')
        self.playBtn.clicked.connect(self.play_pause)

        self.muteBtn = QPushButton()
        self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        self.muteBtn.setObjectName('video_button')
        self.muteBtn.setToolTip('Mute')
        self.muteBtn.clicked.connect(self.muteVideo)

        self.controlLayout.addWidget(self.playBtn)
        self.controlLayout.addWidget(self.muteBtn)

        layout = QVBoxLayout()
        layout.setContentsMargins(100, 30, 100, 30)
        layout.addWidget(self.video_frame)
        layout.addLayout(self.controlLayout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.video_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                            if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
        self.current_index = 0
        if self.video_files:
            self.play_video(self.video_files[self.current_index])

        self.controlTimer = QTimer()
        self.controlTimer.setInterval(3000)
        self.controlTimer.timeout.connect(self.hide_controls)

        self.mediaPlayer.audio_set_mute(True)
        self.hide_controls()

        self.setMouseTracking(True)

    def play_pause(self):
        if self.mediaPlayer.is_playing():
            self.mediaPlayer.pause()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playBtn.setToolTip('Play')
            self.timer.stop()
        else:
            self.mediaPlayer.play()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.playBtn.setToolTip('Pause')
            self.timer.start()

    def play_video(self, file_path):
        self.media = self.instance.media_new(file_path)
        self.mediaPlayer.set_media(self.media)
        self.mediaPlayer.set_hwnd(self.video_frame.winId())
        self.mediaPlayer.play()

        self.timer.start()

    def muteVideo(self):
        if self.mediaPlayer.audio_get_mute():
            self.mediaPlayer.audio_set_mute(False)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.muteBtn.setToolTip('Mute')
        else:
            self.mediaPlayer.audio_set_mute(True)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.muteBtn.setToolTip('Unmute')

    def update_ui(self):
        if not self.mediaPlayer.is_playing():
            self.timer.stop()
            self.current_index += 1
            if self.current_index >= len(self.video_files):
                self.current_index = 0
            self.play_video(self.video_files[self.current_index])

    def mouseMoveEvent(self, event):
        self.show_controls()
        self.controlTimer.start()

    def hide_controls(self):
        self.playBtn.hide()
        self.muteBtn.hide()
        self.controlTimer.stop()

    def show_controls(self):
        self.playBtn.show()
        self.muteBtn.show()
        self.controlTimer.start()
    

if __name__ == '__main__':
    folder_path = "video"  # Change this to the path of your video folder
    app = QApplication(sys.argv)
    player = VideoPlayer(folder_path)
    player.show()
    sys.exit(app.exec_())
