import logging
import pprint
from unittest import TestCase

from Backgammon import Checker, Game, Die
from Player import HumanPlayer
from move_generator import generate_moves

logging.basicConfig(level=logging.CRITICAL)


class Test(TestCase):
    black = HumanPlayer(Checker.BLACK)
    white = HumanPlayer(Checker.WHITE)

    logging.basicConfig(level=logging.DEBUG)

    def setUp(self) -> None:
        self.game = Game(self.black, self.white)

    def test_move_generator_double_six(self):
        pprint.pprint(generate_moves(self.white, Die(6, 6), self.game.board))

    def test_move_generator_one_and_two(self):
        pprint.pprint(generate_moves(self.white, Die(1, 2), self.game.board))

    def test_move_generator_one_and_two_and_one_out(self):
        self.game.board.remove_from(19)
        self.game.board.place_at(0, self.white.color)
        pprint.pprint(generate_moves(self.white, Die(1, 2), self.game.board))

    def test_move_generator_one_and_two_one_not_in_home(self):
        self.fill_home()
        self.game.board.place_at(18, self.white.color)
        pprint.pprint(generate_moves(self.white, Die(1, 2), self.game.board))

    def test_move_generator_five_six_in_home_one_out(self):
        self.fill_home()
        self.game.board.place_at(0, self.white.color)
        self.assertEqual(len(generate_moves(self.white, Die(5, 6), self.game.board)), 3)

    def test_move_generator_double_six_black(self):
        pprint.pprint(generate_moves(self.black, Die(6, 6), self.game.board))

    def test_move_generator_one_and_two_and_one_out_black(self):
        self.game.board.remove_from(19)
        self.game.board.place_at(0, self.black.color)
        pprint.pprint(generate_moves(self.black, Die(1, 2), self.game.board))

    def test_move_generator(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(23, self.white.color, 2)
        pprint.pprint(generate_moves(self.white, Die(4, 6), self.game.board))

    def fill_home(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(24, self.white.color, 2)
        self.game.board.place_at(23, self.white.color, 2)
        self.game.board.place_at(22, self.white.color, 2)
        self.game.board.place_at(21, self.white.color, 2)
        self.game.board.place_at(20, self.white.color, 2)
        self.game.board.place_at(19, self.white.color, 2)
