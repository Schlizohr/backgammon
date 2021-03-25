import logging
import os

from Backgammon import Checker
from Player import HumanPlayer
from Protocol import Protocol

if __name__ == '__main__':
    player1 = 0
    player2 = 0
    directory = "../protocol/gamefiles/splitted/"
    for filename in os.listdir(directory):
        if filename.endswith(".mat") or filename.endswith(".txt"):
            # print(os.path.join(directory, filename))
            path = os.path.join("gamefiles/splitted/", filename)
            prot = Protocol(HumanPlayer(Checker.WHITE), HumanPlayer(Checker.BLACK), path, 'r')
            print(filename + " -> " + prot.whowon())
            if prot.whowonNumber() == 1:
                player1 += 1
            else:
                player2 += 1

            prot = None
        else:
            continue
    print("Player1: " + str(player1) + "Player2: " + str(player2))
    print("Player1 won "+str((player1/(player1+player2))*100)+"%!")
