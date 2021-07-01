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


def mcl_chain_status():
    if is_local:
        result = ""
        marmarad_pid = subprocess.Popen('pidof komodod', shell=True, stdout=subprocess.PIPE)
        while True:
            line = marmarad_pid.stdout.readlines()
            if not line:
                marmarad_pid.terminate()
                break
            result = result + str(line)
    else:
        marmarad_pid = remote_connection.server_execute_command('pidof komodod')
        result = marmarad_pid[0]
    return result


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


class RpcHandler(QtCore.QObject):
    command_out = pyqtSignal(tuple)
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
