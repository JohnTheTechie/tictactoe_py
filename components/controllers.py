import components.board as bc
import random


class BaseCoinShuffler:
    """
    class for assigning a coin at random to the player objects
    """
    def __init__(self, host_player: bc.BasePlayer, client_player: bc.BasePlayer):
        self.host_player: bc.BasePlayer = host_player
        self.client_player: bc.BasePlayer = client_player

    def shuffle_deck(self):
        """
        function to randomly assign the coins to each player
        :return: None
        """
        pass

    def reset_shuffler(self):
        """
        reinitialize the shuffler
        :return:
        """
        pass


class SimpleCoinShuffler(BaseCoinShuffler):

    def __init__(self, host_player: bc.BasePlayer, client_player: bc.BasePlayer):
        BaseCoinShuffler.__init__(self, host_player, client_player)
        self.is_first_time_shuffling = True

    def shuffle_deck(self):
        index = random.randint(1, 2)
        if self.is_first_time_shuffling:
            self.__assign_coins(index)
            self.is_first_time_shuffling = False
        else:
            self.__switch_coins_of_the_players()

    def reset_shuffler(self):
        self.is_first_time_shuffling = True

    def __assign_coins(self, rand_int: int):
        """
        private function called when the coins are assigned for the first time
        :param rand_int: random integer generated for decision making
        :return: None
        """
        if rand_int == 1:
            self.host_player.coin = bc.Coin.PIECE_X
            self.client_player.coin = bc.Coin.PIECE_O
        else:
            self.host_player.coin = bc.Coin.PIECE_O
            self.client_player.coin = bc.Coin.PIECE_X

    def __switch_coins_of_the_players(self):
        """
        swap the coins assigned to each player
        :return: None
        """
        self.host_player.coin, self.client_player.coin = self.client_player.coin, self.host_player.coin
