import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QListWidget
import vlc

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.instance = vlc.Instance()
        self.mediaPlayer = self.instance.media_player_new()

        self.playlist = QListWidget()
        self.playlist.clicked.connect(self.play_selected_video)

        openFolderButton = QPushButton("Open Folder")
        openFolderButton.clicked.connect(self.open_folder)

        layout = QVBoxLayout()
        layout.addWidget(openFolderButton)
        layout.addWidget(self.playlist)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.video_widget = QWidget(self)
        layout.addWidget(self.video_widget)
        self.mediaPlayer.set_hwnd(self.video_widget.winId())

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder:
            self.load_videos_from_folder(folder)

    def load_videos_from_folder(self, folder):
        self.playlist.clear()
        for file_name in os.listdir(folder):
            if file_name.endswith(('.mp4', '.avi', '.mkv', '.mov')):
                file_path = os.path.join(folder, file_name)
                file_path = os.path.normpath(file_path)  # Normalize path
                self.playlist.addItem(file_path)

    def play_selected_video(self):
        selected_item = self.playlist.currentItem()
        if selected_item:
            video_path = selected_item.text()
            self.media = self.instance.media_new(video_path)
            self.mediaPlayer.set_media(self.media)
            self.mediaPlayer.play()

if __name__ == '__main__':
    # Initialize COM library
    ctypes.windll.ole32.CoInitializeEx(None, ctypes.COINIT_MULTITHREADED)

    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())

    # Uninitialize COM library
    ctypes.windll.ole32.CoUninitialize()
