import socketio
from PyQt5.QtCore import QThread, pyqtSignal
from dotenv import dotenv_values
import time



class SocketClient(QThread):
    message_received = pyqtSignal(str)

    config = dotenv_values(".env")

    def __init__(self):
        super(SocketClient, self).__init__()
        self.sio = socketio.Client(logger=True)

        @self.sio.event
        def connect():
            print("Connected to the server")

        @self.sio.event
        def disconnect():
            print("Disconnected from the server")
            self.attempt_reconnect()

        @self.sio.on(self.config['SOCKET_SEND'])
        def on_message(data):
            self.message_received.emit(data)

    def run(self):
        self.sio.connect(self.config['URL_WEBSOCKET'], wait_timeout=100)
        self.sio.wait()
    
    def attempt_reconnect(self):
        while True:
            try:
                print("Attempting to reconnect...")
                self.sio.connect(self.config['URL_WEBSOCKET'])
                break
            except socketio.exceptions.ConnectionError:
                print("Reconnection failed, retrying in 5 seconds...")
                time.sleep(5)

    def send_message(self, message):
        self.sio.emit(self.config['SOCKET_RECEIVED'], message)
