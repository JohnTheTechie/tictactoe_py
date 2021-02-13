from enum import Enum
from typing import Dict, Tuple, List
import components.listeners


class Coin(Enum):
    PIECE_X = 0x01
    PIECE_O = 0x02
    EMPTY = 0x03


class Board:
    """
    base class for defining coin positions on the gam board
    """
    def __init__(self):
        pass

    def get_map(self) -> dict:
        """
        function returns a map of coordinates and coins

        format should be {(x_coord, y_coord) : coin,,,}

        :return: dict of coord, coins
        """
        raise NotImplemented

    def set_cell(self, x, y, coin_to_insert):
        """
        sets the coin to be mapped to a specified coordinates
        :param x: x coordinate
        :param y: y coordinate
        :param coin_to_insert: Coin enum to be mapped
        :return: None
        """
        raise NotImplemented

    def get_cell(self, x, y) -> Coin:
        """
        return the coin mapped to the specified cell
        :param x: x coordinate
        :param y: y coordinate
        :return: cin enum mapped to the coordinates
        """
        raise NotImplemented

    def clear_board(self):
        """
        clears and initializes the board
        :return: None
        """
        raise NotImplemented


class SimpleBoard(Board):

    def __init__(self):
        Board.__init__(self)
        self.map = {(0, 0): Coin.EMPTY, (0, 1): Coin.EMPTY, (0, 2): Coin.EMPTY,
                    (1, 0): Coin.EMPTY, (1, 1): Coin.EMPTY, (1, 2): Coin.EMPTY,
                    (2, 0): Coin.EMPTY, (2, 1): Coin.EMPTY, (2, 2): Coin.EMPTY}

    def get_map(self) -> Dict[Tuple[int, int], Coin]:
        return self.map

    def set_cell(self, x, y, coin_to_insert):
        self.map[(x, y)] = coin_to_insert
        listener = components.listeners.OnCellUpdatedListener()
        listener.event_update((x, y, coin_to_insert))

    def get_cell(self, x, y) -> Coin:
        return self.map[x, y]

    def clear_board(self):
        for key, value in self.map.items():
            self.map[key] = Coin.EMPTY
        components.listeners.OnCellUpdatedListener().event_update((-1, -1, Coin.EMPTY))


class BasePlayer:
    """
    Base class for encapsulating the player details
    """
    __object_count = 0

    def __init__(self, is_host):
        BasePlayer.__object_count += 1
        self.name: str = f"Player_{BasePlayer.__object_count}"
        self.coin: Coin = Coin.EMPTY
        self.is_holding_turn: bool = False
        self.is_host: bool = is_host

    def set_name(self, name):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def set_turn(self, is_turn: bool):
        self.is_holding_turn = is_turn

    def __del__(self):
        BasePlayer.__object_count -= 1


class BasePlayerQueueController:

    def __init__(self):
        pass

    def get_player_count(self):
        """
        returns the number of the players registered
        :return: int
        """

    def add_player_to_the_game(self, player: BasePlayer):
        """
        function to add a player to the queue controller
        the function simply adds the new player to the end of the list
        :param player: player to be pushed to the queue
        :return: None
        """
        raise NotImplemented

    def remove_player_from_the_game(self, player):
        """
        function to remove a player from he game queue
        :param player: player to be removed
        :return: None
        """
        raise NotImplemented

    def round_completed(self):
        """
        intimates object that the round is completed
        :return:
        """
        raise NotImplemented

    def get_current_player(self) -> BasePlayer:
        """
        retrieve the current player whose turn is up
        :return: Player whose turn is up
        """
        raise NotImplemented

    def set_player_queue(self, p_queue: [BasePlayer]):
        """
        directly reinitialise the player queue
        :param p_queue: new queue order to be adapted
        :return: None
        """
        raise NotImplemented


class SimplePlayerControllerQueue(BasePlayerQueueController):

    def __init__(self):
        BasePlayerQueueController.__init__(self)
        self.__player_queue = []

    def get_player_count(self):
        return len(self.__player_queue)

    def add_player_to_the_game(self, player: BasePlayer):
        if len(self.__player_queue) == 2:
            raise Exception("too many players being pushed into the controller")
        self.__player_queue.append(player)

    def remove_player_from_the_game(self, player):
        self.__player_queue.remove(player)

    def round_completed(self):
        player = self.__player_queue[0]
        self.__player_queue.remove(self.__player_queue[0])
        self.__player_queue.append(player)

    def get_current_player(self) -> BasePlayer:
        return self.__player_queue[0]

    def set_player_queue(self, p_queue: List[BasePlayer]):
        self.__player_queue = p_queue
