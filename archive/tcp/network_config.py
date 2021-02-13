
import socket


class NetworkConfiguration:

    __singleton = None

    def __init__(self):
        self.local_machine_id = socket.gethostbyname(socket.gethostname())
        self.network_id = self.local_machine_id.rsplit(".")[0]
        self.configured_application_port = 10101
        self.maximum_allowed_connection = 5
        self.authenticated_clients = []

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

