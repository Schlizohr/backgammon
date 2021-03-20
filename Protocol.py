from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Backgammon import Board, Player, Die, Checker

protocol_logger = logging.getLogger("Protocol")


class Protocol:
    player1 = None
    player2 = None
    protocol_file = None
    protocol_filename = None
    turn_number = 1
    one_player_turn = None

    game_proto = []

    def __init__(self, player1, player2, filename=None, mode='w'):
        if mode == 'r' and filename == None:
            protocol_logger.debug("r is given but no filename !")
            return
        self.player1 = player1
        self.player2 = player2
        if mode == 'w':
            self.createProtocolFile(filename)
        else:
            self.openProtocolFile(filename)

    def createProtocolFile(self, filename):
        if filename is None:
            filename = "protocol-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
        self.protocol_filename = filename
        self.protocol_file = open("protocol/" + filename, "w")
        self.protocol_file.write(datetime.now().strftime("Protocol from: %Y/%m/%d %H:%M:%S\n\n"))
        self.protocol_file.write(str(type(self.player1)) + " against " + str(type(self.player2)) + "\n\n")
        self.protocol_file.close()

    def openProtocolFile(self, filename):
        self.protocol_filename = filename
        try:
            self.protocol_file = open("protocol/" + filename, "r")
        except FileNotFoundError:
            self.protocol_file = open("../protocol/" + filename, "r")

        self.readProtocol()
        self.protocol_file.close()

    def readProtocol(self):
        lines = self.protocol_file.readlines()

        count = 0
        # Strips the newline character
        for line in lines:
            count += 1
            line = line.strip()
            if line[0] == ';' or not line[0].isdigit():
                continue
            protocol_logger.debug("Line{}: {}".format(count, line.strip()))

            #delete turn number
            line = (line.split(")")[1]).strip()
            #split by space
            lineElements = line.split(" ")
            for element in lineElements:
                turn = []
                if ":" in element:
                    if len(turn) == 0:
                        pass


            #moves =[]
            #moves.append(Move(src,trg))
            #self.game_proto.append(Turn(die,moves))


    def log_player_turn(self, player, dices, moves):
        if self.one_player_turn is None:
            self.one_player_turn = (player, dices, moves)
        else:
            self.log_turn(player, dices, moves)
            self.one_player_turn = None

    def log_turn(self, player, dices, moves):
        self.protocol_file = open("protocol/" + self.protocol_filename, "a")
        (playerOld, dicesOld, movesOld) = self.one_player_turn
        self.protocol_file.write(
            '{0:40}  {1}'.format("  " + str(self.turn_number) + ") " + printTurn(dicesOld, movesOld),
                                 printTurn(dices, moves)) + "\n")
        self.protocol_file.close()
        self.turn_number += 1


def printTurn(dices, moves):
    return printDices(dices) + ": " + printMoves(moves)


def printDices(dices):
    return str(dices).replace(',', '').replace(' ', '')


# in die klasse rein
def printMoves(moves):
    if len(moves) == 0:
        return ""
    protocol_logger.debug("Before replace moves: " + str(moves))
    protocol_logger.debug("After replace moves: " + str(moves))

    movesStr = ""
    for (mvsrc, mvtrg) in moves:
        movesStr += str(str(mvsrc) + "/" + str(mvtrg)) + " "
    return movesStr.strip()


class Turn:
    die = None
    moveWithDie = []

    def __init__(self, die, moves):
        self.moveWithDie.append((die, moves))


class Move:
    src = None
    trg = None

    def __init__(self, src, trg):
        if src in range(0, 24) and trg in range(0, 24):
            self.src = src
            self.trg = trg
        else:
            protocol_logger.log("Input file contains move thats not valid: " + str(src) + "->" + str(trg))
