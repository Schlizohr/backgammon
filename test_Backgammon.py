import logging
from unittest import TestCase

from Backgammon import Checker, Game, moves_are_valid
from Player import HumanPlayer


class TestValidation(TestCase):
    black = HumanPlayer(Checker.BLACK)
    white = HumanPlayer(Checker.WHITE)

    logging.basicConfig(level=logging.DEBUG)

    def setUp(self) -> None:
        self.game = Game(self.black, self.white)

    def test_move_checkers_from_valid_to_valid_with_no_items_out_and_not_in_home_success(self):
        self.game.current_dice = (3, 4)
        print(self.game.board)
        self.assertTrue(moves_are_valid(self.black, [(13, 9), (13, 10)], self.game))

    def test_move_checkers_from_invalid_valid_target_location_with_no_items_out_and_not_in_home_fail(self):
        self.game.current_dice = (1, 4)
        self.assertFalse(moves_are_valid(self.black, [(13, 12), (13, 9)], self.game))

    def test_move_checkers_invalid_checker_fail(self):
        self.game.current_dice = (1, 4)
        self.assertFalse(moves_are_valid(self.white, [(12, 16), (12, 13)], self.game))

    def test_moves_are_valid(self):
        self.fail()
