# Import the required libraries
import socket
import select

# Define the IP address and port to bind the server socket
IP = "::"  # This IP address allows both IPv6 and IPv4 connections
#IP="localhost"
PORT = 8888

# Create a server socket
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

# Set the SO_REUSEADDR socket option to allow multiple bind to the same address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server socket to the specified IP address and port
server_socket.bind((IP, PORT))

# Start listening for incoming connections
server_socket.listen(3)

# Print a message to indicate the server is running
print(f"HTTP server is using TCP port <{PORT}>\nHTTPS server is using TCP port -1")
print("Waiting for connections ...")

# A list to keep track of all connected clients
clients_list = [server_socket]

# Continuously wait for incoming connections
while True:
    # Use select.select() to wait for incoming data from the connected clients
    read_sockets, _, _ = select.select(clients_list, [], [])
    for sock in read_sockets:
        # If the socket is the server socket, it means a new connection has been accepted
        if sock == server_socket:
            new_socket, addr = server_socket.accept()
            clients_list.append(new_socket)
            print(f"Accepted new connection from {addr[0]}:{addr[1]}")
        else:
            # Receive data from the client
            data = sock.recv(1024)
            if not data:
                # If there is no data, it means the connection has been closed
                print(f"Closing connection from {sock.getpeername()[0]}:{sock.getpeername()[1]}")
                clients_list.remove(sock)
                sock.close()
            else:
                # Send the received data back to the client
                print(b"Received: " + data)
                sock.send(b"ECHO: " + data)
