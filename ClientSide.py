#! /usr/bin/python

"""Socket Communicator Client Side Script

This script is put on the local machine. It will send message or signals
to the server side script.
"""

import socket
import subprocess

# The server's hostname or IP address
HOST = "172.20.1.47"

# The port used by the server
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Creates a socket object, uses .connect() to connect to
    # the server
    s.connect((HOST, PORT))

    # Calls .sendall() to send its message
    s.sendall("Hello, World")
    data = s.recv(2048)

# Echo the feed back information
subprocess.call(f"Echo {data!r}")