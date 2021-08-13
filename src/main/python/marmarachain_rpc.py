import json
import platform
import re
import time
import subprocess
import pathlib
import version

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import remote_connection
import chain_args as cp
import configuration

marmara_path = configuration.ConnectorConf().read_conf_file().get('marmarad_path')
is_local = None


def set_connection_local():
    global is_local
    is_local = True


def set_connection_remote():
    global is_local
    is_local = False


def set_marmara_path(path):
    global marmara_path
    marmara_path = path


def start_param_local(marmarad):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        marmarad = cp.linux_d + marmarad
    if platform.system() == 'Windows':
        marmarad = cp.windows_d + marmarad
    return marmarad


def start_param_remote():
    marmarad = cp.linux_d + cp.marmarad
    return marmarad


def set_remote(command):
    command = cp.linux_cli + command
    return command


def set_local(command):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        command = cp.linux_cli + command
    if platform.system() == 'Windows':
        if command.find("{"):
            command = command.replace("'{", '{').replace("}'", '}').replace('"', '\\"')
        command = cp.windows_cli + command
    return command


def set_pid_local(command):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return command
    if platform.system() == 'Windows':
        marmara_pid = 'tasklist | findstr komodod'
        return marmara_pid


def do_search_path(cmd):
    if is_local:
        mcl_path = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        mcl_path.wait()
        mcl_path.terminate()
        return mcl_path.stdout.read().decode("utf8").split('\n'), mcl_path.stdout.read().decode("utf8").split('\n')
    else:
        mcl_path = remote_connection.server_execute_command(cmd)
        return mcl_path[0].split('\n'), mcl_path[1].split('\n'),


def search_marmarad_path():  # will be added for windows search
    search_list = ['ls ' + str(pathlib.Path.home()), 'ls ' + str(pathlib.Path.home()) + '/marmara/src',
                   'ls ' + str(pathlib.Path.home()) + '/komodo0/src']
    i = 0
    while True:
        path = do_search_path(search_list[i])
        if not path[0] == ['']:
            if 'komodod' in path[0] and 'komodo-cli' in path[0]:
                out_path = search_list[i]
                out_path = out_path.replace('ls ', '') + '/'
                break
            else:
                i = i + 1
        else:
            i = i + 1
        if i == 3:
            out_path = ""
            break
    return out_path


def start_chain(pubkey=None):
    if is_local:
        marmara_param = start_param_local(cp.marmarad)
        if pubkey is None:
            marmara_param = marmara_param + ' &'
        if pubkey is not None:
            marmara_param = marmara_param + ' -pubkey=' + str(pubkey) + ' &'
        start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        start.communicate()
        start.terminate()
        print('shell closed')
    else:
        marmara_param = start_param_remote()
        if not pubkey:
            marmara_param = marmara_path + marmara_param
        if pubkey:
            marmara_param = marmara_param + ' -pubkey=' + str(pubkey)
        start = remote_connection.server_start_chain(marmara_param)
        start.close()
        print('shell closed')


def mcl_chain_status():
    if is_local:
        marmara_pid = set_pid_local('pidof komodod')
        marmarad_pid = subprocess.Popen(marmara_pid, shell=True, stdout=subprocess.PIPE)
        marmarad_pid.wait()
        marmarad_pid.terminate()
        return marmarad_pid.stdout.read().decode("utf8"), marmarad_pid.stdout.read().decode("utf8")
    else:
        marmarad_pid = remote_connection.server_execute_command('pidof komodod')
    return marmarad_pid


def handle_rpc(command):
    if is_local:
        cmd = set_local(command)
        proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        retvalue = proc.poll()
        return proc.stdout.read().decode("utf8"), proc.stderr.read().decode("utf8"), retvalue
    else:
        cmd = set_remote(command)
        cmd = marmara_path + cmd
        result = remote_connection.server_execute_command(cmd)
        return result


class RpcHandler(QtCore.QObject):
    command_out = pyqtSignal(tuple)
    output = pyqtSignal(str)
    walletlist_out = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.command = ""
        self.bottom_info_obj = object

    @pyqtSlot(str)
    def set_command(self, value):
        self.command = value

    @pyqtSlot(object, str)
    def set_bottom_info(self, info_obj, value):
        self.bottom_info_obj = info_obj
        self.info_value = value

    @pyqtSlot()
    def write_bottom_info(self):
        self.bottom_info_obj.setText(self.info_value)
        self.finished.emit()

    @pyqtSlot()
    def do_execute_rpc(self):
        result_out = handle_rpc(self.command)
        self.command_out.emit(result_out)
        self.finished.emit()

    @pyqtSlot()
    def is_chain_ready(self):
        while True:
            result_out = handle_rpc(cp.getinfo)
            if result_out[0]:
                self.command_out.emit(result_out)
                self.finished.emit()
                print('chain ready')
                break
            elif result_out[1]:
                self.command_out.emit(result_out)
                # print('chain is not ready')
            time.sleep(2)

    @pyqtSlot()
    def stopping_chain(self):
        result_out = handle_rpc(cp.stop)
        self.command_out.emit(result_out)
        if result_out[0]:
            while True:
                pid = mcl_chain_status()
                if len(pid[0]) == 0:
                    self.finished.emit()
                    self.command_out.emit(pid)
                    print('chain stopped')
                    break
                time.sleep(1)
        elif result_out[1]:
            self.command_out.emit(result_out)
            self.finished.emit()

    @pyqtSlot()
    def get_addresses(self):
        addresses = handle_rpc(cp.getaddressesbyaccount)
        if addresses[0]:
            addresses = json.loads(addresses[0])
            wallet_list = []
            for address in addresses:
                validation = handle_rpc(cp.validateaddress + ' ' + address)
                if validation[0]:
                    if json.loads(validation[0])['ismine']:
                        pubkey = json.loads(validation[0])['pubkey']
                elif validation[1]:
                    print(validation[1])
                address_js = {'addresses': [address]}
                command = cp.getaddressbalance + "'" + json.dumps(address_js) + "'"
                amounts = handle_rpc(command)
                if amounts[0]:
                    amount = json.loads(amounts[0])['balance']
                elif amounts[1]:
                    print(amounts[1])
                address_list = [amount, address, pubkey]
                wallet_list.append(address_list)
            self.walletlist_out.emit(wallet_list)
            self.finished.emit()
        elif addresses[1]:
            print(addresses[1])
            self.finished.emit()

    @pyqtSlot()
    def refresh_sidepanel(self):
        getinfo = handle_rpc(cp.getinfo)
        if getinfo[0]:
            self.command_out.emit(getinfo)
            getgenerate = handle_rpc(cp.getgenerate)
            if getgenerate[0]:
                self.command_out.emit(getgenerate)
                self.finished.emit()
            elif getgenerate[1]:
                self.command_out(getgenerate)
                self.finished.emit()
        elif getinfo[1]:
            self.command_out.emit(getinfo)
            self.finished.emit()

    @pyqtSlot()
    def setgenerate(self):
        setgenerate = handle_rpc(self.command)
        if setgenerate[2] == 0:
            getgenerate = handle_rpc(cp.getgenerate)
            self.finished.emit()
            self.command_out.emit(getgenerate)
        else:
            self.finished.emit()
            self.command_out.emit(setgenerate)


class Autoinstall(QtCore.QObject):
    out_text = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mcl_linux_download_command = version.latest_marmara_zip_url()
        self.linux_command_list = ['sudo apt-get update', 'sudo apt-get install libgomp1 -y',
                                   'wget ' + str(self.mcl_linux_download_command) + '/MCL-linux.zip',
                                   'sudo apt-get install unzip -y', 'unzip MCL-linux.zip',
                                   'sudo chmod +x komodod komodo-cli fetch-params.sh', './fetch-params.sh']
        self.win_command_list = []

    @pyqtSlot()
    def start_install(self):
        if is_local:
            if platform.system() == 'Linux':
                self.out_text.emit(str("installing on linux"))
                self.linux_install()
            if platform.system() == 'Windows':
                self.windows_install()
        else:
            self.out_text.emit(str("installing on linux"))
            self.linux_install()

    def linux_install(self):
        self.out_text.emit(str("update linux"))
        i = 0
        while i < len(self.linux_command_list):
            cmd = self.linux_command_list[i]
            if cmd.startswith('sudo'):
                cmd = 'sudo -S -- ' + cmd + '\n'
            print(cmd)
            if is_local:
                print('local linux installation not coded yet!')
                # proc = subprocess.Popen(cmd, cwd=str(pathlib.Path.home()), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            else:
                sshclient = remote_connection.server_ssh_connect()
                session = sshclient.get_transport().open_session()
                stdin = session.makefile_stdin('wb', -1)
                stdout = session.makefile('rb', -1)
                session.exec_command(cmd)
                if cmd.startswith('sudo'):
                    stdin.write(remote_connection.server_password + '\n')
                    stdin.flush()
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        out = stdout.channel.recv(4096).decode()
                        print(str(out))
                        self.out_text.emit(str(out))
                    if stdout.channel.recv_stderr_ready():
                        err = stdout.channel.recv_stderr(4096).decode()
                        self.out_text.emit(str(err))
                        print(str(err))
                exit_status = session.recv_exit_status()  # Blocking call
                print(exit_status)
                session.close()
                sshclient.close()
            i = i + 1
            self.progress.emit(int(i*14))
        self.finished.emit()

    def windows_install(self):
        self.out_text.emit(str("installing on windows"))
        print('local Windows installation not coded yet!')
        # update = subprocess.Popen

