import socket
import threading
from tcp.network_config import NetworkConfiguration


class HostThread(threading.Thread):

    def __init__(self,
                 addr=NetworkConfiguration().local_machine_id,
                 port=NetworkConfiguration().configured_application_port,
                 max_conn = NetworkConfiguration().maximum_allowed_connection):
        threading.Thread.__init__(self)
        self.host_address = addr
        self.host_port = port
        self.max_connection = max_conn
        self.host_conn = socket.socket()
        self.host_conn.bind((self.host_address, self.host_port))

        self.is_ok_to_listen = True
        self.terminate_flag_is_set = False

    def run(self) -> None:

        while self.is_ok_to_listen:
            self.host_conn.listen(self.max_connection)
            connection_socket, client_address = self.host_conn.accept()
            # TODO: implement HostSubThread
            HostSubThread(connection_socket, client_address).start()


class HostSubThread(threading.Thread):
    pass
