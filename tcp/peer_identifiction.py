
import logging
import socket
import threading
import time

SERVER_POLLING_WAITING_DURATION = 30
SERVER_POLLING_WAITING_DURATION_SHORT = 5


class PeerIdentifier:
    """
    Class to manage the polling threads to identify the peer network member

    for normal use intialize the object with is_server argument
    then call get_peer_connections(self). address of the peer shall be returned
    """
    APPLICATION_PORT = 12121
    HOST_ADDRESS = socket.gethostbyname(socket.gethostname()).split("/")[0]
    POLLING_REQUEST_STRING = "poll_msg"
    POLLING_RESPONSE_STRING = "resp_msg"
    POLLING_STRING_LENGTH = 8
    MAX_CONCURRENT_CONNECTIONS = 5

    def __init__(self, id_key: str = "0x123456",
                 is_server: bool = True,
                 port=APPLICATION_PORT,
                 host_address=HOST_ADDRESS):

        PeerIdentifier.POLLING_REQUEST_STRING = id_key
        PeerIdentifier.POLLING_RESPONSE_STRING = self.__calculate_response(id_key)
        PeerIdentifier.APPLICATION_PORT = port
        PeerIdentifier.HOST_ADDRESS = host_address
        self.is_server = is_server
        # variable to maintain the list of all peers identified by the server
        self.registered_peer_list = []
        # variable to keep count of sub threads started
        self.active_server_subthread_count = 0
        logging.debug(f"{self.__class__.__name__} | Created")

    def __calculate_response(self, message):
        """
        function calculates the corresponding response for the specified poll message to be sent back as response
        :param message: str
        :return: hashed version of message which can be sent as a response
        """
        response = hex((int("0x123456", 16)) ^ 0xffffff)
        logging.debug(f"{self.__class__.__name__} | __calculate_response | {message}:{response}")
        return response

    def __register_server_subthread(self):
        """
        function to increase the sub thread count
        to be used by the class to monitor active thread counts to decide when to close the calling thread
        :return: None
        """
        self.active_server_subthread_count += 1
        logging.debug(f"{self.__class__.__name__} | __register_server_subthread | {self.active_server_subthread_count}")

    def __unregister_server_subthread(self):
        """
        function to decrease the sub thread count
        to be used by the class to monitor active thread counts to decide when to close the calling thread
        :return: None
        """
        if self.active_server_subthread_count == 0:
            raise IndexError(f"{self.__class__.__name__} | __unregister_server_subthread | "
                             f"active subthread counter is reduced below 0")
        self.active_server_subthread_count -= 1
        logging.debug(f"{self.__class__.__name__} | ")

    def get_peer_connections(self):
        """
        Function to be used for starting the polling process
        The function returns the collection of remote peer details

        Single item if called as client
        possibly a  list if called as a server

        :return: ip address list
        """
        if self.is_server:
            return self.__get_client_details()
        else:
            return self.__get_server_details()

    def push_peer_details(self, ip_address: tuple):
        """
        When the remote peer is identified the details shall be pushed to the list
        :param ip_address: (socket, address)
        :return: None
        """
        self.registered_peer_list.append(ip_address)
        logging.debug(f"{self.__class__.__name__} | push_peer_details | {ip_address}")

    def __get_client_details(self):
        """
        Function triggering the server side routine to identify the clients
        :return: client list
        """
        server_thread = PeerPollingReceptor(port=PeerIdentifier.APPLICATION_PORT,
                                            max_conc_conn_count=PeerIdentifier.MAX_CONCURRENT_CONNECTIONS,
                                            controller=self)
        server_thread.start()
        server_thread.join()
        logging.debug(f"{self.__class__.__name__} | __get_client_details | completed | {self.registered_peer_list}")
        return self.registered_peer_list

    def __get_server_details(self):
        """
        Function triggering the client side routine to identify the server in the network if any
        :return: server ip address
        """
        client_thread = PeerPollingClient(port=PeerIdentifier.APPLICATION_PORT,
                                          max_conc_conn_count=PeerIdentifier.MAX_CONCURRENT_CONNECTIONS,
                                          controller=self)
        client_thread.start()
        client_thread.join()
        server_address = client_thread.server_ip_address
        logging.debug(f"{self.__class__.__name__} | __get_server_details | {server_address}")
        return server_address


class PeerPollingReceptor(threading.Thread):
    """
    Class for server side application to listen for Client polls
    """

    def __init__(self, port, max_conc_conn_count, controller: PeerIdentifier):
        threading.Thread.__init__(self)
        # prepare socket for listening
        self.polling_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.polling_socket.bind((socket.gethostname(), port))
        # flag for tracking if a client has been identified
        self.is_client_identified = False
        # flag for tracking if a connection request has been accepted
        self.is_processing_request = False
        # the address of the client identified
        self.client_address = None
        # simultaneous connection limit
        self.max_concurrent_conn_count = max_conc_conn_count
        # calling objects reference
        self.controller = controller
        logging.debug(f"{self.__class__.__name__} | created")

    def run(self) -> None:
        # start listening
        self.polling_socket.listen(self.max_concurrent_conn_count)
        # start the timer thread to stop the thread after significant time
        threading.Thread(target=monitor_and_close, args=(self.polling_socket, self)).start()
        logging.debug(f"{self.__class__.__name__} | run | listening started")

        try:
            # need to loop until a client is identified
            while not self.is_client_identified:
                conn, address, key_message = self.__accept_and_read_message()
                logging.debug(f"{self.__class__.__name__} | run | message received | {address}:{key_message}")
                # check if a valid key is received if yes process else restart
                if self.__validate_key(key_message):
                    logging.debug(f"{self.__class__.__name__} | run | {address} key message validated")
                    self.client_address = address
                    self.is_client_identified = True
                    # send the calculated response
                    length = conn.send(PeerIdentifier.POLLING_RESPONSE_STRING.encode())
                    logging.debug(f"{self.__class__.__name__} | {length} bytes sent as response")
                else:
                    # since the connection does not give the expected key, restart the process
                    self.is_processing_request = False
            # loop exited since client established. push it
            self.controller.push_peer_details(self.client_address)

        except WindowsError as e:
            logging.debug(f"{self.__class__.__name__} | {e}")
        except Exception as e:
            logging.debug(f"{self.__class__.__name__} | {e}")

        finally:
            self.polling_socket.close()

    def __accept_and_read_message(self):
        """
        internal function for accepting the connection and processing data
        :return: socket, ip_addr, message received
        """
        # accept the connection request
        conn, address = self.polling_socket.accept()
        # set the flag indicating the process has started
        self.is_processing_request = True
        # read the message from the connection
        key_message = conn.recv(PeerIdentifier.POLLING_STRING_LENGTH).decode()

        logging.debug(f"{self.__class__.__name__} | __accept_and_read_message | {address} | {key_message}")

        return conn, address, key_message

    def __validate_key(self, key_message):
        """
        Process the key received from the connection and compare it to the expected message
        :param key_message: received message
        :return: comparison result
        """
        result = (PeerIdentifier.POLLING_REQUEST_STRING == key_message)
        logging.debug(f"{self.__class__.__name__} | __validate_key | {key_message} | {result}")
        return result


def monitor_and_close(polling_socket, controller: PeerPollingReceptor):
    """
    function to terminate the thread when the timer expires
    :param polling_socket: socket object to be timed
    :param controller: Controlled which give process status
    :return: None
    """
    # Initially sleep for default time
    time.sleep(SERVER_POLLING_WAITING_DURATION)
    # then wait for another intermediate time until a current process, if any, is completed
    while not controller.is_processing_request:
        time.sleep(SERVER_POLLING_WAITING_DURATION_SHORT)
    # when no connection is currently being processed, close the socket
    polling_socket.close()
    logging.debug(f" monitor_and_close | timed out")


class PeerPollingClient(threading.Thread):
    """
    thread class to be used by the client side application to poll for the servers
    """

    def __init__(self, port, max_conc_conn_count, controller: PeerIdentifier):
        threading.Thread.__init__(self)
        # port to which to connect
        self.application_port = port
        # ip id of the network
        self.network_id = self.__identify_network_id()
        # flag to track if the server is identified
        self.is_server_identified = False
        # ip address of the server identified
        self.server_ip_address = None
        # self.server_socket_address_pair = None
        self.max_concurrent_conn_count = max_conc_conn_count
        # calling object reference
        self.controller = controller
        # avctive thread counter
        self.counter = 0
        logging.debug(f"{self.__class__.__name__} | created")

    def run(self) -> None:
        # send key to each possible ip address in the network
        for index in range(2, 255):
            ip_addr = self.__calculate_ip_addr(index)
            # start a new thread to handle a separate ip address
            thread = threading.Thread(target=self.poll, args=(ip_addr, str(index)))
            thread.start()
            logging.debug(f"{self.__class__.__name__} | run | {ip_addr} | polling thread started")

        # wait until all the threads unregister from the counter
        while self.counter > 0:
            time.sleep(0.2)
            # logging.debug(f"{self.__class__.__name__} | run | waiting for polling threads to complete")

    def poll(self, ip_addr, id_num):
        lock = threading.Lock()
        flag = False

        logging.debug(f"{self.__class__.__name__} | poll | {id_num} | {ip_addr} | started")

        # synchronously increment the counter
        lock.acquire()
        self.__increment_counter()
        lock.release()

        try:
            # prepare and connect the socket
            socket_conn = socket.socket()
            socket_conn.connect((ip_addr, self.application_port))
            logging.debug(f"{self.__class__.__name__} | poll | {id_num} |  {ip_addr} | connection established")

            # send the message over network anc confirm
            length = socket_conn.send(PeerIdentifier.POLLING_REQUEST_STRING.encode())
            logging.debug(f"{self.__class__.__name__} | poll | {id_num} |  {ip_addr} | "
                          f"{PeerIdentifier.POLLING_REQUEST_STRING.encode()} of {length} sent")

            # record the data read
            resp = socket_conn.recv(PeerIdentifier.POLLING_STRING_LENGTH).decode()
            logging.debug(f"{self.__class__.__name__} | poll | {id_num} |  {ip_addr} | response received | {resp}")

            # validate the recorded data's integrity
            if len(resp) != PeerIdentifier.POLLING_STRING_LENGTH:
                raise Exception("response from the remote server is truncated")

            # validate the recorded data's validity
            if resp == PeerIdentifier.POLLING_RESPONSE_STRING:
                flag = True
                logging.debug(f"{self.__class__.__name__} | poll | {id_num} |  {ip_addr} | {resp} | validated | {True}")

        except ConnectionRefusedError:
            logging.debug(f"poll | {id_num} |  {ip_addr} | connection refused")

        except ConnectionAbortedError:
            logging.debug(f"poll | {id_num} |  {ip_addr} | connection aborted")

        except Exception as e:
            logging.debug(f"poll | {id_num} |  {ip_addr} | unexpected exception {e}")

        finally:
            # unregister the thread
            lock.acquire()
            self.__decrement_counter()
            if flag:
                self.__update_server_details(ip_addr)
            lock.release()

    def __identify_network_id(self):
        network_id = socket.gethostbyname(socket.gethostname()).rsplit(".", 1)[0]
        logging.debug(f"{self.__class__.__name__} | __identify_network_id | {network_id}")
        return network_id

    def __calculate_ip_addr(self, id_num):
        ip_address = self.network_id + "." + str(id_num)
        logging.debug(f"{self.__class__.__name__} | __calculate_ip_addr | {ip_address}")
        return ip_address

    def __increment_counter(self):
        self.counter += 1
        logging.debug(f"{self.__class__.__name__} | __increment_counter | {self.counter}")

    def __decrement_counter(self):
        self.counter -= 1
        logging.debug(f"{self.__class__.__name__} | __decrement_counter | {self.counter}")

    def __update_server_details(self, ip_address):
        self.is_server_identified = True
        self.server_ip_address = ip_address
        logging.debug(f"{self.__class__.__name__} | __update_server_details | {ip_address}")
