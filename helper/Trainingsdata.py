import glob
import json
import os
from datetime import datetime

from tqdm.auto import tqdm

from Protocol import Protocol
from Simulation import Simulation
from helper.Encoder import MyEncoder
from mapper import NNMapper, TrainingsData


def delete_old_files(path):
    files = glob.glob(path)
    for f in files:
        os.remove(f)


def dump_trainingsdata(trainingsdata: [TrainingsData], nr: int = 0):
    filename = str(nr) + "-trainingsdata-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
    protocol_file = open("../protocol/trainingsboards/" + filename, "w")
    json.dump(MyEncoder().encode(trainingsdata), protocol_file)
    protocol_file.close()


def create_trainings_data():
    count = 0
    player1 = 0
    player2 = 0
    directory = "../protocol/gamefiles/splitted/"
    for filename in tqdm(os.listdir(directory)):
        if filename.endswith(".mat") or filename.endswith(".txt"):
            # print(os.path.join(directory, filename))
            path = os.path.join("gamefiles/splitted/", filename)
            # prot = Protocol(HumanPlayer(Checker.WHITE), HumanPlayer(Checker.BLACK), path, 'r')
            prot = Protocol(path, 'r')
            # print(filename + " -> " + prot.whowon())

            sim = Simulation()
            mapper = NNMapper()
            status = []
            try:
                status = sim.runSimulation(prot, False)
                trainingsdata = []
                for (t_board, t_next_play, t_winner) in status:
                    trainingsdata.append(mapper.to_trainings_data(t_board, t_next_play, t_winner))
                dump_trainingsdata(trainingsdata, count)
                count += 1
            except:
                os.rename(os.path.join(directory, filename), os.path.join(directory + "broken/", filename))

            if prot.whowonNumber() == 1:
                player1 += 1
            else:
                player2 += 1
            prot = None

        else:
            continue

    print("Player1: " + str(player1) + "Player2: " + str(player2))
    print("Player1 won " + str((player1 / (player1 + player2)) * 100) + "%!")


if __name__ == '__main__':
    delete_old_files("../protocol/trainingsboards/*.txt")
    create_trainings_data()
