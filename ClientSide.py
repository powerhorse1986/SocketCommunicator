"""Socket Communicator Client Side Script

This script is put on the local machine. It will send message or signals
to the server side script.
"""

import socket
import selectors
import types

class Client:
    """
    A class used to represent the client side of the client-server program

    Methods
    -------
    start_connection(host, port, num_conns)
        Initiate the connection to the server
    service_connection(key, mask)
        Process the connection with the server
    """

    def __init__(self) -> None:
        self.sel = selectors.DefaultSelector()
        self.messages = []
        
    def set_msg(self, msg) -> None:
        """This function sets up the message sending to the server for 
        echoing

        Parameters
        ----------
        msg : list
            A list contains the messages
        """
        self.messages.extend(msg)


    def start_connection(self, host, port, num_conns) -> None:
        """Initiate a connection to the server

        Parameters
        ----------
        host : str
            The name of the host or the IP address of the host
        port : int
            The port number to which the server be connected
        num_conns : int        
            Number of connections created
        """
        
        server_addr = (host, port)
        for i in range(num_conns):
            conn_id = i + 1
            print(f"Starting connection {conn_id} to {server_addr}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(
                conn_id = conn_id,
                msg_total = sum(len(m) for m in self.messages),
                recv_total = 0,
                messages = self.messages.copy(),
                outb = b""
            )
            self.sel.register(sock, events, data = data)

    def service_connection(self, key, mask) -> None:
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
                self.sel.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            # If the data.outb is empty, we pop out the contents in data.message
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
                print(f"Loading {data.outb!r}")
            
            # If the data.outb is not empty, we send it out and trim off the buffer
            if data.outb:
                print(f"Sending {data.outb!r} to connection {data.conn_id}")
                sent = sock.send(data.outb)
                data.outb = data.outb[sent : ]
    
    def main(self):
        # The server's hostname or IP address
        # HOST = input("Type in the IP address of the server")
        HOST = "144.30.235.158"

        # The port used by the server
        PORT = 9898

        messages = [b"Message 1 from client.", b"Message 2 from client."]
        self.set_msg(messages)
        self.start_connection(HOST, PORT, len(messages))

        try:
            while True:
                events = self.sel.select(timeout = 1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask)
                # Check for a socket being monitored to continue
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("Caught keyboard intterrupt, exiting")
        finally:
            self.sel.close()

if __name__ == "__main__":
    client = Client()
    client.main()