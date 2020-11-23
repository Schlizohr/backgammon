from Backgammon import Checker, Game
from Player import RandomPlayer


class Simulation:
    def __init__(self):
        self.player1 = RandomPlayer(Checker.WHITE)
        self.player2 = RandomPlayer(Checker.BLACK)
        self.game = Game(self.player1, self.player2)

    def run(self):
        self.game.run()
