import logging
import os
from random import choice
from time import sleep

from BackammonGamer import AI
from Backgammon import Player, Die, Checker
from mapper import NNMapper
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
        print("throw", dices)
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


class AiPlayer(Player):

    def __init__(self, color: Checker):
        super().__init__(color)
        self.mapper = NNMapper()
        self.ai = AI()

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        print("throw", dices)
        moves_options = generate_moves(self, Die(dices.first, dices.second), board)
        if len(moves_options) == 0:
            return moves_options

        future_boards = self.get_future_boards(moves_options, board)

        node_data = [self.mapper.to_nodes(b, self.color) for b in future_boards]
        win_chance_white: [float] = self.ai.predict(node_data)

        extreme = max(win_chance_white)
        if self.color == Checker.BLACK:
            extreme = min(win_chance_white)

        self.slow(board)
        return moves_options[win_chance_white.index(extreme)]

    def slow(self, board):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(board, end="\r")
        sleep(0.5)

    def fast(self, dices, moves):
        logging.info(f"die: {dices} -> moves: {moves}")

    def invalid_move(self):
        logging.debug("invalid move")

    def get_future_boards(self, moves_options, board):
        possible_boards = []
        for possible_moves in moves_options:
            temp_board = board.get_view()
            for (src, trg) in possible_moves:
                temp_board.move(self.color, src, trg)
            possible_boards.append(temp_board.get_view())
        return possible_boards
