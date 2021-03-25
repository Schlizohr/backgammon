import logging
import random
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from itertools import repeat, cycle

import jsonpickle

from Protocol import Protocol
from move_verifier import moves_are_valid


def get_logger(name, file, formatter, level, filemode="a"):
    """To setup as many loggers as you want"""
    try:
        handler = logging.FileHandler(file, mode=filemode)
    except FileNotFoundError:
        handler = logging.FileHandler('../'+file, mode=filemode)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


log_board_state = False
board_logger = get_logger("log_board_file", "log/board_state.log", logging.Formatter("%(message)s"), logging.DEBUG)


class GameStateLog():
    def __init__(self, board, die, player, moves):
        self.board = board
        self.die = die
        self.player = player
        self.moves = moves


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

    def __str__(self):
        return f"{self.first}, {self.second}"


class Player(ABC):
    player_logging = logging.getLogger(__name__)

    def __init__(self, color: Checker):

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
    def calculate_moves(self, dices: Die, board) -> [(int, int)]:
        pass

    def winner(self, points=1):
        self.player_logging.info(f"{self.color.name} WINNER: {points}")

    def loser(self, points=1):
        self.player_logging.info(f"{self.color.name} LOSER: {points}")

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

    def remove(self, checker: Checker = None):
        #print("Content:" + str(self.content) + " checker:" + str(checker))
        if checker is None:
            self.content.pop()
        else:
            self.content.remove(checker)

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
        self.out = self.board[0]
        self.place_checkers(player_1)
        self.place_checkers_rev(player_2)

    def clear_board(self):
        return {k: v for k, v in enumerate([Field() for _ in range(self.__TOTAL_FIELD_COUNT + 1)])}

    def checkers_at_field(self, field_number: int):
        return self.board[field_number]

    def place_at(self, field_number: int, checker: Checker, n=1):
        self.board[field_number].place(checker, n)

    def remove_from(self, field_number: int, checker: Checker = None):
        self.board[field_number].remove(checker)

    def move(self, checker: Checker, src: int, tar: int) -> None:
        self.remove_from(src, checker)
        if tar <= 0 or tar >= 25:
            return
        if len(self.board[tar].content) == 1 and self.board[tar].content[0] != checker:
            self.place_at(0, self.board[tar].content[0])
            self.remove_from(tar)
        if tar != 0:
            self.place_at(tar, checker)

    def get_checkers_position_of(self, player: Player = None, color=None) -> [int]:
        color = player.color if player else color
        return [pos for pos, v in list(self.board.items()) if color in v]

    def reversed_board(self):
        rev_board: Board = deepcopy(self)
        rev_dict: dict = {abs(k - 25): v for k, v in rev_board.board.items()}
        rev_dict[0] = rev_dict[25]
        del rev_dict[25]
        rev_board.board = dict(sorted(rev_dict.items()))
        return rev_board

    def get_view(self, revered=False):
        if revered:
            return self.reversed_board()
        else:
            return deepcopy(self)

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

    def __repr__(self):
        # return pprint.pformat(self.board)
        return self.__str__()


class Game:
    current_dice = None
    protocol = None

    def __init__(self, player_1, player_2, _log_board_state=False, create_protocol=True):
        global log_board_state
        log_board_state = _log_board_state
        board_logger.debug("#" * 200)
        self.player_1: Player = player_1
        self.player_2: Player = player_2
        self.players: [Player] = [player_1, player_2]
        random.shuffle(self.players)
        self.players = cycle(self.players)
        self.current_player: Player = next(self.players)
        self.board: Board = Board(player_1, player_2)
        if create_protocol:
            self.protocol = Protocol(player_1, player_2, filename=None)
        else:
            self.protocol = None

    def run(self):
        while True:
            self.current_player: Player = next(self.players)
            self.play()
            if len(self.board.get_checkers_position_of(self.current_player)) == 0:
                self.notify_player()
                return None

    def notify_player(self):
        loser = next(self.players)
        points = self.calculate_points(self.current_player, loser)
        self.current_player.reward(points)
        loser.reward(-1 * points)

    def play(self):
        self.current_dice: Die = Die()
        moves = self.players_moves()  # verify moves
        for src, tar in moves:
            self.board.move(self.current_player.color, src, tar)
        if self.protocol is not None:
            self.protocol.log_player_turn(self.current_player, self.current_dice, moves)

    def players_moves(self):
        is_player_2 = self.current_player == self.player_2
        moves = self.current_player.calculate_moves(deepcopy(self.current_dice), self.board.get_view(is_player_2))
        Game.log_board_state(GameStateLog(self.board.board, self.current_dice, self.current_player, moves))
        while not moves_are_valid(self.current_player, moves, self.current_dice, self.board.get_view(is_player_2)):
            self.current_player.invalid_move()
            moves = self.current_player.calculate_moves(
                deepcopy(self.current_dice),
                self.board.get_view(is_player_2)
            )
        if is_player_2:
            moves = [((25 - s) % 25, (25 - t) % 25) for s, t in moves]
        return moves

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

    @staticmethod
    def log_board_state(game_state: GameStateLog = None):
        global log_board_state
        if log_board_state:
            global board_logger
            s = jsonpickle.encode(game_state)
            board_logger.debug(s)
