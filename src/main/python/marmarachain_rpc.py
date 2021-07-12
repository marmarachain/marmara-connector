import json
import subprocess, pathlib
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import remote_connection
import chain_args as cp

marmara_path = str(pathlib.Path.home()) + '/komodo/src/'
is_local = None


def set_connection_local():
    global is_local
    is_local = True


def set_connection_remote():
    global is_local
    is_local = False


def start_chain():
    if is_local:
        marmara_param = cp.start_param_local()
        marmara_param = marmara_param + ' &'
        start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        start.communicate()
        start.terminate()
        print('shell closed')
    else:
        marmara_param = cp.start_param_remote()
        marmara_param = marmara_path + marmara_param
        start = remote_connection.server_start_chain(marmara_param)
        start.close()
        print('shell closed')


def mcl_chain_status():
    if is_local:
        marmara_pid = cp.set_pid_local(cp.marmara_pid)
        marmarad_pid = subprocess.Popen(marmara_pid, shell=True, stdout=subprocess.PIPE)
        marmarad_pid.wait()
        marmarad_pid.terminate()
        return marmarad_pid.stdout.read().decode("utf8"), marmarad_pid.stdout.read().decode("utf8")
    else:
        marmarad_pid = remote_connection.server_execute_command(cp.marmara_pid)
    return marmarad_pid


def handle_rpc(command):
    if is_local:
        cmd = cp.set_local(command)
        proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        retvalue = proc.poll()
        return proc.stdout.read().decode("utf8"), proc.stderr.read().decode("utf8"), retvalue
    else:
        cmd = cp.set_remote(command)
        cmd = marmara_path + cmd
        result = remote_connection.server_execute_command(cmd)
        return result


class RpcHandler(QtCore.QObject):
    command_out = pyqtSignal(tuple)
    daemon_pid = pyqtSignal(str)
    walletlist_out = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.command = ""

    @pyqtSlot(str)
    def set_command(self, value):
        self.command = value

    @pyqtSlot()
    def do_execute_rpc(self):

        result_out = handle_rpc(self.command)
        self.command_out.emit(result_out)
        self.finished.emit()

    @pyqtSlot()
    def chain_pid(self):
        i = 10
        while True:
            result_out = mcl_chain_status()
            if len(result_out[0]) > 0:
                self.daemon_pid.emit(str(result_out[0]))
                self.finished.emit()
                print('chain has pid')
                break
            time.sleep(1)
            i = i - 1
            if i == 0:
                print('tried still no pid')
                self.daemon_pid.emit(str(result_out[0]))
                self.finished.emit()
                break
            elif result_out[1]:
                print('error')
                self.daemon_pid.emitstr(str(result_out[1]))
                break

    @pyqtSlot()
    def is_chain_ready(self):
        while True:
            result_out = handle_rpc(self.command)
            if result_out[0]:
                self.command_out.emit(result_out)
                self.finished.emit()
                print('chain ready')
                break
            elif result_out[1]:
                self.command_out.emit(result_out)
                time.sleep(2)
                print('chain is not ready')

    @pyqtSlot()
    def stopping_chain(self):
        result_out = handle_rpc(cp.stop)
        self.command_out.emit(result_out)
        print(result_out[0])
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
                address_list = [address, pubkey, amount]
                wallet_list.append(address_list)
            self.walletlist_out.emit(wallet_list)
            self.finished.emit()
        elif addresses[1]:
            print(addresses[1])
            self.finished.emit()
