import socket
import time
import os
import threading


class SocketCommAgent:
    """
    Base class for socket communication agent
    To be overridden for customizing the socket read behavior
    """
    def __init__(self, conn_socket: socket.socket, codex=None):
        # socket object
        self.conn_socket = conn_socket
        # size of single block of data to be read from buffer
        self.buffer_size = 1024
        # codex object for encoding and decoding the message
        self.codex = None

    def transmit_data(self, data) -> int:
        """
        Implement to transmit over network
        return codes:
            1   - successful transmission
            -1  - loss of connection. Message partially sent.
        :param data: data to be sent over network, in string format
        :return: process return code
        """
        raise NotImplemented

    def receive_data(self, message_size: int) -> (str, int):
        """
        Implement to read the data from the read buffer

        returns path at which read data is stored and return process code

        return codes:
            1   : successful reception
            -1  : partial message read. Request retransmission

        :param message_size: expected size of the message
        :return: path_of_message_file, process code
        """
        raise NotImplemented


class SizeSpecifiedSocketCommAgent(SocketCommAgent):

    def __init__(self, conn_socket: socket.socket):
        SocketCommAgent.__init__(self, conn_socket)
        self.size_indicator_length = 10

    def transmit_data(self, data) -> int:
        """
        return codes:
            0   - successful transmission
            -1  - loss of connection. Message partially sent.

        :param data:
        :return: int
        """
        data = self.__compose_size_message(len(data)) + data

        message_to_transmit = data.encode()
        message_length = len(data) + self.size_indicator_length
        total_transferred_size = 0

        while total_transferred_size < message_length:
            transferred_size = self.conn_socket.send(message_to_transmit[total_transferred_size:])
            if transferred_size != 0:
                total_transferred_size += transferred_size
            else:
                return -1

        return 0

    def receive_data(self, message_size: int = 0):
        """
        return codes:
            0   : successful reception
            -1  : partial message read. Request retransmission

        :param message_size:
        :return: path_of_message_file, process code
        """
        #
        if message_size == 0:
            len_message = self.conn_socket.recv(self.size_indicator_length)
            message_size = self.__calculate_message_size(len_message)

        file_label = time.asctime().replace(" ", "_") + ".msg"
        file_path = os.path.join(os.getenv("TEMP"), file_label)

        received_size = 0

        with open(file_path, "w") as FILE:
            while received_size < message_size:
                blob = self.conn_socket.recv(min(message_size - received_size, self.buffer_size))
                message = blob.decode()
                message_size = len(message)
                if message_size != 0:
                    received_size += message_size
                    FILE.write(message)
                else:
                    return None, -1
        return file_path, 0

    def __compose_size_message(self, data_length: int):
        hex_rep = hex(data_length + 2 + self.size_indicator_length)
        if len(hex_rep) < self.size_indicator_length:
            filler_0_count = self.size_indicator_length - len(hex_rep) - 2
            hex_rep = "0x" + ("0" * filler_0_count) + hex_rep.split("x")[1]
        size_indicator_string = "<" + hex_rep + ">"
        return size_indicator_string

    def __calculate_message_size(self, message):
        decoded_message = message.decode()
        hex_rep = decoded_message.replace("<", "").replace(">", "")
        int_rep = int(hex_rep, 16)
        return int_rep

