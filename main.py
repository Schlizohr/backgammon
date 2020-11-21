from Backgammon import Game, Checker
from Player import HumanPlayer

player_1 = HumanPlayer(Checker.WHITE)
player_2 = HumanPlayer(Checker.BLACK)
game = Game(player_1, player_2)
game.run()
