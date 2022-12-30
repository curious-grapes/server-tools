## server-tools
This set of scripts is responsible for creating and scripts on a Linux server. It is configurable via a configuration file, allowing you to easily set up and customize your tasks.

##### Prerequisites
- A Linux machine with Systemd installed
- Python 3
- The following Python packages: sshconf

##### TO-DO
- [] write other arguments
- [] notifications
- [] remove function
- [] verify function
- [] clean function
- [] add more output while script is running
- [] fix bugs

##### Installation
Install Python and dependency packages:
```bash
sudo apt update -y && sudo apt install python3 python3-pip -y && pip install sshconf
```
Clone the repository to your Linux machine:
```bash
git clone https://github.com/curious_grapes/server-tools.git
```
Navigate to the repository directory:
```bash
cd server-tools
```

Copy the configuration file (my.conf) to specify your desired tasks. An example configuration is provided in sample.conf.

Run the create_tasks.py script with one of the following arguments to create the specified tasks:
-   Install
```bash
python3 install.py install
```
-   Verify
```bash
python3 install.py verify
```
-   Clean
```bash
python3 install.py clean
```
-   Remove
```bash
python3 install.py remove
```
##### Configuration
The configuration file (sample.conf) is a file that specifies the tasks to be created. It has the following structure:
```
[PATH]
install_def_app = false
install_folder = /install_folder

[AUTOUPDATE]
auto_update = false

[MUSIC_DOWNLOADER]
yt_download = false
songs_folder = /songs_folder
yt_playlist =

[TORRENT_MOVER]
torrent_mover = false
local_torrent_folder = /local_torrent_folder
remote_torrent_folder = /remote_torrent_folder
```
"install_def_app": installs default apps if true (htop, wget, curl, sudo, lnav), boolean;
"install_folder": where scripts should be saved, path to folder;

Autoupdate feature parses your ssh config(assuming you are using key authentication)
"auto_update": generates script with hardcoded ssh hosts and adds task to crontab that runs everyday at 3:00AM, boolean;

"yt_download": generates script that checks youtube playlist for updates, then downloads mp3 tracks from all videos in playlist and adds task to crontab that runs everyday at 3:00AM, boolean;
"songs_folder": where musics from playlist should be saved, path to folder;
"yt_playlist": playlist to download from, url link;


"torrent_mover": generates script that moves .torrent files from local folder to remote one, boolean;
"local_torrent_folder": folder from which scripts takes files ,path to folder;
"remote_torrent_folder": folder where scripts moves files ,path to folder;
