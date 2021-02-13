from components import board


class GameGuiInterface:

    def update_location(self, row_index: int, column_index: int, piece):
        raise NotImplementedError

    def refresh_board(self):
        raise NotImplementedError

    def assign_for_player1(self, player_type: board.PlayerType, piece):
        raise NotImplementedError

    def assign_for_player2(self, player_type: board.PlayerType, piece):
        raise NotImplementedError

    def deliver_winner(self, piece):
        raise NotImplementedError
