def torrentmover_f():
    if config['TORRENT_MOVER'].getboolean('torrent_mover') == True:
        create_dir()
        local_torrent_folder = dir + 'torrent/'
        if os.path.isdir(local_torrent_folder) == False: os.mkdir(local_torrent_folder)
        if os.path.isdir(config['TORRENT_MOVER']['remote_torrent_folder']) == False: print('Folder to copy from not exist'); exit()
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
