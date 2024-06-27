import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSizePolicy, QHBoxLayout, QSlider, QStyle
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QDir, Qt, QTimer
import logging


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(350, 100, 655, 344)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videowidget = QVideoWidget()

        self.playBtn = QPushButton()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setObjectName('video_button')
        self.playBtn.setToolTip('Play')
        self.playBtn.clicked.connect(self.playPauseVideo)

        self.nextBtn = QPushButton()
        self.nextBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.nextBtn.setObjectName('video_button')
        self.nextBtn.setToolTip('Next')
        self.nextBtn.clicked.connect(self.nextVideo)

        self.prevBtn = QPushButton()
        self.prevBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.prevBtn.setObjectName('video_button')
        self.prevBtn.setToolTip('Previous')
        self.prevBtn.clicked.connect(self.prevVideo)
        

        self.stopBtn = QPushButton()
        self.stopBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopBtn.setObjectName('video_button')
        self.stopBtn.setToolTip('Stop')
        self.stopBtn.clicked.connect(self.stopVideo)

        self.muteBtn = QPushButton()
        self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        self.muteBtn.setObjectName('video_button')
        self.muteBtn.setToolTip('Mute')
        self.muteBtn.clicked.connect(self.muteVideo)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playBtn)
        controlLayout.addWidget(self.prevBtn)
        controlLayout.addWidget(self.stopBtn)
        controlLayout.addWidget(self.nextBtn)
        controlLayout.addWidget(self.muteBtn)
        

        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(50, 20, 50, 0)
        vboxLayout.setSpacing(0)
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(controlLayout)
        vboxLayout.addWidget(self.slider)

        self.setLayout(vboxLayout)
        self.setStyleSheet("background-color: black;")

        self.mediaPlayer.setVideoOutput(videowidget)
        self.mediaPlayer.error.connect(self.handleError)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        self.playlist = []
        self.currentIndex = 0

        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStatusChanged)
    
        self.folder = rf"video"  # Set specific folder path
        self.loadVideos()
        if self.playlist:
            self.playVideo(self.playlist[self.currentIndex])
        
        self.hideControls()

        self.controlTimer = QTimer()
        self.controlTimer.setInterval(3000)  
        self.controlTimer.timeout.connect(self.hideControls)
        self.setMouseTracking(True)

    def loadVideos(self):
        print(self.folder)
        if os.path.exists(self.folder):
            self.playlist = [os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            self.currentIndex = 0
            print(self.playlist)
        else:
            logging.error(f"Folder does not exist: {self.folder}")

    def playVideo(self, videoPath):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.mediaPlayer.play()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.playBtn.setToolTip('Pause')

    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.currentIndex += 1
            if self.currentIndex >= len(self.playlist):
                self.currentIndex = 0
            self.playVideo(self.playlist[self.currentIndex])
    
    def playPauseVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playBtn.setToolTip('Play')
        else:
            self.mediaPlayer.play()
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.playBtn.setToolTip('Pause')

    def stopVideo(self):
        self.mediaPlayer.stop()
        self.positionChanged(0)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setToolTip('Play')

    def nextVideo(self):
        self.currentIndex += 1
        if self.currentIndex >= len(self.playlist):
            self.currentIndex = 0
        self.playVideo(self.playlist[self.currentIndex])

    def prevVideo(self):
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = len(self.playlist) - 1
        self.playVideo(self.playlist[self.currentIndex])
    
    def muteVideo(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.muteBtn.setToolTip('Mute')
        else:
            self.mediaPlayer.setMuted(True)
            self.muteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.muteBtn.setToolTip('Unmute')

    def handleError(self):
        print("Error: " + self.mediaPlayer.errorString())
    
    def positionChanged(self, position):
        self.slider.setValue(position)

    def durationChanged(self, duration):
        self.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def mouseMoveEvent(self, event):
        self.showControls()
        self.controlTimer.start()

    def showControls(self):
        self.playBtn.show()
        self.nextBtn.show()
        self.prevBtn.show()
        self.stopBtn.show()
        self.muteBtn.show()
        self.slider.show()
        self.controlTimer.start()

    def hideControls(self):
        self.playBtn.hide()
        self.nextBtn.hide()
        self.prevBtn.hide()
        self.stopBtn.hide()
        self.muteBtn.hide()
        self.slider.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
