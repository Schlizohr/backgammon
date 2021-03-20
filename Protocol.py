from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Backgammon import Board, Player, Die

protocol_logger = logging.getLogger("Protocol")

class Protocol:
    player1 = None
    player2 = None
    protocol_file = None
    protocol_filename = None
    turn_number = 1
    one_player_turn = None

    def __init__(self, player1, player2, filename=None):
        self.player1 = player1
        self.player2 = player2
        self.createProtocolFile(filename)

    def createProtocolFile(self, filename):
        if filename is None:
            filename = "protocol-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
        self.protocol_filename = filename
        self.protocol_file = open("protocol/" + filename, "w")
        self.protocol_file.write(datetime.now().strftime("Protocol from: %Y/%m/%d %H:%M:%S\n\n"))
        self.protocol_file.write(str(type(self.player1)) + " against " + str(type(self.player2)) + "\n\n")
        self.protocol_file.close()

    def log_player_turn(self, player, dices, moves):
        if self.one_player_turn is None:
            self.one_player_turn = (player, dices, moves)
        else:
            self.log_turn(player, dices, moves)
            self.one_player_turn = None

    def log_turn(self, player, dices, moves):
        self.protocol_file = open("protocol/" + self.protocol_filename, "a")
        (playerOld, dicesOld, movesOld) = self.one_player_turn
        self.protocol_file.write('{0:40}  {1}'.format("  "+str(self.turn_number) + ") " + printTurn(dicesOld, movesOld), printTurn(dices, moves))+"\n")
        self.protocol_file.close()
        self.turn_number += 1


def printTurn(dices, moves):
    return printDices(dices) + ": " + printMoves(moves)


def printDices(dices):
    return str(dices).replace(',', '').replace(' ', '')

#in die klasse rein
def printMoves(moves):
    if len(moves) == 0:
        return ""
    protocol_logger.debug("Before replace moves: " + str(moves))
    protocol_logger.debug("After replace moves: "+str(moves))
    # add serial moves
    serial_moves = [moves[0]]
    for i in range(len(moves) - 1):
        (mvsrc, mvtrg) = moves[i + 1]
        added_move_to_serial = False
        for j in range(len(serial_moves)):
            (tmpmvsrc, tmpmvtrg) = serial_moves[j]
            if mvtrg == tmpmvsrc:
                serial_moves[j] = (mvsrc, tmpmvtrg)
                added_move_to_serial = True
                #print("Merged moves")
                break
            elif mvsrc == tmpmvtrg:
                serial_moves[j] = (tmpmvsrc, mvtrg)
                added_move_to_serial = True
                #print("Merged moves2")
                break
        if not added_move_to_serial:
            serial_moves.append((mvsrc, mvtrg))
            #print("Added move")

    # merge duplicate moves
    formated_moves = {}
    for (mvsrc, mvtrg) in serial_moves:
        key = str(mvsrc) + "/" + str(mvtrg)
        if key in formated_moves.keys():
            formated_moves[key] = formated_moves[key] + 1
        else:
            formated_moves[key] = 1

    movesStr = ""
    for move in formated_moves:
        if formated_moves[move] > 1:
            movesStr += str(move) + "(" + str(formated_moves[move]) + ")" + " "
        else:
            movesStr += str(move) + " "
    return movesStr.strip()

