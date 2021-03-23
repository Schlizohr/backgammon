# ( 61-70 / 2222 records ) done
import os
from datetime import datetime

directory = "../protocol/gamefiles/"


def openProtocolFile(filename,count =0):
    protocol_file = open(filename, "r")
    #print("countt:"+str(count))
    readProtocol(protocol_file,count)
    protocol_file.close()


def writeFile(lines_per_file, nr=0):
    file_name = str(nr)+"-splitprot-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(len(lines_per_file))
    file_name = file_name + ".txt"
    protocol_file = open("../protocol/gamefiles/splitted/" + file_name, "w")
    protocol_file.write(lines_per_file)
    protocol_file.close()


def readProtocol(protocol_file,countfile=0):
    lines = protocol_file.readlines()

    linesperfile = ""

    count = 0
    # Strips the newline character
    firstgame = True
    for line in lines:
        count += 1

        if "Game" in line:
            if firstgame:
                firstgame = False
            else:
                #print("countfile:"+str(countfile)+" count:"+str(count))
                writeFile(linesperfile, int(str(countfile)+str(count)))
                linesperfile = ""

        linesperfile = linesperfile + line

    # last block
    writeFile(linesperfile, int(str(countfile)+str(count)))


if __name__ == '__main__':
    count=0
    for filename in os.listdir(directory):
        if filename.endswith(".mat") or filename.endswith(".txt"):
            # print(os.path.join(directory, filename))
            openProtocolFile(os.path.join(directory, filename),count)
            count +=1
            continue
        else:
            count += 1
            continue


