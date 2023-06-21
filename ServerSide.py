#! /usr/bin/python

"""Socket Communicator Server Side Program

This script will be put on the server side to receive the signal or
file sent by the client side which is put on local machine
"""
import os
import socket
import selectors
import types

# Standard loopback interface address (localhost)
HOST = "0.0.0.0"
# Port to listen on
PORT = 9898

# The selectors module allows high-level and efficient I/O
# multiplexing. DefaultSelector is an alias to the most 
# effecient implementation available on the current platform.
selector = selectors.DefaultSelector()

def accept_wrapper(sock):
    """This function gets the new socket object and register it with the 
    selector

    Parameters
    ----------
    sock : a fileobj of the key in the tuple returned by selector.select()
        The fileobj of the key is the file boject registered. Till now we 
        only registered the sock listening on (HOST, PORT)
    """
    # Because the listening block was registered for the event 
    # selectors.EVENT_READ, it should be ready to readl. Call sock.accept()
    # and then call conn.setblocking(False) to put the socket in non-blocking
    # mode
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)

    # Create an object to hold the data that we want to included along with 
    # the socket using a SimpleNamespace.
    data = types.SimpleNamespace(addr = addr, inb = b"", outb = b"")

    # We want to know when the client connection is ready for reading and 
    # writing
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    selector.register(conn, events, data = data)

def service_connection(key, mask):
    """This function services the client socket

    Parameters
    ----------
    key : The SelectorKey instance corresponding to a ready file object.
        key contains the socket object (fileobj) and data object
    mask : A bit mask
        a bitmask of events ready on this file object
    """
    sock = key.fileobj
    data = key.data

    # If the socket is ready for reading then mask & selectors.EVENT_READ
    # will be True, thus sock.recv() is called. Any data that's read is 
    # appended to data.outb so that it can be sent later
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        print(f"Data: {data}")
        if recv_data:
            print(f"Data: {recv_data!r}")
            data.outb += recv_data
        # If no data is received, this means that the client has closed
        # its socket, so the server should too
        else:
            print(f"Closing connection to {data.addr}")
            selector.unregister(sock)
            sock.close()

    # When the socket is ready for writing, which should always be the case
    # for a healthy socket, any received data stored in data.outb is echoed
    # to the client using sock.send(). The bytes sent are then removed from
    # the send buffer.
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Closing connection to {data.addr}")

            # The .send() method returns the number of bytes sent. This 
            # number then be used to slice the .outb buffer to discard the
            # bytes sent later
            try:
                sent = sock.send(data.outb)
                data.oub = data.outb[sent : ]
            except Exception as e:
                print(e)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    """
    socket.AF_INET: The internet address family of IPv4
    socket.SOCK_STREAM: The socket type for TCP
    """
    sock.bind((HOST, PORT))
    sock.listen()
    print(f"Listening on {HOST, PORT}")

    # .setblocking(False) configures the socket in non-blocking
    # mode. Calls made to this socket will no longer block.
    sock.setblocking(False)

    # selector.register() registers the socket to be monitored
    # with selector.register() for the event that we are 
    # interested in. For the listening socket, we want read 
    # events: selectors.EVENT_READ
    selector.register(sock, selectors.EVENT_READ, data = None)
    
    try:
        
        while True:
            
            # selector.select(timeout = None) blocks until there
            # are sockets ready for I/O. It returns a list of 
            # tuples, one for each socket. Each tuple contains 
            # a key and a mask. They key is the SelectorKey 
            # instance corresponding to a ready file object. key.fileobj
            # is the socke object. mask is a bitmask of events
            #  ready on this file object
            events = selector.select(timeout = None)
            

            for key, mask in events:

                # If key.data is None, then we know it's from the
                # listening socket and we need to accept the connection.
                # We'll call the accept_wrapper() function to get the 
                # new socket object and register it with the selector
                if key.data is None:
                    accept_wrapper(key.fileobj)
                
                # If key.data is not None, we know it's a client socket
                # that's ready been accepted, and we need to service it
                # The function service_connection() is then called with 
                # key and mask as arguments
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Cauth keyboard interrupt, exiting")
    finally:
        selector.close()