"""Socket Communicator Client Side Script

This script is put on the local machine. It will send message or signals
to the server side script.
"""

import socket
import selectors
import types

# The server's hostname or IP address
# HOST = input("Type in the IP address of the server")
HOST = ""

# The port used by the server
PORT = 9898

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connection(host, port, num_conns = len(messages)):
    """Initiate a connection to the server

    Parameters
    ----------
    host : str
        The name of the host or the IP address of the host
    port : int
        The port number to which the server be connected
    num_conns : int        Number of connections created
    """
    
    server_addr = (host, port)
    for i in range(num_conns):
        conn_id = i + 1
        print(f"Starting connection {conn_id} to {host, port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            conn_id = conn_id,
            msg_total = sum(len(m) for m in messages),
            recv_total = 0,
            messages = messages.copy(),
            outb = b""
        )
        sel.register(sock, events, data = data)

def service_connection(key, mask):
    """This function connects to the server socket

    Parameters
    ----------
    key : The SelectorKey instance corresponding to a ready file object.
        key contains the socket object (fileobj) and data object
    mask : A bit mask
        a bitmask of events ready on this file object
    """

    # The socket object 
    sock = key.fileobj

    # The data object
    data = key.data

    if mask & selectors.EVENT_READ:
        # Take out the data transferred by the socket
        recv_data = sock.recv(1024)

        # If we receive data which is not empty, print it out and update
        # the data.recv_total
        if recv_data:
            print(f"Received {recv_data} from connection {data.conn_id}")
            data.recv_total += len(recv_data)

        # If the received data is empty or data.recv_total == data.msg_total
        # that means the connection should be closed
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.conn_id}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        # If the data.outb is empty, we pop out the contents in data.message
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        
        # If the data.outb is not empty, we send it out and trim off the buffer
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.conn_id}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent : ]

start_connection(HOST, PORT)

try:
    while True:
        events = sel.select(timeout = 1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard intterrupt, exiting")
finally:
    sel.close()