from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Backgammon import Die

protocol_logger = logging.getLogger("Protocol")


class Protocol:
    player1 = None
    player2 = None
    protocol_file = None
    protocol_filename = None
    turn_number = 1
    one_player_turn = None

    game_proto = []

    # def __init__(self, player1, player2, filename=None, mode='w'):
    def __init__(self, filename=None, mode='w'):
        if mode == 'r' and filename is None:
            protocol_logger.debug("r is given but no filename !")
            return
        # self.player1 = player1
        # self.player2 = player2

        # if something doesnt work with protocol it could be with the following 4 lines
        self.protocol_file = None
        self.protocol_filename = None
        self.turn_number = 1
        self.one_player_turn = None

        self.game_proto = []

        if mode == 'w':
            self.createProtocolFile(filename)
        else:
            # print("Opening: "+filename)
            self.openProtocolFile(filename)

    def createProtocolFile(self, filename):
        if filename is None:
            filename = "protocol-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
        self.protocol_filename = filename
        self.protocol_file = open("protocol/" + filename, "w")
        self.protocol_file.write(datetime.now().strftime("Protocol from: %Y/%m/%d %H:%M:%S\n\n"))
        #self.protocol_file.write(str(type(self.player1)) + " against " + str(type(self.player2)) + "\n\n")
        self.protocol_file.close()

    def openProtocolFile(self, filename):
        self.protocol_filename = filename
        try:
            self.protocol_file = open("protocol/" + filename, "r", errors='replace')
        except FileNotFoundError:
            self.protocol_file = open("../protocol/" + filename, "r", errors='replace')

        self.readProtocol()
        self.protocol_file.close()

    def readProtocol(self):
        lines = self.protocol_file.readlines()

        count = 0
        # Strips the newline character
        for line in lines:
            count += 1
            line = line.strip()
            if len(line) < 4:  # to short for further checks
                continue
            # if line[0] == ';' or not line[0].isdigit() or 'match' in line:
            #    continue
            if not (line[0].isdigit() and line[1] == ')') \
                    and not (line[0].isdigit() and line[1].isdigit() and line[2] == ')') \
                    and not (line[0].isdigit() and line[1].isdigit() and line[2].isdigit() and line[3] == ')'):
                continue
            protocol_logger.debug("Line{}: {}".format(count, line.strip()))

            # delete turn number
            # print(line)
            line = (line.split(")")[1]).strip()
            # split by space
            # example line :   63: 25/22 22/16             64: 21/15 15/11
            lineElements = line.split(" ")
            die = None
            turn = []
            moves = []
            got_dices = False
            for element in lineElements:
                if ":" in element:
                    if len(moves) != 0 or got_dices:
                        tempturn = Turn(die, moves)
                        self.game_proto.append(tempturn)
                        moves = []
                        die = None
                        got_dices = False
                    element = element.replace(":", "").strip()
                    die = Die(element[0], element[1])
                    got_dices = True
                elif "/" in element:
                    # print(str(element.split("/")[0]))
                    src = int(((element.split("/"))[0]).replace('*', '').strip())
                    trg = int(((element.split("/"))[1]).replace('*', '').strip())
                    moves.append(Move(src, trg))

            if len(moves) != 0 or got_dices:
                self.game_proto.append(Turn(die, moves))

    def printGameProto(self):
        for turn in self.game_proto:
            print(str(turn) + "\n")

    def whowon(self):
        return "Player: " + str(((len(self.game_proto) + 1) % 2) + 1) + " won! ->" + str(len(self.game_proto))

    def whowonNumber(self):
        return ((len(self.game_proto) + 1) % 2) + 1

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
    moves = []

    def __init__(self, die, moves):
        self.die = die
        self.moves = moves

    def __str__(self):
        retString = "Die: " + str(self.die)
        for move in self.moves:
            retString = retString + " " + str(move)
        return retString


class Move:
    src = None
    trg = None

    def __init__(self, src: int, trg: int):
        # print("Src: "+str(src)+" Trg: "+str(trg))
        if src == 25:
            src = 0
        if trg == 25:
            trg = 0
        if 0 <= src <= 24 and 0 <= trg <= 24:
            self.src = src
            self.trg = trg
        else:
            protocol_logger.debug("Input file contains move thats not valid: " + str(src) + "->" + str(trg))

    def __str__(self):
        return str(self.src) + "/" + str(self.trg)


class Die:

    def __init__(self, first=None, second=None):
        self.first: int = first
        self.second: int = second

    def __str__(self):
        return f"{self.first}, {self.second}"
