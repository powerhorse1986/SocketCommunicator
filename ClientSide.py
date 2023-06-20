#! /usr/bin/python

"""Socket Communicator Client Side Script

This script is put on the local machine. It will send message or signals
to the server side script.
"""

import socket

# The server's hostname or IP address
# HOST = input("Type in the IP address of the server")
HOST = socket.gethostname()

# The port used by the server
PORT = 9898

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Creates a socket object, uses .connect() to connect to
    # the server

    s.connect((HOST, PORT))

    # Calls .sendall() to send its message
    s.sendall("Hello, World".encode())
    data = s.recv(1024)

# Echo the feed back information
print(f"{data!r}")