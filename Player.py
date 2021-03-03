import logging
import os
from random import choice
from time import sleep

from Backgammon import Player, Die
from move_generator import generate_moves

logging.basicConfig(level=logging.INFO)


class HumanPlayer(Player):

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        print(board)
        print(self.color.value, "your dices are:", dices)
        moves = []
        number_of_moves = 2
        if dices.first == dices.second:
            number_of_moves = 4

        for i in range(number_of_moves):
            print("input move usage: <src> <target>")
            src, tar = input().strip().split(" ")
            moves.append((int(src), int(tar)))
        return moves


class RandomPlayer(Player):

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        moves_options = generate_moves(self, Die(dices.first, dices.second), board)
        moves = []
        if len(moves_options) > 0:
            moves = choice(moves_options)
        self.slow(board)
        return moves

    def slow(self, board):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(board, end="\r")
        sleep(0.5)

    def fast(self, dices, moves):
        logging.info(f"die: {dices} -> moves: {moves}")

    def invalid_move(self):
        logging.debug("invalid move")
