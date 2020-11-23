from __future__ import annotations

from copy import deepcopy
from itertools import repeat
from typing import TYPE_CHECKING

from move_verifier import can_move, moves_are_valid

if TYPE_CHECKING:
    from Backgammon import Board, Player, Die


def __possible_move_options_permutations(player: Player, die: Die) -> [[int]]:
    move_option = list(die.get_roll())
    if player.home.out_bound == 1:
        move_option = [-1 * move_option[0], -1 * move_option[1]]

    if die.is_double():
        return [list(repeat(move_option[0], 4))]
    return [move_option, [move_option[1], move_option[0]]]


def __calculate_possible_moves(player, move_options: [int], board: Board) -> [[(int, int)]]:
    travel_distance = move_options.pop()
    possible_moves: [[(int, int)]] = []
    for location in board.get_checkers_position_of(player):
        target = location + travel_distance
        if player.home.out_bound == 1 and location == 0:
            target = 25 + travel_distance
        if can_move(player, location, target, board):
            move: [(int, int)] = [(location, target)]
            moves: [[(int, int)]] = [move]
            temp_board = deepcopy(board)
            temp_board.move(player.color, location, target)
            if len(move_options) != 0:
                child_moves: [[(int, int)]] = __calculate_possible_moves(player, deepcopy(move_options), temp_board)
                for child_move in child_moves:
                    moves.append(move + child_move)
            possible_moves.extend(moves)
    return possible_moves


def keep_max_moves_only(possible_moves) -> [[(int, int)]]:
    max_len = len(max(possible_moves, key=len))
    return list(filter(lambda pm: len(pm) == max_len, possible_moves))


def remove_invalid_moves(possible_moves, player: Player, die: Die, board: Board) -> [[(int, int)]]:
    possible_moves = keep_max_moves_only(possible_moves)
    possible_moves = list(filter(lambda m: moves_are_valid(player, m, die, deepcopy(board)), possible_moves))
    return possible_moves


def generate_moves(player: Player, die: Die, board: Board) -> [[(int, int)]]:
    move_options: [[int]] = __possible_move_options_permutations(player, die)
    possible_moves: [[(int, int)]] = []
    for move_option in move_options:
        possible_moves.extend(__calculate_possible_moves(player, deepcopy(move_option), board))

    possible_moves = remove_invalid_moves(possible_moves, player, die, board)
    return possible_moves
