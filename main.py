from Backgammon import Checker, Game
from Player import HumanPlayer

player_1 = HumanPlayer(Checker.WHITE)
player_2 = HumanPlayer(Checker.BLACK)
game = Game(player_1, player_2, True)
game.run()
# die = Die(5, 6)
# moves_1 = move_generator.generate_moves(player_1, die, game.board.get_view())
# moves_2 = move_generator.generate_moves(player_2, die, game.board.get_view(True))
# print(moves_1)
# print(moves_1 == moves_2)
