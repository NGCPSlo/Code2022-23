import socket

# Define the server's IP address and port
#IP = "localhost"  # Replace this with the server's IP address
IP = "::"
PORT = 8888

# Create a client socket
client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Connect the socket to the server
client_socket.connect((IP, PORT))

# Continuously send data to the server
while True:
        # Get input from the user
        message = input("Enter your message: ")

        # Send the message to the server
        client_socket.sendall(message.encode())

        # Receive the response from the server
        data = client_socket.recv(1024)

        # Print the response
        print(f"Received from server: {data.decode()}")
