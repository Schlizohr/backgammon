from __future__ import annotations

import logging
from copy import deepcopy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Backgammon import Board, Player, Game, Die

logging = logging.getLogger(__name__)


def is_valid_target(color, target: int, board: Board) -> bool:
    if not 0 <= target <= 24:
        return True
    target_field = board[target]
    return all([c == color for c in target_field]) or len(target_field) <= 1


def has_src(color, src: int, board: Board) -> bool:
    return color in board[src]


def can_move(color, src: int, target: int, board: Board) -> bool:
    return has_src(color, src, board) and is_valid_target(color, target, board)


def moves_are_valid(player: Player, moves: [(int, int)], die: Die, board: Board):
    try:
        verify_moves(player, moves, die, board)
    except ValueError as e:
        return False
    return True


# move list of moves [(from,to),(from,to)]. len of list 0 <= n <= 4
def verify_moves(player: Player, moves: [(int, int)], die: Die, board: Board):
    dice = list(die.get_move_options())
    out = board[0][player.color]
    for src, target in moves:
        logging.debug(f"verify move: from {src} to {target}")

        # check out
        if len(out) != 0:
            if src != 0:
                logging.debug("checker in out and move does not place it into game")
                raise ValueError("checker in out and move does not place it into game")
            out.pop()
        logging.debug(f"out is okay")

        dif = abs(src - target)
        if src == 0:
            dif = 25 - target
        if dif not in dice and 0 != src and target != 0:
            logging.debug(f"distance {dif} of {src},{target} dose not match with any die")
            raise ValueError(f"distance {dif} of {src},{target} dose not match with any die")
        dice.remove(dif)
        logging.debug(f"distance is present as die")

        # move in right direction
        if abs(player.home.out_bound - target) > abs(player.home.out_bound - src) and 0 < target <= 24 and (
                player.home.out_bound != 1 and src == 0):
            logging.debug(f"wrong direction")
            raise ValueError("wrong direction")

        local_src = board[src]
        if player.color not in local_src:
            logging.debug(f"src location does not contain checker for player")
            raise ValueError("src location does not contain checker for player")

        logging.debug(f"player moves its checker")

        remove_from_game = target <= 0 or target >= 24
        # player can only move checker to to positions with 1 or less checkers present or one then he already owns
        target_field = None
        if not remove_from_game:
            target_field = board[target]
            if len(target_field.content) > 1 and player.color not in target_field:
                logging.debug(f"target location {target_field.content} is not available")
                raise ValueError(f"target location {target_field.content} is not available")
            logging.debug(f"target location is available")

        if remove_from_game:
            pos = board.get_checkers_position_of(player)
            in_base = 1 <= min(pos) <= 6 and 1 <= max(pos) <= 6
            if not in_base:
                logging.debug(f"not all checkers in base")
                raise ValueError("not all checkers in base")
            logging.debug(f"can remove checker from game")
        else:
            target_field.place(player.color)
        local_src.remove(player.color)
        logging.debug(f"move is okay")


def game_moves_are_valid(player: Player, moves: [(int, int)], game: Game):
    verify_moves(player, moves, game.current_dice, deepcopy(game.board))
