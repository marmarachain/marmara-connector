import os, subprocess, pathlib
import remote_connection
import chain_rpc_const as cp

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
        marmarad_pid = subprocess.Popen('pidof komodod', shell=True, stdout=subprocess.PIPE)
    else:
        marmarad_pid = remote_connection.server_execute_command('pidof komodod')
    return marmarad_pid


def start_chain():
    if is_local:
        marmara_param = cp.start_param_local()
        start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        marmara_param = cp.start_param_remote()
        marmara_param = marmara_path + marmara_param
        start = remote_connection.server_execute_command(marmara_param)
    return start


def getinfo():
    if is_local:
        cmd = cp.getinfo_local()
        proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE)
        result = proc.stdout
        proc.stdout.flush()
    else:
        cmd = cp.getinfo_remote()
        cmd = marmara_path + cmd
        result = remote_connection.server_execute_command(cmd)
    return result

# def getaddresses():
#     if is_local:
#         cmd = cp.
#     else:
#
#     return