import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

# Event handler for connection
@sio.event
def connect():
    print('Connected to server')

# Event handler for disconnection
@sio.event
def disconnect():
    print('Disconnected from server')

# Event handler for receiving a message
@sio.event
def message_from_client(data):
    print('Message from', data['sender'], ':', data['message'])

# Connect to the server
sio.connect('http://201.131.0.219:4001')

sio.emit('send-text1', "Testttt")
sio.emit('send-text1', "Testttt")



# Wait for events
sio.wait()