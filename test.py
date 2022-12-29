import os
cur_user = os.getlogin()
cron_file = f'/var/spool/cron/crontabs/{cur_user}'

with open(cron_file, "r") as fp:
    lines = fp.readlines()

with open(cron_file, "w") as fp:
    for line in lines:
        if line.strip("\n") != "00 03 * * * bash music.sh":
            fp.write(line)
with open(cron_file, "r") as fp:
    lines = fp.readlines()

with open(cron_file, "w") as fp:
    for line in lines:
        if line.strip("\n") != "00 03 * * * bash music.sh1":
            fp.write(line)

