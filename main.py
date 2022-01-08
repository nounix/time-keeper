import time
from datetime import datetime, timedelta


# disable default TTY login prompt for not grabbing stdio
# $ sudo systemctl disable getty@tty1.service

TIMES_DIR = "/home/pi/times/"


def calcSumTime(user_id):
    summe = 0
    last_month = (datetime.today().replace(day=1) -
                  timedelta(days=1)).strftime("%Y-%m")

    try:
        with open(TIMES_DIR + last_month + "-" + user_id + ".tk", "r") as f:
            lines = f.read().splitlines()

            for line in lines:
                if(len(line.split('|')) > 3 and line.split('|')[3].isnumeric()):
                    summe += int(line.split('|')[3])

        with open(TIMES_DIR + last_month + "-" + user_id + ".tk", "a+") as f:
            f.write("SUM|{0}\n".format(summe))
    except Exception as e:
        print("Calc sum failed for:", user_id, "\n\tException:", e)


def update_time(user_id):
    last_line = ""
    last_date = datetime.now()

    try:
        with open(TIMES_DIR + datetime.now().strftime("%Y-%m") + "-" + user_id + ".tk", "r+") as f:
            lines = [line for line in f if line.startswith(("S", "E"))]
            f.seek(0)
            f.writelines(lines)
            f.truncate()

            last_line = lines[-1]

            last_date = datetime.strptime(
                ' '.join(last_line.split('|')[1:3]).rstrip(), '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print("Update time failed for:", user_id, "\n\tException:", e)
        calcSumTime(user_id)

    with open(TIMES_DIR + datetime.now().strftime("%Y-%m") + "-" + user_id + ".tk", "a+") as f:
        if last_line == "" or last_line[0] == 'E':
            if last_date.date() == datetime.now().date():
                if (datetime.now() - last_date).seconds > 3600:
                    f.write("S|{0}|W\n".format(
                        (last_date + timedelta(minutes=60)).strftime("%Y-%m-%d|%H:%M:%S")))
                    f.write("E|{0}|{1}\n".format(datetime.now().strftime("%Y-%m-%d|%H:%M:%S"), int(
                        (datetime.now() - (last_date + timedelta(minutes=60))).seconds / 60)))
                else:
                    f.write("S|{0}\n".format(
                        datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
            else:
                f.write("S|{0}\n".format(
                    datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
        else:
            if last_date.date() != datetime.now().date():
                f.write("E|{0}|{1}|W\n".format(
                    (last_date + timedelta(minutes=10)).strftime("%Y-%m-%d|%H:%M:%S"), 10))
                f.write("S|{0}\n".format(
                    datetime.now().strftime("%Y-%m-%d|%H:%M:%S")))
            else:
                f.write("E|{0}|{1}\n".format(datetime.now().strftime(
                    "%Y-%m-%d|%H:%M:%S"), int((datetime.now() - last_date).seconds / 60)))


def test():
    global TIMES_DIR
    TIMES_DIR = "/tmp/"

    while True:
        update_time("1337")
        time.sleep(3)


def main():
    fp = open('/dev/tty0', 'rb')

    while True:
        buffer = fp.readline().rstrip().decode('UTF-8')
        update_time(buffer)
        time.sleep(1)


if __name__ == "__main__":
    main()
