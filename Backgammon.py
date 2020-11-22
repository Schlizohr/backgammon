import logging
import random
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from itertools import repeat, cycle


class Checker(Enum):
    BLACK = "x"
    WHITE = "o"

    def __str__(self):
        return self.name


class Home:
    def __init__(self, lower_bound: int, upper_bound: int):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class Player(ABC):
    def __init__(self, color):
        self.color = color
        self.__set_home(color)

    def __set_home(self, color):
        if color == Checker.BLACK:
            self.home: Home = Home(1, 6)
        elif color == Checker.WHITE:
            self.home: Home = Home(19, 24)
        else:
            raise ValueError("only black and white are supported")

    @abstractmethod
    def calculate_moves(self, dices: [int], board) -> [(int, int)]:
        pass


class Field:
    def __init__(self):
        self.content: [Checker] = []

    def place(self, checker: Checker, n=1):
        self.content.extend(repeat(checker, n))

    def remove(self, n=1):
        [self.content.pop() for _ in range(n)]

    def __contains__(self, checker: Checker):
        return len(self.__getitem__(checker)) != 0

    def __getitem__(self, checker: Checker):
        return list(filter(lambda c: c.name == checker.name, self.content))


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
        self.board = {k + 1: v for k, v in enumerate([Field() for _ in range(self.__TOTAL_FIELD_COUNT)])}
        self.board[0] = Field()
        self.out = self.board[0]
        self.place_checkers(player_1)
        self.place_checkers_rev(player_2)

    def checkers_at_field(self, field_number: int):
        return self.board[field_number]

    def place_at(self, field_number: int, checker: Checker, n=1):
        self.board[field_number].place(checker, n)

    def remove_from(self, field_number: int):
        self.board[field_number].remove()

    def move(self, checker: Checker, src: int, tar: int) -> None:
        self.remove_from(src)
        if len(self.board[tar].content) == 1 and self.board[tar].content[0] != checker:
            self.place_at(0, self.board[tar].content[0])
            self.remove_from(tar)
        if tar != 0:
            self.place_at(tar, checker)

    def get_checkers_position_of(self, player: Player):
        return [pos for pos, v in list(self.board.items()) if player.color in v]

    def __getitem__(self, item: int) -> Field:
        return self.board[item]

    def __str__(self) -> str:
        board = list(self.board.values())
        out: Field = board.pop()
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


def roll_dice():
    return random.randint(1, 6)


def roll_dices():
    return roll_dice(), roll_dice()


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
        self.play()

    def play(self):
        while True:
            current_player: Player = next(self.players)
            self.current_dice = roll_dices()
            moves = []
            # while not moves_are_valid(current_player, moves, self):
            #     moves = current_player.calculate_moves(self.current_dice, self.board)

            moves = current_player.calculate_moves(deepcopy(self.current_dice), deepcopy(self.board))
            moves_are_valid(current_player, moves, self)
            for src, tar in moves:
                self.board.move(current_player.color, src, tar)


# move list of moves [(from,to),(from,to)]. len of list 0 <= n <= 4
def moves_are_valid(player: Player, moves: [(int, int)], game: Game):
    dice = list(game.current_dice)
    out = game.board[0][player.color]
    for src, target in moves:
        logging.debug(f"verify move: from {src} to {target}")

        # check out
        if len(out) != 0:
            if src != 0:
                logging.debug("checker in out and move does not place it into game")
                return False
            out.pop()
        logging.debug(f"out is okay")

        dif = abs(src - target)
        if dif not in dice:
            logging.debug(f"distance {dif} of {src},{target} dose not match with any die")
            return False
        dice.remove(dif)
        logging.debug(f"distance is present as die")

        # move in right direction
        if abs(player.home.lower_bound - target) > abs(player.home.lower_bound - src):
            logging.debug(f"wrong direction")
            return False

        local_src = game.board[src]
        if player.color not in local_src:
            logging.debug(f"src location does not contain checker for player")
            return False
        local_src.remove()
        logging.debug(f"player moves its checker")

        # player can only move checker to to positions with 1 or less checkers present or one then he already owns
        target_field = game.board[target]
        if len(target_field.content) > 1 and player.color not in target_field:
            logging.debug(f"target location {target_field.content} is not available")
            return False
        logging.debug(f"target location is available")

        if target == 0:
            pos = game.board.get_checkers_position_of(player)
            in_base = player.home.lower_bound <= min(pos) <= max(pos) <= player.home.upper_bound
            if not in_base:
                logging.debug(f"not all checkers in base")
                return False
            logging.debug(f"can remove checker from game")
        else:
            target_field.place(player.color)
        logging.debug(f"move is okay")

    return True
