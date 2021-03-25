from copy import deepcopy

from Backgammon import Checker, Game
from Player import RandomPlayer
from Protocol import Protocol


class Simulation:
    def __init__(self):
        self.player1 = RandomPlayer(Checker.WHITE)
        self.player2 = RandomPlayer(Checker.BLACK)
        self.game = Game(self.player1, self.player2, create_protocol=False)

    def run(self):
        self.game.run()

    def runSimulation(self, game_proto: Protocol, log=False):
        status = []
        if game_proto.whowonNumber() == 1:
            winner = self.player1.color
        else:
            winner = self.player2.color

        for i, turn in enumerate(game_proto.game_proto):
            if i % 2 == 0:
                player = self.player1
                next_player = self.player2
            else:
                player = self.player2
                next_player = self.player2
            for move in turn.moves:

                if i % 2 == 0:
                    if log:
                        print(
                            "Player:" + str(player.color) + " Dice:" + str(turn.die) + " Src: " + str(
                                move.src) + " Trg:" + str(
                                move.trg))
                    self.game.board.move(player.color, int(move.src), int(move.trg))
                else:
                    if log:
                        print(
                            "Player:" + str(player.color) + " Dice:" + str(turn.die) + " Src: " + str(
                                (25 - int(move.src)) % 25) + " Trg:" + str(
                                (25 - int(move.trg)) % 25))
                    self.game.board.move(player.color, (25 - int(move.src)) % 25, (25 - int(move.trg)) % 25)

            status.append((self.game.board.get_view(), deepcopy(next_player.color), deepcopy(winner)))
            if log:
                print(self.game.board)
        return status
