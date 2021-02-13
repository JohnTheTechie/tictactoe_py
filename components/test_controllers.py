from unittest import TestCase
from components.board import *
from components.controllers import *


class TestSimpleCoinShuffler(TestCase):

    def setUp(self) -> None:
        self.host_player = BasePlayer(is_host=True)
        self.client_player = BasePlayer(is_host=False)
        self.controller = SimpleCoinShuffler(self.host_player, self.client_player)
        self.host_player_coin = Coin.EMPTY

    def tearDown(self) -> None:
        self.host_player = None
        self.client_player = None
        self.controller = None
        self.host_player_coin = Coin.EMPTY

    def test_shuffle_deck(self):
        self.controller.shuffle_deck()
        self.assertNotEqual(self.host_player.coin, self.client_player.coin)
        self.assertNotEqual(self.host_player.coin, Coin.EMPTY)
        self.assertNotEqual(self.client_player.coin, Coin.EMPTY)
        self.assertFalse(self.controller.is_first_time_shuffling)

    def test_reset_shuffler(self):
        self.controller.shuffle_deck()
        self.host_player_coin = self.host_player.coin
        self.controller.shuffle_deck()
        self.assertNotEqual(self.host_player_coin, self.host_player.coin)
        self.controller.shuffle_deck()
        self.assertEqual(self.host_player_coin, self.host_player.coin)
        self.controller.shuffle_deck()
        self.assertNotEqual(self.host_player_coin, self.host_player.coin)
