import logging
import os
from random import choice
from time import sleep

from BackammonGamer import NNMapper
from Backgammon import Player, Die
from helper.Encoder import MyEncoder
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


class AiPlayer(Player):

    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        moves_options = generate_moves(self, Die(dices.first, dices.second), board)
        moves = []

        future_boards = self.get_future_boards(moves_options, board)

        best_board = -1
        best_value = -1

        for i,future_board in enumerate(future_boards):
            mapper = NNMapper()
            node_data = mapper.to_nodes(future_board, self.color)
            ret_value = 0 #send to ai and recieve value???
            if ret_value > best_value:
                best_value=ret_value
                best_board=i


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

    def get_future_boards(self, moves_options, board):
        possible_boards = []
        for possible_moves in moves_options:
            temp_board = board.get_view()
            for (src, trg) in possible_moves:
                temp_board.move(self.color, src, trg)
            possible_boards.append(temp_board.get_view())
        return possible_boards
