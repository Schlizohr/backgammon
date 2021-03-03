import json

from Backgammon import Game, Player, Checker, GameStateLog, Die
from Player import HumanPlayer


def load_latest_game_state() -> GameStateLog:
    with open("../log/board_state.log", "r") as f:
        return json.loads(f.readlines()[-1])


class DebugPlayer(Player):

    def __init__(self, color: Checker.Color, move):
        super().__init__(color)
        self.move = move

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        return self.move


if __name__ == "__main__":
    game_state: GameStateLog = load_latest_game_state()
    player2_color = Checker.WHITE if game_state.player.color == Checker.BLACK else Checker.BLACK
    debug_player: DebugPlayer = DebugPlayer(game_state.player.color, game_state.moves)
    player2: HumanPlayer = HumanPlayer(player2_color)

    game: Game = Game(debug_player, player2)

    game.current_player = debug_player
    game.board.board = game_state.board
    game.current_dice = game_state.die

    game.play()
