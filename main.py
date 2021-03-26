from pyro.infer.autoguide import AutoDelta

from BackammonGamer import Analyzing, NeuralNetwork
from Backgammon import Checker, Game
from Player import AiPlayer, RandomPlayer


def play_against_ai():
    player1 = AiPlayer(Checker.WHITE)
    player2 = RandomPlayer(Checker.BLACK)

    game = Game(player_1=player1, player_2=player2, create_protocol=True)
    game.run()


if __name__ == '__main__':
    # Analyzing(NeuralNetwork()).analyzing()

    # print("guide auto delta")
    model4 = NeuralNetwork()
    Analyzing(model4, AutoDelta(model4)).analyzing()
