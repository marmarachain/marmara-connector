import time

import paramiko
from PyQt5.QtCore import QThread, pyqtSignal


class AutoInstall(QThread):
    change_value_text_edit = pyqtSignal(str)
    change_value_progressbar = pyqtSignal(int)

    withBootstrap = False
    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22
    mcl_linux_download_command = ""


    def run(self):
        self.mcl_install_connect_ssh()


    def remote_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.server_hostname, username=self.server_username, password=self.server_password, port=self.server_port)
        return ssh

    def ssh_run_command(self, command, sudo=False):
        client = self.remote_connect()
        if sudo:
            command = 'sudo -S -- ' + command + '\n'
        stdin, stdout, stderr = client.exec_command(command)
        if sudo:
            stdin.write(self.server_password + '\n')
            stdin.flush()
            stdin.channel.shutdown_write()
        exit_status = stdout.channel.recv_exit_status()  # wait for exec_command to finish
        client.close()
        return {'out': stdout.read().decode("utf8"), 'err': stderr.read().decode("utf8"), 'retval': exit_status}

    def print_out_emit(self, result):
        print(result.get('retval'))
        if result.get('retval') == 0:
            for item in result.get('out').splitlines():
                self.change_value_text_edit.emit(str(item))
        else:
            for item in result.get('err').splitlines():
                self.change_value_text_edit.emit(str(item))


    def mcl_install_connect_ssh(self):
        self.change_value_text_edit.emit(str("starting auto install"))
        self.change_value_text_edit.emit(str("update Server"))
        update = self.ssh_run_command('sudo apt-get update', sudo=True)
        self.print_out_emit(update)
        self.change_value_progressbar.emit(2)
        self.change_value_text_edit.emit(str("installing dependency"))
        depend = self.ssh_run_command('sudo apt-get install libgomp1 -y', sudo=True)
        self.print_out_emit(depend)
        self.change_value_progressbar.emit(7)
        depend = self.ssh_run_command('sudo apt-get install unzip -y', sudo=True)
        self.print_out_emit(depend)
        self.change_value_progressbar.emit(8)
        self.change_value_text_edit.emit(str("Downloading latest MCL version"))
        self.change_value_text_edit.emit(str("------------------------------"))
        get_mcl_zip = self.ssh_run_command('wget ' + self.mcl_linux_download_command, sudo=True)
        self.change_value_text_edit.emit(str('Download complete ...'))
        self.change_value_progressbar.emit(15)
        self.change_value_text_edit.emit(str("Extracting Files..."))
        unzip_mcl_zip = self.ssh_run_command('unzip MCL-linux.zip')
        self.print_out_emit(unzip_mcl_zip)
        self.change_value_progressbar.emit(22)
        self.change_value_text_edit.emit("Setting permissions...")
        allow_mcl = self.ssh_run_command('sudo chmod +x komodod komodo-cli fetch-params.sh', sudo=True)
        self.print_out_emit(allow_mcl)
        self.change_value_progressbar.emit(25)

        self.change_value_text_edit.emit("Running Fetch Parameters...")
        zcash_get = self.ssh_run_command('./fetch-params.sh')
        self.print_out_emit(zcash_get)
        self.change_value_progressbar.emit(67)
        self.change_value_text_edit.emit("Finished Fetch Parameters.")

        if self.withBootstrap:
            download_bootstrap = self.ssh_run_command('wget https://eu.bootstrap.dexstats.info/MCL-bootstrap.tar.gz -O MCL-bootstrap.tar.gz')
            self.print_out_emit(download_bootstrap)
            self.change_value_progressbar.emit(78)
            blocks = self.ssh_run_command('mkdir -p ~/.komodo/MCL')
            self.print_out_emit(blocks)
            extract_blocks = self.ssh_run_command('tar -xvf MCL-bootstrap.tar.gz -C .komodo/MCL')
            self.print_out_emit(extract_blocks)

        self.change_value_progressbar.emit(100)
