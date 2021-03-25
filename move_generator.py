from __future__ import annotations

import multiprocessing
import time
from copy import deepcopy
from itertools import repeat
from typing import TYPE_CHECKING

from joblib import Parallel, delayed

from move_verifier import can_move, moves_are_valid

if TYPE_CHECKING:
    from Backgammon import Board, Player, Die

num_cores = multiprocessing.cpu_count()


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def __possible_move_options_permutations(die: Die) -> [[int]]:
    move_option = list(die.get_roll())

    if die.is_double():
        return [list(repeat(move_option[0], 4))]
    return [move_option, [move_option[1], move_option[0]]]


def __calculate_possible_moves(color, move_options: [int], board: Board) -> [[(int, int)]]:
    travel_distance = move_options.pop()
    possible_moves: [[(int, int)]] = []
    for location in board.get_checkers_position_of(color=color):
        target = location - travel_distance
        if location == 0:
            target = 25 - travel_distance
        if can_move(color, location, target, board):
            move: [(int, int)] = [(location, target)]
            moves: [[(int, int)]] = [move]
            temp_board = deepcopy(board)
            temp_board.move(color, location, target)
            if len(move_options) != 0:
                # possible_moves.extend(moves[:])
                child_moves: [[(int, int)]] = __calculate_possible_moves(color, deepcopy(move_options), temp_board)
                for child_move in child_moves:
                    moves.append(move + child_move)
            possible_moves.extend(moves)
    return possible_moves


def keep_max_moves_only(possible_moves) -> [[(int, int)]]:
    max_len = len(max(possible_moves, key=len))
    return list(filter(lambda pm: len(pm) == max_len, possible_moves))


def remove_invalid_moves(possible_moves, player: Player, die: Die, board: Board) -> [[(int, int)]]:
    possible_moves = list(filter(lambda m: moves_are_valid(player, m, die, deepcopy(board)), possible_moves))
    possible_moves = keep_max_moves_only(possible_moves)
    return possible_moves


@timeit
def generate_moves_serial(player: Player, die: Die, board: Board) -> [[(int, int)]]:
    move_options: [[int]] = __possible_move_options_permutations(die)
    possible_moves: [[(int, int)]] = []
    for move_option in move_options:
        possible_moves.extend(__calculate_possible_moves(player.color, deepcopy(move_option), board))

    possible_moves = remove_invalid_moves(possible_moves, player, die, board)
    return possible_moves


@timeit
def generate_moves(player: Player, die: Die, board: Board) -> [[(int, int)]]:
    print(type(player))
    move_options: [[int]] = __possible_move_options_permutations(die)
    possible_moves = __calculate_possible_moves_parallel(board, move_options, player)
    possible_moves = remove_invalid_moves(possible_moves, player, die, board)
    return possible_moves


def __calculate_possible_moves_parallel(board, move_options, player: Player):
    print(type(player))
    moves_per_job = Parallel(n_jobs=num_cores)(
        delayed(__calculate_possible_moves)(player.color, deepcopy(move_option), board) for move_option in move_options)
    moves = []
    for move in moves_per_job:
        moves.extend(move)
    return moves
