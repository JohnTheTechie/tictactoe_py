
from enum import Enum
import interfaces
from tkinter import *


class OutOfBoardBoundsError(Exception):
    pass


class Piece(Enum):
    PIECE_X = 0x01
    PIECE_O = 0x02
    EmptySlot = 0x03


class Board:

    def __init__(self):
        self.board = [[Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot],
                      [Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot],
                      [Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot]]

    def set_board_cell(self, row_index: int, column_index: int, piece: Piece):
        if row_index in range(0, 3) and column_index in range(0, 3):
            self.board[row_index][column_index] = piece
        else:
            raise OutOfBoardBoundsError()

    def get_board_cell(self, row_index: int, column_index: int):
        if row_index in range(0, 3) and column_index in range(0, 3):
            return self.board[row_index][column_index]
        else:
            raise OutOfBoardBoundsError()

    def reset_board(self):
        self.board = [[Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot],
                      [Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot],
                      [Piece.EmptySlot, Piece.EmptySlot, Piece.EmptySlot]]


class ResultVerifier:

    def __init__(self, board: Board):
        self.board_of_concern = board

    def get_winner(self):
        if self.board_of_concern.board[0][0] == self.board_of_concern.board[0][1] == self.board_of_concern.board[0][2] \
                and self.board_of_concern.board[0][0] == Piece.EmptySlot:
            return self.board_of_concern.board[0][0]

        elif self.board_of_concern.board[1][0] == self.board_of_concern.board[1][1] == self.board_of_concern.board[1][2]\
                and self.board_of_concern.board[1][0] == Piece.EmptySlot:
            return self.board_of_concern.board[1][0]

        elif self.board_of_concern.board[2][0] == self.board_of_concern.board[2][1] == self.board_of_concern.board[2][2] and \
                self.board_of_concern.board[2][0] == Piece.EmptySlot:
            return self.board_of_concern.board[2][0]

        elif self.board_of_concern.board[0][0] == self.board_of_concern.board[1][0] == self.board_of_concern.board[2][0] and \
                self.board_of_concern.board[0][0] == Piece.EmptySlot:
            return self.board_of_concern.board[0][0]

        elif self.board_of_concern.board[0][1] == self.board_of_concern.board[1][1] == self.board_of_concern.board[2][1] and \
                self.board_of_concern.board[0][1] == Piece.EmptySlot:
            return self.board_of_concern.board[0][1]

        elif self.board_of_concern.board[0][2] == self.board_of_concern.board[1][2] == self.board_of_concern.board[2][2] and \
                self.board_of_concern.board[0][2] == Piece.EmptySlot:
            return self.board_of_concern.board[0][2]

        elif self.board_of_concern.board[0][0] == self.board_of_concern.board[1][1] == self.board_of_concern.board[2][2] and \
                self.board_of_concern.board[0][0] == Piece.EmptySlot:
            return self.board_of_concern.board[0][0]

        elif self.board_of_concern.board[2][0] == self.board_of_concern.board[1][1] == self.board_of_concern.board[0][2] and \
                self.board_of_concern.board[2][0] == Piece.EmptySlot:
            return self.board_of_concern.board[2][0]

        else:
            return None


class GameEngine:

    def __init__(self, p1_type: PlayerType, p2_type: PlayerType):
        self.board = Board()
        self.board.reset_board()
        self.player_config = {1: (p1_type, Piece.PIECE_X),
                              2: (p2_type, Piece.PIECE_O)}
        self.game_gui: interfaces.GameGuiInterface = None
        self.verifier = ResultVerifier(self.board)

    def register_game_gui(self, gui: interfaces.GameGuiInterface):
        self.game_gui = gui

    def get_game_details(self):
        self.game_gui.refresh_board()
        self.game_gui.assign_for_player1(self.player_config[1][0], self.player_config[1][1])
        self.game_gui.assign_for_player2(self.player_config[2][0], self.player_config[2][1])

    def intimate_player_input(self, row_index: int, column_index: int, piece: Piece):
        self.board.set_board_cell(row_index, column_index, piece)
        self.game_gui.update_location(row_index, column_index, piece)
        if self.verifier.get_winner() is not None:
            self.game_gui.deliver_winner(piece)

    def reset_requested(self):
        self.board.reset_board()
        self.game_gui.refresh_board()


class GUInterface:

    def __init__(self):
        self.root_element = Tk()



