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
        result = marmarad_pid.stdout
    else:
        marmarad_pid = remote_connection.server_execute_command('pidof komodod')
        result = marmarad_pid[0]
    return result


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
        result = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout
        stderr = result.stderr
    else:
        cmd = cp.getinfo_remote()
        cmd = marmara_path + cmd
        ssh = remote_connection.server_execute_command(cmd)
        result = ssh[2]
        stdout = ssh[0]
        stderr = ssh[1]
    return stdout, stderr, result

# def getaddresses():
#     if is_local:
#         cmd = cp.
#     else:
#
#     return