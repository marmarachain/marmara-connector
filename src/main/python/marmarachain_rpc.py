import os, subprocess, pathlib
import remote_connection
import chain_rpc_const as cp

marmara_path = str(pathlib.Path.home()) + '/komodo/src'
is_local = None


def mcl_chain_status():
    marmarad_pid = subprocess.Popen('pidof komodod', shell=True, stdout=subprocess.PIPE)
    return marmarad_pid


def set_connection_local():
    global is_local
    is_local = True


def set_connection_remote():
    global is_local
    is_local = False


def start_chain():
    if is_local:
        marmara_param = cp.start_param_local()
        start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        marmara_param = cp.start_param_remote()
        start = remote_connection.send_command(marmara_param)
    return start


def getinfo():
    if is_local:
        cmd = cp.getinfo_local()
        proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE)
        result = proc.stdout
        proc.stdout.flush()
    else:
        cmd = cp.getinfo_remote()
        remote_connection.send_command(cmd)
    return result
