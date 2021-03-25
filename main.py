from BackammonGamer import load_trainings_data
from Backgammon import Checker, Board, Game
from Player import AiPlayer, RandomPlayer
from mapper import NNMapper

if __name__ == '__main__':
    node_mapper = NNMapper()
    player1 = AiPlayer(Checker.WHITE)
    player2 = RandomPlayer(Checker.BLACK)
    board = Board(player1, player2)

    game = Game(player_1=player1, player_2=player2, create_protocol=True)
    game.run()
