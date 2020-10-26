from enum import Enum
import logging


class PlayerType(Enum):
    HUMAN = 0x01
    COMP = 0x02
    REMOTE = 0x03


class ConfigurationManager:

    __manager = None

    def __init__(self):
        logging.debug(__class__.__name__+" created")
        self.second_player_type: PlayerType = PlayerType.HUMAN
        self.is_playing_remote_player = False
        self.remote_address: str = "8.8.8.8"
        self.remote_port: int = 0

    def __new__(cls, *args, **kwargs):
        if cls.__manager is None:
            cls.__manager = object().__new__(cls)
        return cls.__manager

    def get_second_player_type(self):
        logging.debug(__class__.__name__+" | get second Player type : " + self.second_player_type.name)
        return self.second_player_type

    def update_second_player_type(self, new_player_type):
        logging.debug(__class__.__name__ + " | update second Player type : " + new_player_type.name)
        self.second_player_type = new_player_type
        self.is_playing_remote_player = (self.second_player_type == PlayerType.REMOTE)

    def set_remote_player_network_attr(self, addr, port):
        if isinstance(addr, str):
            logging.debug(f"{__class__.__name__} +  | setting remote server Attributes | address:port = {addr}:{port}")
            self.remote_address = addr
            self.remote_port = port
        else:
            raise TypeError(f"{__class__.__name__} | assigned address is not in string format")

    def get_remote_player_network_attr(self):
        logging.debug(f"{__class__.__name__} +  | getting remote server Attributes | address:port = {self.remote_address}:{self.remote_port}")
        return self.remote_address,self.remote_port


class Master:

    def __init__(self):
        """
        prepare the environment and call theHMI controller to draw he reception HMI
        """
        self.__config_manager = ConfigurationManager()

        pass

    def call_opening_hmi(self):
