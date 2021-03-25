import itertools
import json

from Backgammon import Board, Field, Checker


class TrainingsData:

    def __init__(self, board: [float], winner: int):
        """
        :param board: At the bginning for each field in board 8 vales. first 4 for white second 4 for black.
                    The first one is set to 1 if at least on checker is on this field. second is set if at least 2 checkers are present
                    the third for three checkers and the 4 is count/ of checkers if more then 3.

                    Then the which players move it is currently.
                    Then the number of checkers on the bar for both players
                    finally the number of checkers each player has already removed form the board.
        :param winner: who wins the game. 1 if white wins 0 if black wins
        :type int
        """
        self.board: [int] = board
        self.winner: int = winner


class NNMapper:
    @staticmethod
    def json_to_trainings_data(s: str):
        data = json.loads(s)
        return TrainingsData(data["board"], data["winner"])

    def to_trainings_data(self, board: Board, next_player: Checker, winner: Checker) -> TrainingsData:
        return TrainingsData(self.to_nodes(board, next_player), self.winner(winner))

    def to_nodes(self, board: Board, next_player: Checker) -> []:
        node_values = []
        for i in range(1, len(board.board)):
            node_values.extend(self.field_to_nodes(board.board[i]))
        node_values.extend(self.players(next_player))
        node_values.extend(self.checkers_on_bar(board))
        node_values.extend(self.removed_checkers(board))

        return list(itertools.chain(*node_values))

    def field_to_nodes(self, field: Field) -> [[], []]:
        content = field.content
        if len(content) == 0:
            return [[0, 0, 0, 0], [0, 0, 0, 0]]
        if content[0] == Checker.WHITE:
            return [self.content_to_nodes(content), [0, 0, 0, 0]]
        if content[0] == Checker.BLACK:
            return [[0, 0, 0, 0], self.content_to_nodes(content)]

    @staticmethod
    def content_to_nodes(content: [Checker]) -> []:
        node_values = [0, 0, 0, 0]

        if len(content) >= 1:
            node_values[0] = 1
        if len(content) >= 2:
            node_values[1] = 1
        if len(content) >= 3:
            node_values[2] = 1
        if len(content) >= 4:
            node_values[3] = (len(content) - 3) / 2

        return node_values

    def removed_checkers(self, board: Board) -> [[], []]:
        return [
            [self.removed_checkers_for_color(board, Checker.WHITE)],
            [self.removed_checkers_for_color(board, Checker.BLACK)]
        ]

    @staticmethod
    def removed_checkers_for_color(board: Board, color) -> int:
        count = 0
        for i in board.get_checkers_position_of(color=color):
            count += len(board.checkers_at_field(i).content)
        return 15 - count

    @staticmethod
    def players(checker: Checker) -> [[], []]:
        if checker == Checker.WHITE:
            return [[1], [0]]
        return [[0], [1]]

    @staticmethod
    def winner(checker: Checker) -> [[], []]:
        winner = 0
        if checker == Checker.WHITE:
            winner = 1
        return winner

    @staticmethod
    def checkers_on_bar(board: Board) -> [[], []]:
        out = board.out
        total_count = len(out)
        white_count = len([x for x in out if x == Checker.WHITE])
        return [[white_count / 2], [(total_count - white_count) / 2]]
