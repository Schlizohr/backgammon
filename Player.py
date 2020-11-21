from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def calculate_moves(self, dices: [int], board) -> [(int, int)]:
        pass


class HumanPlayer(Player):

    def calculate_moves(self, dices: [int], board) -> [(int, int)]:
        print(board)
        print(self.color.value, "your dices are:", dices)
        moves = []
        number_of_moves = 2
        if dices[0] == dices[1]:
            number_of_moves = 4

        for i in range(number_of_moves):
            print("input move usage: <src> <target>")
            src, tar = input().strip().split(" ")
            moves.append((int(src), int(tar)))
        return moves
