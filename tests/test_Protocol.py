import logging
from unittest import TestCase

from Backgammon import Checker
from Player import HumanPlayer
from Protocol import printMoves, Protocol

logging.basicConfig(level=logging.CRITICAL)


class Test(TestCase):
    logging.basicConfig(level=logging.DEBUG)

    def test_double_two_move_two_checkers_serial(self):
        self.assertEqual("24/22 24/22 22/20", printMoves([(24, 22), (24, 22), (22, 20)]))

    def test_double_two_move_two_checkers_serial2(self):
        self.assertEqual("24/22 24/22 22/20 22/20", printMoves([(24, 22), (24, 22), (22, 20), (22, 20)]))

    def test_normal_two_moves(self):
        self.assertEqual("24/22 23/17", printMoves([(24, 22), (23, 17)]))

    def test_normal_one_entry_one(self):
        self.assertEqual("0/22 7/1", printMoves([(0, 22), (7, 1)]))

    def test_move_one_normal_and_one_off(self):
        self.assertEqual("0/22 7/0", printMoves([(0, 22), (7, 0)]))

    def test_cannot_move(self):
        self.assertEqual("", printMoves([]))

    def test_readProtocol(self):
        prot = Protocol(HumanPlayer(Checker.WHITE), HumanPlayer(Checker.BLACK), 'prototoread','r')
