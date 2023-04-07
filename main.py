import time
from datetime import datetime, timedelta

# disable default TTY login prompt for not grabbing stdio
# $ sudo systemctl disable getty@tty1.service

TIMES_DIR = "/home/pi/times/"

def cleanUpFile(f, lines):
    f.seek(0)
    f.writelines(lines)
    f.truncate()

def readLastLine(userId):
    try:
        with open(TIMES_DIR + datetime.now().strftime("%Y-%m") + "-" + userId + ".tk", "r+") as f:
            lines = [line for line in f if line.startswith(("S", "E"))]
            cleanUpFile(f, lines)
            return lines[-1]
    except FileNotFoundError as e:
        print(f"File not found for user: {userId}\n\tFileNotFoundError in updateTime(): {e}")
    except IndexError as e:
        print(f"File empty for user: {userId}\n\tIndexError in updateTime(): {e}")

def calcSumOfTrackedDaysAndMinutes(userId):
    daysTracked = set([])
    sumOfMinutesTracked = 0
    lastMonth = (datetime.today().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    try:
        with open(TIMES_DIR + lastMonth + "-" + userId + ".tk", "r") as f:
            lines = f.read().splitlines()

            for line in lines:
                if(len(line.split('|')) > 3):
                    daysTracked.add(line.split('|')[1])
                    if(line.split('|')[3].isnumeric()):
                        sumOfMinutesTracked += int(line.split('|')[3])

        with open(TIMES_DIR + lastMonth + "-" + userId + ".tk", "a+") as f:
            f.write(f"SUM_DAYS|{len(daysTracked)}\nSUM_MINUTES|{sumOfMinutesTracked}\n")
    except FileNotFoundError as e:
        print(f"File not found for user: {userId}\n\tFileNotFoundError in calcSumOfTrackedDaysAndMinutes(): {e}")

def updateTime(userId):
    lastLine = readLastLine(userId)

    if not lastLine:
        calcSumOfTrackedDaysAndMinutes(userId)

    lastDate = datetime.now() if not lastLine else datetime.strptime(' '.join(lastLine.split('|')[1:3]).rstrip(), '%Y-%m-%d %H:%M:%S')

    with open(TIMES_DIR + datetime.now().strftime("%Y-%m") + "-" + userId + ".tk", "a+") as f:
        if not lastLine or lastLine[0] == 'E':
            if lastDate.date() == datetime.now().date():
                if (datetime.now() - lastDate).seconds > 3600:
                    f.write("S|{0}|W\n".format(
                        (lastDate + timedelta(minutes=60)).strftime("%Y-%m-%d|%H:%M:%S")))
                    f.write("E|{0}|{1}\n".format(datetime.now().strftime("%Y-%m-%d|%H:%M:%S"), int(
                        (datetime.now() - (lastDate + timedelta(minutes=60))).seconds / 60)))
                else:
                    f.write("S|{0}\n".format(
                        datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
            else:
                f.write("S|{0}\n".format(
                    datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
        else:
            if lastDate.date() != datetime.now().date():
                f.write("E|{0}|{1}|W\n".format(
                    (lastDate + timedelta(minutes=10)).strftime("%Y-%m-%d|%H:%M:%S"), 10))
                f.write("S|{0}\n".format(
                    datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
            else:
                f.write("E|{0}|{1}\n".format(datetime.now().strftime(
                    "%Y-%m-%d|%H:%M:%S"), int((datetime.now() - lastDate).seconds / 60)))

def test():
    global TIMES_DIR
    TIMES_DIR = "/tmp/"

    while True:
        updateTime("1337")
        time.sleep(3)

def main():
    fp = open('/dev/tty0', 'rb')

    while True:
        userId = fp.readline().rstrip().decode('UTF-8')
        updateTime(userId)
        time.sleep(1)


if __name__ == "__main__":
    test()
