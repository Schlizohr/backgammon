import random
from copy import deepcopy
from enum import Enum
from itertools import repeat, cycle

from Player import Player


class Checker(Enum):
    BLACK = "x"
    WHITE = "o"

    def __str__(self):
        return self.name


class Field:
    def __init__(self):
        self.content = []

    def place(self, checker: Checker, n=1):
        self.content.extend(repeat(checker, n))

    def remove(self, n=1):
        [self.content.pop() for _ in range(n)]


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
        return [pos for pos, v in list(self.board.values()) if v.occupied_by() == player.color]

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
        self.player_1 = player_1
        self.player_2 = player_2
        self.players = [player_1, player_2]
        random.shuffle(self.players)
        self.players = cycle(self.players)
        self.board = Board(player_1, player_2)

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

            for src, tar in moves:
                self.board.move(current_player.color, src, tar)


# move list of moves [(from,to),(from,to)]. len of list 0 <= n <= 4
def moves_are_valid(player: Player, moves: [(int, int)], game: Game):
    dice = list(game.current_dice)
    local_board = deepcopy(game.board)
    for src, target in moves:
        if len(game.board[0]) != 0 and src != 0:
            return False
        dif = abs(src - target)
        if dif not in dice:
            return False
        dice.remove(dif)
        local_src = local_board[src]
        if player.color not in local_src:
            return False
        target_field = local_board[target]
        if len(target_field) > 1 and player.color != target_field[0]:
            return False

        # todo don't leave if not all in last quarter
        local_src.remove(player.color)
        target_field.append(player.color)

    return True
