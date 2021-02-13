import socket
import tcp.exceptions as exc
import tcp.sysenvcons as sysenvcons
import threading


class BaseHostListenerSocket:

    def __init__(self, host_socket: socket.socket = None, max_connection: int = 5):
        self.host_socket = host_socket
        self.max_connection = max_connection
        self.port = sysenvcons.BasicTCPConstructs.port
        self.host_address = sysenvcons.BasicTCPConstructs.host
        self.is_bound = False

    def bind_and_listen(self) -> int:
        """
        bind the socket and start listening.
        return codes:
            0   - successful
            1   - retry requested

        :return: int return code
        """
        raise NotImplemented

    def accept(self) -> (socket.socket, str):
        """
        accept the incoming request and return the socket object and remote address
        :return: socket connection, remote address
        """
        raise NotImplemented

    def kill_socket(self) -> int:
        """
        kills the socket and returns the status code
        return code:
            0   - successful
        :return: return code
        """
        raise NotImplemented


class BasicHostListenerSocket(BaseHostListenerSocket):
    """
    Simple implementation of Host Listner
    """

    def __init__(self, host_socket: socket.socket = None, max_connection: int = 5):
        BaseHostListenerSocket.__init__(self, host_socket, max_connection)

    def bind_and_listen(self) -> int:
        self.host_socket.bind((socket.gethostname(), self.port))
        self.host_socket.listen(self.max_connection)
        self.is_bound = True
        return 0

    def accept(self) -> (socket.socket, str):
        if not self.is_bound:
            raise exc.AccessingClosedSocketError("Accessing non-open socket")
        conn, address = self.host_socket.accept()
        assert isinstance(address, str)
        return conn, address

    def kill_socket(self) -> int:
        self.host_socket.close()
        self.is_bound = False
        return 0


class BaseHostDispatcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.host_listener: BaseHostListenerSocket = None
        self.execution_control_flag_is_set = False

    def build(self):
        """
        preps the object for listening loop
        :return: self
        """
        pass

    def close(self):
        pass

    def _listening_process(self):
        pass

    def run(self) -> None:
        pass


class BasicHostDispatcher(BaseHostDispatcher):

    def __init__(self):
        BaseHostDispatcher.__init__(self)

    def build(self):
        if not self.host_listener.is_bound:
            self.host_listener.bind_and_listen()
        return self

    def close(self):
        if self.host_listener.is_bound:
            self.host_listener.kill_socket()
        else:
            self.execution_control_flag_is_set = False

    def _listening_process(self):
        self.execution_control_flag = True
        while self.execution_control_flag_is_set:
            conn_socket, address = self.host_listener.accept()
        # TODO: finish the code

    def run(self) -> None:
        while self.execution_control_flag_is_set:
            self._listening_process()