# ( 81-90 / 2222 records ) done
import glob
import os
import re
from datetime import datetime

directory = "../protocol/gamefiles/"


def openProtocolFile(filename, count=0):
    print("filename: " + filename)
    protocol_file = open(filename, "r", encoding="utf8", errors='replace')
    # print("countt:"+str(count))
    readProtocol(protocol_file, count)
    protocol_file.close()


def writeFile(lines_per_file, nr=0):
    file_name = str(nr) + "-splitprot-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(len(lines_per_file))
    file_name = file_name + ".txt"
    if "drop" not in lines_per_file.lower():
        # protocol_file = open("../protocol/gamefiles/splitted/drops/" + file_name, "w")
        return
    elif "cannot move" in lines_per_file.lower() or "/off" in lines_per_file.lower() or "bar/" in lines_per_file.lower():
        # protocol_file = open("../protocol/gamefiles/splitted/wrongformat/" + file_name, "w")
        return
    elif countnonoverlappingrematches("\(\d\)", lines_per_file) > 0:
        return
    else:
        protocol_file = open("../protocol/gamefiles/splitted/" + file_name, "w", encoding="utf8")
    protocol_file.write(lines_per_file)
    protocol_file.close()


def countnonoverlappingrematches(pattern, thestring):
    return re.subn(pattern, '', thestring)[1]


def readProtocol(protocol_file, countfile=0):
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
                # print("countfile:"+str(countfile)+" count:"+str(count))
                writeFile(linesperfile, int(str(countfile) + str(count)))
                linesperfile = ""

        linesperfile = linesperfile + line

    # last block
    writeFile(linesperfile, int(str(countfile) + str(count)))


def delete_old_files(path):
    files = glob.glob(path)
    for f in files:
        os.remove(f)


if __name__ == '__main__':
    delete_old_files('../protocol/gamefiles/splitted/drops/*.txt')
    delete_old_files('../protocol/gamefiles/splitted/*.txt')
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".mat") or filename.endswith(".txt"):
            # print(os.path.join(directory, filename))
            openProtocolFile(os.path.join(directory, filename), count)
            count += 1
            continue
        else:
            count += 1
            continue
