#! /usr/bin/python

"""Socket Communicator Server Side Program

This script will be put on the server side to receive the signal or
file sent by the client side which is put on local machine
"""
import socket
import subprocess

# Standard loopback interface address (localhost)
HOST = "0.0.0.0"
# Port to listen on
PORT = 9898

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    """
    socket.AF_INET: The internet address family of IPv4
    socket.SOCK_STREAM: The socket type for TCP
    """
    s.bind((HOST, PORT))
    s.listen()

    # The .accept() method blocks execution and waits for an
    # incoming connection. When a client connects, it returns
    # a new socket object representing the connection and a
    # tuple holding the address of the client
    conn, addr = s.accept()

    with conn:
        subprocess.call(f"Connected by {addr}")
        while True:
            """
            An infinite while loop is used to loop over blocking
            calls to conn.recv(). This reads whatever data the
            client sends and echoes it back using conn.sendall()
            """
            data = conn.recv(2048)

            # If conn.recv() returns an empty bytes object, b'',
            # that signals that the client closed the connection
            # and the loop is terminated
            if not data:
                break
            conn.sendall(data)