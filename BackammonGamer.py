from copy import deepcopy
from random import choice

from Backgammon import Player, Die, Board
from move_generator import generate_moves


class Gamer(Player):
    def __init__(self, color):
        # board, before, dices, returned moves
        super().__init__(color)
        self.game_log: [(Board, [int], [(int, int)])] = []
        self.game_reward = 0

    def calculate_moves(self, dices: [int], board) -> [(int, int)]:
        moves_options = generate_moves(self, Die(dices[0], dices[1]), board)
        moves = []
        if len(moves_options) > 0:
            moves = choice(moves_options)
        self.game_log.append((deepcopy(board), dices, moves))
        return moves

    def reward(self, points):
        self.game_reward = points * 10


class BackgammonAlphaZeroGameAdapter:
    pass

# class GamerGameAdapter(Game):
#
#     def __init__(self, player_1, player_2):
#         super().__init__(player_1, player_2)
#         self.winners_log = None
#         self.winners_points = 0
#         self.loser_log = None
#         self.loser_points = 0
#
#     def notify_player(self, current_player: Gamer):
#         super().notify_player(current_player)
#         self.winners_points = current_player.game_reward
#         self.winners_log = current_player.game_log
#
#     def get_winners_information(self):
#         return self.winners_log, self.winners_points
#
#
# def winner_data_generator() -> ([(Board, [int], [(int, int)])], int):
#     player_1 = Gamer(Checker.WHITE)
#     player_2 = Gamer(Checker.BLACK)
#     game = GamerGameAdapter(player_1, player_2)
#     game.run()
#     return game.get_winners_information()
#
#
# def generate_model():
#     game_board = Input((25, 15))
#     die = Input((2,))
#     concat_layer = Concatenate()([game_board, die])
#     out = Dense(8)
#     model = Model(inputs=[game_board, die], output=out)
#     plot_model(model)
#     return model
