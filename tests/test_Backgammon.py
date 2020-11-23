import logging
from pprint import pprint
from unittest import TestCase

from Backgammon import Checker, Game, Die
from Player import HumanPlayer
from move_verifier import game_moves_are_valid


class TestValidation(TestCase):
    black = HumanPlayer(Checker.BLACK)
    white = HumanPlayer(Checker.WHITE)

    logging.basicConfig(level=logging.DEBUG)

    def setUp(self) -> None:
        self.game = Game(self.black, self.white)

    def test_move_checkers_from_valid_to_valid_with_no_items_out_and_not_in_home_success(self):
        self.game.current_dice = Die(3, 4)
        print(self.game.board)
        self.assertIsNone(game_moves_are_valid(self.black, [(13, 9), (13, 10)], self.game))

    def test_move_checkers_from_valid_to_invalid_target_location_with_no_items_out_and_not_in_home_fail(self):
        self.game.current_dice = Die(1, 4)
        self.assertRaises(ValueError, lambda: game_moves_are_valid(self.black, [(13, 12), (13, 9)], self.game))

    def test_move_checkers_invalid_checker_fail(self):
        self.game.current_dice = Die(1, 4)
        pprint(self.game.board.board)
        self.assertRaises(ValueError, lambda: game_moves_are_valid(self.white, [(13, 14), (12, 8)], self.game))
