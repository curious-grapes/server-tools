from __future__ import print_function
from sshconf import read_ssh_config
from os.path import expanduser
import os
import configparser
import sys
# VARIABLES
logo = r"""
                                                    __                 ___             
                                                   /\ \__             /\_ \            
  ____    __  _ __  __  __    __  _ __             \ \ ,_\   ___    __\//\ \     ____  
 /',__\ /'__`/\`'__/\ \/\ \ /'__`/\`'__     ______  \ \ \/  / __`\ / __`\ \ \   /',__\ 
/\__, `/\  __\ \ \/\ \ \_/ /\  __\ \ \/    /\______  \ \ \_/\ \L\ /\ \L\ \_\ \_/\__, `\
\/\____\ \____\ \_\ \ \___/\ \____\ \_\    \/______/  \ \__\ \____\ \____/\____\/\____/
 \/___/ \/____/\/_/  \/__/  \/____/\/_/                \/__/\/___/ \/___/\/____/\/___/ 
"""
print(logo)
# upgrade commands
update_command = "sudo apt-get update"
upgrade_command = "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y && sudo apt-get autoremove -y"
def_app_install_command = "sudo apt-get install htop wget curl sudo lnav -y"
# list with approved hosts
ahosts = []
# possible user input
y_ans = ['y', 'Y', 'yes', 'Yes', 'YES']
n_ans = ['n', 'N', 'no', 'No', 'NO']
args = ['install', 'debug', 'remove']
cur_user = os.getlogin()
#check for config existence and parse
config = configparser.ConfigParser()
config.sections()
if os.path.isfile(expanduser('./my.conf')) == True:
    config.read('my.conf')
else:
    print("No config found. You need to create one, look in documentation; exiting now.")
    exit()
dir = config['PATH']['install_folder']
#print(dir)
# FUNCTIONS
# check for script folder, create if there is none
def create_dir():
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
        runcom(f"sudo chmod 700 {dir}", True)
# function to execute command
def runcom(command, mute):
    exec = os.popen(command)
    out=exec.read()
    if mute == False: print(out)
    return out
# def apps install
def defapps_f():
    if config['PATH'].getboolean('install_def_app') == True:
        # check for updates
        runcom(update_command, False)
        # installing apps
        runcom(def_app_install_command, True)
# autoupdate server picking
def autoupdate_f():
    if config['AUTOUPDATE'].getboolean('auto_update') == True:
        create_dir()
        ask = str(input('Do you want to update host? (y/n) '))
        if ask in y_ans:
            selfupdate = True
        else:
            selfupdate = False
        if os.path.isfile(expanduser('~/.ssh/config')) == True:
            c = read_ssh_config(expanduser("~/.ssh/config"))
            hosts = c.hosts()
            print(f'Found {len(hosts)} hosts in ssh config file.')
            for index, item in enumerate(hosts):
                while True:
                    ask = str(input(f'Do you want to update {item}? (y/n) '))
                    if ask in n_ans:
                        break
                    elif ask in y_ans:
                        ahosts.append(item)
                        break
            #    DISABLED (why do i need add apt to run not from sudo?) -------------------------------------
            # for item in ahosts:
            #     nhost = c.host(item).get("hostname")
            #     port = c.host(item).get("port")
            #     user = c.host(item).get("user")
            #     print(item, nhost, port, user)
            #     cmd = f"""ssh {user}@{nhost} -p {port} -i ~/.ssh/server.key -t "sudo echo '{cur_user} ALL = (root) NOPASSWD: /usr/bin/apt-get' | sudo EDITOR='tee -a' visudo >> /dev/null" """
            #     print(cmd)
            #     print("enter user password:")
            #     runcom(cmd, True)
        # dummy variables to shut up generator
        user = "{user}"
        nhost = "{nhost}"
        port = "{port}" 
        #wasnt working if commented out
        #upgrade_command = "{upgrade_command}" 
        code = f"""
from __future__ import print_function
from sshconf import read_ssh_config
from os.path import expanduser
import os
# reading ssh config
c = read_ssh_config(expanduser("~/.ssh/config"))
hosts = c.hosts()
upgrade_command = {upgrade_command}
# function to execute command
def runcom(command):
    exec = os.popen(command)
    out=exec.read()
    print(out)
# replaced by script
ahosts = {ahosts}
#update all servers specified in ahosts list
for item in ahosts:
    nhost = c.host(item).get("hostname")
    port = c.host(item).get("port")
    user = c.host(item).get("user")
    print(item, nhost, port, user)
    cmd = f'ssh {user}@{nhost} -p {port} -i ~/.ssh/server.key "{upgrade_command}"'
    runcom(cmd)
    # self update
    if {selfupdate}:
        runcom(upgrade_command)"""
            # creating python script in folder
        autoupdate_file = dir + 'autoupdate.py'
        with open(autoupdate_file, 'w') as f:
            f.write(code)
        runcom(f"sudo chmod +x {autoupdate_file}", True)
        runcom("""crontab -l | { cat; echo "00 03 * * * python3 %s"; } | crontab -""" % (autoupdate_file), True)
# music downloader
def musicdownloader_f():
    if config['MUSIC_DOWNLOADER'].getboolean('yt_download') == True:
        create_dir()
        if os.path.isfile(expanduser('/usr/bin/youtube-dl')) == False:
            runcom('sudo apt-get install youtube-dl -y', False)
        songs_folder = config['MUSIC_DOWNLOADER']['songs_folder']
        yt_playlist = config['MUSIC_DOWNLOADER']['yt_playlist']
        today = u'сьогодні'
        code = f"""wget {yt_playlist}
    if [[ $(cat playlist*  | grep {today}) = *{today}* ]]; then
    echo "is"
    youtube-dl -x --audio-format mp3 -w --download-archive {songs_folder}list.txt -o "{songs_folder}%(title)s.%(ext)s" {yt_playlist}
    else
    echo "Not"
    fi
    rm -rf playlist*
        """
        # creating python script in folder
        music_file = dir + 'music.sh'
        with open(music_file, 'w') as f:
            f.write(code)
        runcom(f"sudo chmod +x {music_file}", True)
        runcom("""crontab -l | { cat; echo "00 03 * * * bash %s"; } | crontab -""" % (music_file), True)
        ask = str(input('Do you want to download music now? (y/n) '))
        if ask in y_ans:
            runcom('bash ' + music_file, False)
# remove folder made by script
def remove_f():
    if os.path.isdir(dir) == True:
        import shutil
        shutil.rmtree(dir)
        print('Removed directory')
# remove crontab entries
def remove_cron():
    import subprocess
    # Define the lines to remove from the crontab file
    music_file = dir + 'music.sh'
    autoupdate_file = dir + 'autoupdate.py'
    lines_to_remove = [f"00 03 * * * bash {music_file}", f"00 03 * * * python3 {autoupdate_file}"]
    # Get the current crontab configuration
    current_crontab = subprocess.check_output(["crontab", "-l"]).decode("utf-8")
    # Split the crontab configuration into a list of lines
    crontab_lines = current_crontab.split("\n")
    # Remove all instances of the lines to delete from the list
    i = 0
    while i < len(crontab_lines):
        if crontab_lines[i] in lines_to_remove:
            crontab_lines.pop(i)
        else:
            i += 1
    # Join the list back into a single string with each line separated by a newline character
    updated_crontab = "\n".join(crontab_lines)
    # Write the updated crontab configuration to a temporary file
    with open('/tmp/crontab.tmp', 'w') as f:
        f.write(updated_crontab)
    # Update the crontab configuration with the contents of the temporary file
    subprocess.run(["crontab", "/tmp/crontab.tmp"])
    print('Removed cron jobs')
# argument processing
if len(sys.argv) == 2:
    option = str(sys.argv[1])
    if option in args:
        if option == 'install':
            print('installing...')
            defapps_f()
            autoupdate_f()
            musicdownloader_f()
        elif option == 'debug':
            print('debugging...')
        elif option == 'remove':
            print('removing...')
            remove_cron()
            remove_f()
    else:
        print('Command not found')
else:
    print('Argument expected')
