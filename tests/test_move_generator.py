import logging
import pprint
from unittest import TestCase

from Backgammon import Checker, Game, Die
from Player import HumanPlayer, RandomPlayer
from move_generator import generate_moves, generate_moves_serial

logging.basicConfig(level=logging.CRITICAL)


class Test(TestCase):
    black = HumanPlayer(Checker.BLACK)
    white = HumanPlayer(Checker.WHITE)

    logging.basicConfig(level=logging.DEBUG)

    def setUp(self) -> None:
        self.game = Game(self.black, self.white, create_protocol=False)

    def test_move_generator_double_six(self):
        pprint.pprint(generate_moves(self.white, Die(6, 6), self.game.board))

    def test_move_generator_double_two(self):
        pprint.pprint(generate_moves(self.white, Die(2, 2), self.game.board))

    def test_move_generator_double_three(self):
        pprint.pprint(generate_moves(self.white, Die(3, 3), self.game.board))

    def test_move_generator_one_and_two(self):
        pprint.pprint(generate_moves(self.white, Die(2, 3), self.game.board))

    def test_move_generator_one_and_two_and_one_out(self):
        self.game.board.remove_from(19)
        self.game.board.place_at(0, self.white.color)
        pprint.pprint(generate_moves(self.white, Die(1, 2), self.game.board))

    def test_move_generator_one_and_two_one_not_in_home(self):
        self.fill_home()
        self.game.board.place_at(7, self.white.color)
        pprint.pprint(self.game.board)
        pprint.pprint(generate_moves(self.white, Die(5, 6), self.game.board))

    def test_move_generator_five_six_in_home_one_out(self):
        self.fill_home()
        self.game.board.place_at(0, self.white.color)
        moves = generate_moves(self.white, Die(5, 6), self.game.board)
        pprint.pprint(moves)
        self.assertEqual(len(moves), 3)

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
        self.game.board.place_at(1, self.white.color, 2)
        self.game.board.place_at(2, self.white.color, 2)
        self.game.board.place_at(3, self.white.color, 2)
        self.game.board.place_at(4, self.white.color, 2)
        self.game.board.place_at(5, self.white.color, 2)
        self.game.board.place_at(6, self.white.color, 2)

    def test_move_white_checker_from_bar_in(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(0, self.white.color, 1)
        moves = generate_moves(self.white, Die(2, 3), self.game.board)
        expected_moves = [
            [(0, 22), (22, 20)],
            [(0, 23), (23, 20)]
        ]
        self.assertEqual(moves, expected_moves)

    def test_move_dark_checker_from_bar_in(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(0, self.black.color, 1)
        print(self.game.board)
        moves = generate_moves_serial(self.black, Die(2, 3), self.game.board)
        expected_moves = [
            [(0, 22), (22, 20)],
            [(0, 23), (23, 20)]
        ]
        pprint.pprint(moves)
        self.assertEqual(moves, expected_moves)

    def test_parallel_move_dark_checker_from_bar_in(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(0, self.black.color, 1)
        print(self.game.board)
        moves = generate_moves(self.black, Die(2, 3), self.game.board)
        expected_moves = [
            [(0, 22), (22, 20)],
            [(0, 23), (23, 20)]
        ]
        pprint.pprint(moves)
        self.assertEqual(moves, expected_moves)

    def test_two_out_can_move_only_one(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(0, self.black.color, 1)
        self.game.board.place_at(0, self.black.color, 1)

        self.game.board.place_at(19, self.white.color, 1)
        self.game.board.place_at(19, self.white.color, 1)

        moves = generate_moves_serial(self.black, Die(2, 6), self.game.board)
        expected_moves = [[(0, 23)]]
        self.assertEqual(moves, expected_moves)

    def test_black_move_out(self):
        rand_black = RandomPlayer(Checker.BLACK)
        human_white = RandomPlayer(Checker.WHITE)

        game = Game(player_1=human_white, player_2=rand_black, create_protocol=False)
        game.board.board = game.board.clear_board()
        game.current_player = rand_black
        game.current_dice = Die(4, 6)
        game.board.place_at(19, Checker.BLACK, 1)
        game.board.place_at(22, Checker.BLACK, 1)

        game.board.place_at(18, Checker.WHITE, 4)

        game.run()

        moves = generate_moves_serial(self.black, Die(4, 6), game.board.get_view(True))
        print(moves)

    def test_black_move_out_4(self):
        self.game.board.board = self.game.board.clear_board()
        self.game.board.place_at(22, self.black.color, 4)
        self.game.board.place_at(21, self.black.color, 2)
        self.game.current_player = self.black

        self.game.board.place_at(23, self.white.color, 6)
        print(self.game.board.get_view(True))

        moves = generate_moves_serial(self.black, Die(4, 4), self.game.board.get_view(True))
        print(moves)
        # expected_moves = [[(0, 23)]]
        # self.assertEqual(moves, expected_moves)
