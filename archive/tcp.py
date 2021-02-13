
import socket
import os
import threading
import logging
from queue import Queue
from enum import Enum


class Configurations:
    """
    class to hold the configurations of the program
    Contains references to all the constants

    It is a singleton
    """

    __item = None

    def __init__(self):
        self.port = 9654
        self.max_number_of_active_socket_connections = 1
        self.download_data_storage_folder = "commtemp"
        self.download_data_storage_file = "download_data.xml"
        self.handshake_size = 8
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || Configurations initiated")

    def __new__(cls, *args, **kwargs):
        if cls.__item is None:
            cls.__item = object.__new__(cls)
            logging.log(logging.DEBUG, f"{cls.__name__} || new object created")
        return cls.__item

    @staticmethod
    def get_download_file_path(self):
        """
        returns the directory where the downloaded data file is to be stored
        :return: full path of the download file
        """
        target_path_address = os.path.join(os.getcwd(), Configurations().download_data_storage_folder, )
        if not os.path.exists(target_path_address):
            os.mkdir(Configurations().download_data_storage_folder)
            logging.log(logging.DEBUG, f"{self.__class__.__name__} || target_path_address created @ {target_path_address}")
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || target_path_address: {target_path_address}")
        return target_path_address


class BasicSocket:
    """
    Base class for connection sockets

    implements base routines for sending and receiving data over the socket connection
    """
    def __init__(self, assigned_port=Configurations().port, sock_addr=socket.gethostname()):
        assert isinstance(assigned_port, int)
        self.hostname = sock_addr
        self.assigned_port = assigned_port
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || socket initiated")

    def receive_data(self):
        """
        reads the data from the buffer when a connection has been established
        :return: the data read from the buffer in string format
        """
        data = []
        # get the fixed size handshake message which specifies the length of the message to be read next
        hs_message = self.connection.recv(Configurations().handshake_size).decode()
        # convert the read to int
        data_size = int(hs_message, 16)
        # size of pending data to be read from the server is initialized to the size read from handshake
        pending_data = data_size
        # loop until the full message is read in chucks of 2 KB
        while pending_data > 0:
            blob = self.connection.recv(min(pending_data, 2048))
            # If, before the fixed size of message s completely read, the line goes empty raise an error
            if len(blob) == 0:
                raise Exception("Abnormal Disconnection")
            # reduce the size of the data pending by subtracting the size of the received data
            pending_data -= len(blob)
            # the newly read data is appended to the main data variable
            data.append(blob)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || data received")
        return data

    def transmit_data(self, data):
        """
        transmits the data specified over the socket connection
        :param data: Data content in string format
        :return: None
        """
        # size of data calculated
        data_size = len(data)
        # the data is then converted to hex string for uniformity in size
        size_in_hex = "0x%0.8X" % data_size
        # send the handshake message that is the data to be read further on the other end
        self.connection.send(size_in_hex.encode())
        # counter initialized to 0
        sent_so_far = 0
        # the contents of the data is sent in loops
        while sent_so_far < data_size:
            sent_blob_size = self.connection.send(data[sent_so_far:])
            if len(sent_blob_size) == 0:
                raise Exception("abnormal disconnection")
            sent_so_far += sent_blob_size
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || data transmission is completed")


class HostSocket(BasicSocket):
    """
    Extension of Basic sockets
    To be used on server side
    """

    def __init__(self, assigned_port=Configurations().port, sock_addr=socket.gethostname()):
        super().__init__(assigned_port, sock_addr)

    def bind_to_the_host_ip(self):
        """
        Function binds to the specified socket
        :return: None
        """
        self.socket_conn.bind((self.hostname, self.assigned_port))
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || socket bound : {(self.hostname, self.assigned_port)}")

    def listen_for_connection_request(self):
        """
        Function listens to the network for connection requests and stores the connections detail to self.connection
        :return: None
        """
        self.socket_conn.listen(Configurations().max_number_of_active_socket_connections)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || listening to remote requests")
        (connection, address) = self.socket_conn.accept()
        self.connection = connection
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || connection secured {address}")
        return connection, address


class ClientSocket(BasicSocket):
    """
    Extension of BasicSocket
    To be used on client side
    """

    def __init__(self, assigned_port=Configurations().port, sock_addr=socket.gethostname()):
        super().__init__(assigned_port, sock_addr)

    def connect_to_remote_socket(self):
        """
        Connects to the server and stores in the self.connection
        :return: None
        """
        logging.log(logging.DEBUG,
                    f"{self.__class__.__name__} || trying to connect to {(self.hostname, self.assigned_port)}")
        self.socket_conn.connect((self.hostname, self.assigned_port))
        self.connection = self.socket_conn


class MessageQueue:
    """
    Base messaging queue
    To be used for inter thread comm

    Do not use directly, first inherit
    """
    def __init__(self):
        self.queue = Queue()
        self.last_message = None
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || instantiated")

    def push(self, message):
        """
        add the specified message to the queue
        :param message: any type, to push into queue, sent to a different thread
        :return: None
        """
        self.queue.put(message)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || message pushed into queue")

    def get(self):
        """
        get the next message out of the queue
        :return: message
        """
        self.last_message = self.queue.get()
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || message popped from the queue")
        return self.last_message

    def get_last_message(self):
        """
        get the last read message without affecting the queue
        :return: message
        """
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || last message from the queue read")
        return self.last_message


class IncomingMessageQueue(MessageQueue):
    """
    Message queue to be used for sending the messages to the comm agent
    """

    __singleton = None

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
            logging.log(logging.DEBUG, f"{cls.__name__} || new instance created")
        return cls.__singleton


class OutgoingMessageQueue(MessageQueue):
    """
    message queue to be used by the classes to receive the message from the comm agent
    """

    __singleton = None

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
            logging.log(logging.DEBUG, f"{cls.__name__} || new instance created")
        return cls.__singleton


class HostStates(Enum):
    """
    enumeration of Host Comm agents different states
    """
    PEER_UNREGISTERED = 0x01
    PENDING_CONTACT_FROM_PEER = 0x02
    DATA_TRANSMISSION_PENDING = 0x03
    PENDING_ACK = 0x04
    COMM_COMPLETED = 0x05


class ClientStates(Enum):
    """
    enumeration of Client Comm agents different states
    """
    PEER_UNREGISTERED = 0x01
    PENDING_CONNECTION_TO_PEER = 0x02
    DATA_RECEPTION_PENDING = 0x03
    PENDING_ACK = 0x04
    COMM_COMPLETED = 0x05


class CommunicationThread(threading):
    """
    Comm agent thread class specializing in how communication is done across the network
    """

    def __init__(self, is_server: bool, remote_server_address_tuple=(socket.gethostname(), Configurations().port)):
        self.status = None
        self.is_server = is_server
        if self.is_server:
            self.remote_peer_address = None
        else:
            self.remote_peer_address = remote_server_address_tuple
        self.inbox = IncomingMessageQueue()
        self.outbox = OutgoingMessageQueue()
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || is_server: {self.is_server} || remote server : {self.remote_peer_address}")

    def run(self):
        self.status = HostStates.PEER_UNREGISTERED
        if self.is_server:
            self.server_routine()
        else:
            self.client_routine()

    def server_routine(self):

        connection = None
        logging.log(logging.DEBUG, f"{self.__class__.__name__} || server routine started")

        while not self.status == HostStates.COMM_COMPLETED:
            if self.status == HostStates.PEER_UNREGISTERED:
                connection = HostSocket()
                connection.bind_to_the_host_ip()
                connection.listen_for_connection_request()
                self.status = HostStates.PENDING_CONTACT_FROM_PEER
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || registration completed")

            elif self.status == HostStates.PENDING_CONTACT_FROM_PEER:
                msg = connection.receive_data()
                downloaded_file_path = self.write_to_file(msg)
                self.outbox.push(downloaded_file_path)
                self.status = HostStates.DATA_TRANSMISSION_PENDING
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || reception of data done")

            elif self.status == HostStates.DATA_TRANSMISSION_PENDING:
                msg = self.outbox.get()
                connection.transmit_data(msg)
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || data transmission done | to exit")
                self.status = HostStates.COMM_COMPLETED

        logging.log(logging.DEBUG, f"{self.__class__.__name__} || server routine is completed")

    def client_routine(self):

        connection = None

        logging.log(logging.DEBUG, f"{self.__class__.__name__} || client routine started")

        while not self.status == ClientStates.COMM_COMPLETED:
            if self.status == ClientStates.PEER_UNREGISTERED:
                connection = ClientSocket(self.remote_peer_address[1], self.remote_peer_address[0])
                connection.connect_to_remote_socket()
                self.status = ClientStates.PENDING_CONNECTION_TO_PEER
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || registration completed")

            elif self.status == ClientStates.PENDING_CONNECTION_TO_PEER:
                msg = self.inbox.get()
                connection.transmit_data(msg)
                self.status = ClientStates.DATA_RECEPTION_PENDING
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || data transmission completed")

            elif self.status == ClientStates.DATA_RECEPTION_PENDING:
                msg = connection.receive_data()
                downloaded_file_path = self.write_to_file(msg)
                self.outbox.push(downloaded_file_path)
                logging.log(logging.DEBUG, f"{self.__class__.__name__} || data reception completed")
                self.status = ClientStates.COMM_COMPLETED

        logging.log(logging.DEBUG, f"{self.__class__.__name__} || client routine completed")

    def write_to_file(self, data, file_path=Configurations().get_download_file_path()):
        with open(file_path, "w") as file:
            file.write('<?xml version="1.0" encoding="UTF-8" >')
            file.write("\n")
            file.write(data)
        return file_path
