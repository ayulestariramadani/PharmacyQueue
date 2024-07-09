import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPainter, QLinearGradient
from PyQt5.QtCore import Qt

class ShadowWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Shadow Widget')

        layout = QVBoxLayout(self)

        # Example label, replace with your widget
        label = QLabel("Widget with shadow", self)
        label.setStyleSheet("background-color: white; color: black; border: 1px solid #aaa;")
        layout.addWidget(label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a linear gradient for the shadow effect
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 100))
        gradient.setColorAt(0.5, QColor(0, 0, 0, 50))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        # Draw the gradient as a shadow on the left side
        shadow_rect = self.rect()
        shadow_rect.setWidth(10)  # Adjust the width of the shadow as needed
        painter.fillRect(shadow_rect, gradient)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    shadow_widget = ShadowWidget()
    shadow_widget.show()
    sys.exit(app.exec_())
