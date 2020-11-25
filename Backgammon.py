import logging
import random
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from itertools import repeat, cycle

from move_verifier import moves_are_valid


class Checker(Enum):
    BLACK = "x"
    WHITE = "o"

    def __str__(self):
        return self.name


class Home:
    def __init__(self, in_bound: int, out_bound: int):
        self.in_bound = in_bound
        self.out_bound = out_bound

    def get_lower(self):
        return min(self.in_bound, self.out_bound)

    def get_higher(self):
        return max(self.in_bound, self.out_bound)

    def in_home(self, n: int):
        return self.get_lower() <= n <= self.get_higher()


class Player(ABC):
    logging = logging.getLogger(__name__)

    def __init__(self, color):

        self.color = color
        self.__set_home(color)

    def __set_home(self, color):
        if color == Checker.BLACK:
            self.home: Home = Home(19, 24)
        elif color == Checker.WHITE:
            self.home: Home = Home(6, 1)
        else:
            raise ValueError("only black and white are supported")

    @abstractmethod
    def calculate_moves(self, dices: [int], board) -> [(int, int)]:
        pass

    def winner(self, points=1):
        logging.info(f"{self.color.name} WINNER: {points}")

    def loser(self, points=1):
        logging.info(f"{self.color.name} LOSER: {points}")

    def invalid_move(self):
        pass

    def reward(self, points):
        if points > 0:
            self.winner(points)
        else:
            self.loser(points)


class Field:
    def __init__(self):
        self.content: [Checker] = []

    def place(self, checker: Checker, n=1):
        self.content.extend(repeat(checker, n))

    def remove(self, n=1):
        [self.content.pop() for _ in range(n)]

    def __len__(self):
        return len(self.content)

    def __contains__(self, checker: Checker):
        return len(self.__getitem__(checker)) != 0

    def __getitem__(self, checker: Checker):
        return list(filter(lambda c: c.name == checker.name, self.content))

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.content)


class Board:
    __TOTAL_FIELD_COUNT = 24
    __LINEUP = {6: 5, 8: 3, 13: 5, 24: 2}

    def place_checkers(self, player):
        for (k, v) in self.__LINEUP.items():
            self.board[k].place(player.color, v)

    def place_checkers_rev(self, player: Player):
        for (k, v) in self.__LINEUP.items():
            self.board[self.__TOTAL_FIELD_COUNT - k + 1].place(player.color, v)

    def __init__(self, player_1: Player, player_2: Player):
        self.board = self.clear_board()
        self.clear_board()
        self.out = self.board[0]
        self.place_checkers(player_1)
        self.place_checkers_rev(player_2)

    def clear_board(self):
        return {k: v for k, v in enumerate([Field() for _ in range(self.__TOTAL_FIELD_COUNT + 1)])}

    def checkers_at_field(self, field_number: int):
        return self.board[field_number]

    def place_at(self, field_number: int, checker: Checker, n=1):
        self.board[field_number].place(checker, n)

    def remove_from(self, field_number: int):
        self.board[field_number].remove()

    def move(self, checker: Checker, src: int, tar: int) -> None:
        self.remove_from(src)
        if tar <= 0 or tar >= 24:
            return
        if len(self.board[tar].content) == 1 and self.board[tar].content[0] != checker:
            self.place_at(0, self.board[tar].content[0])
            self.remove_from(tar)
        if tar != 0:
            self.place_at(tar, checker)

    def get_checkers_position_of(self, player: Player) -> [int]:
        return [pos for pos, v in list(self.board.items()) if player.color in v]

    def __getitem__(self, item: int) -> Field:
        return self.board[item]

    def __str__(self) -> str:
        board = list(self.board.values())[1:]
        out: Field = self.board[0]
        s = "out:\t" + "\t".join(map(lambda c: c.value, out.content)) + "\n"
        for i in range(int(self.__TOTAL_FIELD_COUNT / 2)):
            s += str(i + 1) + "\t"
            if i == 5:
                s += "|\t"
        s += "\n"

        for i in range(7):
            for k, f in enumerate(board[:int(len(board) / 2)]):
                if len(f.content) > i:
                    s += str(f.content[i].value)
                s += "\t"
                if k == 5:
                    s += "|\t"

            s += "\n"

        for i in range(self.__TOTAL_FIELD_COUNT * 2 + 2):
            s += "="
        s += "\n"
        for i in range(int(self.__TOTAL_FIELD_COUNT / 2)):
            s += str(self.__TOTAL_FIELD_COUNT - i) + "\t"
            if i == 5:
                s += "|\t"
        s += "\n"

        for i in range(7):
            for k, f in enumerate(board[int(self.__TOTAL_FIELD_COUNT / 2):][::-1]):
                if len(f.content) > i:
                    s += str(f.content[i].value)
                s += "\t"
                if k == 5:
                    s += "|\t"
            s += "\n"
        return s


class Die:

    def __init__(self, first=None, second=None):
        self.first: int = first
        if first is None:
            self.first = random.randint(1, 6)
        self.second: int = second
        if second is None:
            self.second = random.randint(1, 6)

    def is_double(self):
        return self.first == self.second

    def get_roll(self) -> (int, int):
        return self.first, self.second

    def get_move_options(self) -> [int]:
        if self.is_double():
            return repeat(self.first, 4)
        else:
            return [self.first, self.second]


class Game:
    current_dice = None

    def __init__(self, player_1, player_2):
        self.player_1: Player = player_1
        self.player_2: Player = player_2
        self.players: [Player] = [player_1, player_2]
        random.shuffle(self.players)
        self.players = cycle(self.players)
        self.board: Board = Board(player_1, player_2)

    def run(self):
        while True:
            current_player: Player = next(self.players)
            self.current_dice: Die = Die()
            self.play(current_player)
            if len(self.board.get_checkers_position_of(current_player)) == 0:
                loser = next(self.players)
                points = self.calculate_points(current_player, loser)
                current_player.reward(points)
                loser.reward(-1 * points)
                return None

    def play(self, current_player: Player):
        moves = current_player.calculate_moves(deepcopy(self.current_dice.get_roll()), deepcopy(self.board))
        while not moves_are_valid(current_player, moves, self.current_dice, deepcopy(self.board)):
            current_player.invalid_move()
            moves = current_player.calculate_moves(deepcopy(self.current_dice.get_roll()), deepcopy(self.board))

        for src, tar in moves:
            self.board.move(current_player.color, src, tar)

    def calculate_points(self, current_player, loser):
        loser_pos = self.board.get_checkers_position_of(loser)
        remaining_checkers = sum(map(lambda p: len(self.board[p]), loser_pos))
        points = 1
        if remaining_checkers == 15:
            points = 2
            if current_player.home.in_home(max(loser_pos)):
                points = 3
            if loser.color in self.board.out:
                points = 4
        return points
