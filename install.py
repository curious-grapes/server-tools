from __future__ import print_function
from sshconf import read_ssh_config
from os.path import expanduser
import os
import configparser
import sys
# VARIABLES
# upgrade commands
update_command = "sudo apt-get update"
upgrade_command = "sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y && sudo apt-get autoremove -y"
def_app_install_command = "sudo apt-get install glances wget curl sudo lnav -y"
# list with approved hosts
ahosts = []
# possible user input
y_ans = ['y', 'Y', 'yes', 'Yes', 'YES']
n_ans = ['n', 'N', 'no', 'No', 'NO']
args = ['install', 'verify', 'debug', 'remove']
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
print(dir)
# FUNCTIONS
# check for script folder, create if there is none
def create_dir():
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
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
        runcom(update_command, True)
        # installing apps
        runcom(def_app_install_command, False)
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
            for item in ahosts:
                nhost = c.host(item).get("hostname")
                port = c.host(item).get("port")
                user = c.host(item).get("user")
                print(item, nhost, port, user)
                cmd = f"""ssh {user}@{nhost} -p {port} -i ~/.ssh/server.key -t "sudo echo '{cur_user} ALL = (root) NOPASSWD: /usr/bin/apt-get' | sudo EDITOR='tee -a' visudo >> /dev/null" """
                print(cmd)
                print("enter user password:")
                runcom(cmd, True)
        # dummy variables to shut up generator
        user = "{user}"
        nhost = "{nhost}"
        port = "{port}"
        upgrade_command = "{upgrade_command}"
        code = f"""from __future__ import print_function
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
            runcom('sudo apt-get-get install youtube-dl -y', False)
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
# torrent mover
def torrentmover_f():
    if config['TORRENT_MOVER'].getboolean('torrent_mover') == True:
        create_dir()
        if os.path.isdir(config['TORRENT_MOVER']['local_torrent_folder']) == False: os.mkdir(config['TORRENT_MOVER']['local_torrent_folder'])
        if os.path.isdir(config['TORRENT_MOVER']['remote_torrent_folder']) == False: print('Folder to copy from not exist'); exit()
        local_torrent_folder = config['TORRENT_MOVER']['local_torrent_folder']
        remote_torrent_folder = config['TORRENT_MOVER']['remote_torrent_folder']
        code = f"""#!/usr/bin/bash
    while true
    do
    if [ -z "$(ls -A {remote_torrent_folder})" ]; then
    echo "Empty"
    else
    echo "Not Empty"
    mv {remote_torrent_folder}* {local_torrent_folder}
    fi
    done"""
        # creating python script in folder
        torrent_file = dir + 'torrent.sh'
        with open(torrent_file, 'w') as f:
            f.write(code)
        runcom(f"sudo chmod +x {torrent_file}", True)
        service_code = f"""[Install]
    WantedBy=multi-user.target

    [Unit]
    Description=Copies files from HDD to torrent folder
    StartLimitIntervalSec=30
    StartLimitBurst=2

    [Service]
    ExecStart=/usr/bin/bash {dir}/torrent.sh
    Restart=always"""
        service_file = 'torrentmover.service'
        with open(service_file, 'w') as f:
            f.write(service_code)
        runcom(f'sudo chmod +x {service_file} && sudo cp {service_file} /etc/systemd/system/ && sudo systemctl start {service_file} && sudo systemctl enable {service_file} && rm -rf {service_file}', False)
# remove changes made by script
def remove_f():
    if os.path.isdir(dir) == True:
        import shutil
        shutil.rmtree(dir)
        print('0')
        
# argument processing
if len(sys.argv) == 2:
    option = str(sys.argv[1])
    if option in args:
        if option == 'install':
            print('installing...')
            defapps_f()
            autoupdate_f()
            musicdownloader_f()
            torrentmover_f()
        elif option == 'verify':
            print('verifying...')
        elif option == 'debug':
            print('debugging...')
        elif option == 'remove':
            print('removing...')
            remove_f()
    else:
        print('Command not found')
