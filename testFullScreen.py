import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt

class FullScreenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window to full screen
        self.showFullScreen()

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FullScreenWindow()
    window.show()
    sys.exit(app.exec_())
