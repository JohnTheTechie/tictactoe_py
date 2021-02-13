from unittest import TestCase
from components.board import *


class TestBoard(TestCase):

    def test_board(self):
        board = SimpleBoard()
        for key, value in board.get_map().items():
            self.assertEqual(board.get_map()[key], Coin.EMPTY)
        board.set_cell(0, 1, Coin.PIECE_O)
        self.assertEqual(board.get_cell(0, 1), Coin.PIECE_O)
        board.set_cell(0, 2, Coin.PIECE_X)
        self.assertEqual(board.get_cell(0, 2), Coin.PIECE_X)
        board.clear_board()
        self.assertEqual(board.get_cell(0, 2), Coin.EMPTY)

    def test_player(self):
        player1 = BasePlayer(is_host=True)
        self.assertTrue(player1.is_host)
        player2 = BasePlayer(is_host=False)
        self.assertEqual(player2.get_name()[-1:], "2")
        player2 = None
        player1 = None
        player2 = BasePlayer(is_host=True)
        self.assertEqual(player2.get_name()[-1:], "1")
        player2.set_turn(True)
        self.assertTrue(player2.is_holding_turn)
        player2.set_turn(False)
        self.assertFalse(player2.is_holding_turn)

    def test_player_controller(self):
        player1 = BasePlayer(is_host=True)
        player2 = BasePlayer(is_host=False)
        player3 = BasePlayer(is_host=False)
        controller = SimplePlayerControllerQueue()
        controller.add_player_to_the_game(player1)
        controller.add_player_to_the_game(player2)
        with self.assertRaises(Exception):
            controller.add_player_to_the_game(player3)
        controller.remove_player_from_the_game(player2)
        controller.add_player_to_the_game(player3)
        self.assertEqual(player1, controller.get_current_player())
        controller.round_completed()
        self.assertEqual(player3, controller.get_current_player())
        controller.set_player_queue([player2, player3])
        self.assertEqual(player2, controller.get_current_player())
