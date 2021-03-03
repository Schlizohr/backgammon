import os

import jsonpickle

from Backgammon import Game, Player, Checker, GameStateLog, Die
from Player import HumanPlayer


def load_latest_game_state() -> GameStateLog:
    path = os.path.abspath("log/board_state.log")
    with open(path, "r") as f:
        last_line = f.readlines()[-1]
        obj = jsonpickle.decode(last_line)
        return obj


class DebugPlayer(Player):

    def __init__(self, color: Checker, move):
        super().__init__(color)
        self.move = move

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        return self.move


if __name__ == "__main__":
    game_state = load_latest_game_state()
    game_state
    player2_color = Checker.WHITE if game_state.player.color == Checker.BLACK else Checker.BLACK
    debug_player: DebugPlayer = DebugPlayer(game_state.player.color, game_state.moves)
    player2: HumanPlayer = HumanPlayer(player2_color)
    game: Game = Game(debug_player, player2)
    game.current_player = debug_player
    game.board.board = game_state.board
    game.current_dice = game_state.die
    game.play()
