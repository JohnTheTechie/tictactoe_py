
import socket
from threading import Thread
import logging
from queue import Queue
from enum import Enum


class CommConstants:
    DEFAULT_PORT = 12121
    DEFAULT_HOST_ADDRESS = socket.gethostbyname(socket.gethostname()).split("/")[0]
    POLLING_REQUEST_STRING = "poll_msg"
    POLLING_RESPONSE_STRING = "resp_msg"
    POLLING_MESSAGE_LENGTH = 8
    MAX_CONCURRENT_CONNECTIONS = 5


class CommAgentStates(Enum):
    CLIENT_PEER_NOT_DETECTED = 0x01
    CLIENT_PEER_DETECTED = 0x02
    CLIENT_PEER_NOT_REACHABLE = 0x05
    SERVER_PEER_NOT_DETECTED = 0x03
    SERVER_PEER_DETECTED = 0x04
    SERVER_PEER_NOT_REACHABLE = 0x06


class CommStateContainer:

    STATUS_POLLING_COMPLETED = "polling"

    def __init__(self):
        self.is_server = False
        self.status_map = {CommStateContainer.STATUS_POLLING_COMPLETED: False}

    def get_status(self, component_id):
        assert component_id in self.status_map
        status = self.status_map[component_id]
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | get_status | {component_id}:{status}")
        return status


class ServerPollingInfoContainer:

    __singleton = None

    def __init__(self, polling_message="123456"):
        self.polling_msge = polling_message
        self.polling_resp = self.__calculate_response(polling_message)
        self.status_map = {CommStateContainer.STATUS_POLLING_COMPLETED: False}
        self.client_list = []

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

    def __calculate_response(self, message):
        response = hex((int("0x123456", 16)) ^ 0xffffff)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | calculate_response | {message}:{response}")
        return response

    def get_status(self, component_id):
        assert component_id in self.status_map
        status = self.status_map[component_id]
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | get_status | {component_id}:{status}")
        return status

    def push_client_to_queue(self, client_pair:tuple):
        self.client_list.append(client_pair)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | push_client_to_queue | {client_pair}")


class PeerPollingAgent(Thread):

    def __init__(self, address):
        Thread.__init__(self)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address

    def run(self):
        try:
            print(f"connecting to {self.address}")
            self.conn.connect((self.address, 12121))
            self.conn.send("trial!".encode())
            data = self.conn.recv(CommConstants.POLLING_MESSAGE_LENGTH).decode()
            if self.is_poll_response_valid(data):
                self.update_peer_detection()
        except TimeoutError:
            logging.log(logging.DEBUG, f"{self.__class__.__name__} | TimeoutError | {self.address}")
        except ConnectionRefusedError:
            logging.log(logging.DEBUG, f"{self.__class__.__name__} | ConnectionRefusedError | {self.address}")
        except Exception as e:
            logging.log(logging.DEBUG, f"{self.__class__.__name__} | Exception | {e} | {self.address}")

    def is_poll_response_valid(self, received_response):
        result = received_response == CommConstants.POLLING_RESPONSE_STRING
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | is_poll_response_valid | {received_response} | {result}")
        return result

    def update_peer_detection(self):
        pass


class PeerPollingReceptor(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.polling_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.polling_socket.bind((socket.gethostname(), CommConstants.DEFAULT_PORT))
        self.is_client_identified = False
        self.client_address = None

    def run(self) -> None:
        self.polling_socket.listen(CommConstants.MAX_CONCURRENT_CONNECTIONS)
        while True:
            conn, address = self.polling_socket.accept()


'''
class ServerSocket(Thread):
    """
    socket for receiving the connection requests from the clients
    this server socket needs to be handled by a separate thread for just receiving the connection details
    the handling of the received data should be transferred to a different thread
    """

    def __init__(self, socket_addr: tuple = (socket.gethostname(), 10101), maximum_connections_allowed: int = 5):
        Thread.__init__(self)
        self.server_ip = socket_addr[0]
        self.server_port = socket_addr[1]
        self.maximum_connections_allowed = maximum_connections_allowed
        self.output_queue: Queue = Queue()
        self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | ")
        logging.log(logging.DEBUG,
                    f"{self.__class__.__name__} | server socket created | {socket_addr},{maximum_connections_allowed} ")

    def bind_socket(self):
        """
        binds the socket to the required ip address
        :return: None
        """
        self.socket_connection.bind((self.server_ip, self.server_port))
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | socket bound to ip {self.server_ip}")

    def get_connection_socket(self):
        """
        listens to the port for remote requests from the client
        :return: remote address
        """
        logging.log(logging.DEBUG, f"{self.__class__.__name__} | listening for remote requests")
        self.socket_connection.listen(self.maximum_connections_allowed)
        return self.socket_connection.accept()

    def run(self):
        """
        infinite loop to check for requests and return the request details
        :return: socket Address
        """
        self.bind_socket()

        while True:
            remote_socket_connection = self.get_connection_socket()
            self.output_queue.put(remote_socket_connection)


class ClientRequestHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        pass
'''