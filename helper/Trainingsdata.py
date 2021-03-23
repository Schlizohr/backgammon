import logging
import os

from Backgammon import Checker
from Player import HumanPlayer
from Protocol import Protocol

if __name__ == '__main__':
    directory = "../protocol/gamefiles/splitted/"
    for filename in os.listdir(directory):
        if filename.endswith(".mat") or filename.endswith(".txt"):
            # print(os.path.join(directory, filename))
            path = os.path.join("gamefiles/splitted/", filename)
            prot = Protocol(HumanPlayer(Checker.WHITE), HumanPlayer(Checker.BLACK), path, 'r')
            print(filename+" -> "+prot.whowon())
            prot = None
        else:
            continue