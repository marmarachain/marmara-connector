import subprocess, pathlib
import time

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
        result = ""
        marmarad_pid = subprocess.Popen('pidof komodod', shell=True, stdout=subprocess.PIPE)
        while True:
            line = marmarad_pid.stdout.readlines()
            if not line:
                marmarad_pid.terminate()
                break
            result = result + str(line)
        print(result)
    else:
        marmarad_pid = remote_connection.server_execute_command('pidof komodod')
        result = marmarad_pid[0]
    return result


def start_chain():
    if is_local:
        marmara_param = cp.start_param_local()
        marmara_param = marmara_param + ' &'
        start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        start.communicate()
        start.terminate()
        print('shell closed')


    else:
        marmara_param = cp.start_param_remote()
        marmara_param = marmara_path + marmara_param
        start = remote_connection.server_start_chain(marmara_param)
        start.close()
        print('shell closed')


def execute_rpc(command):
    if is_local:
        cmd = cp.set_local(command)
        out = ""
        err = ""
        proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = proc.stdout.readlines()
            if not line:
                proc.terminate()
                break
            out = out + str(line)
        while True:
            line = proc.stderr.readlines()
            if not line:
                proc.terminate()
                break
            err = err + str(line)
    else:
        cmd = cp.set_remote(command)
        cmd = marmara_path + cmd
        result = remote_connection.server_execute_command(cmd)
        out = result[0]
        err = result[1]
    return out, err


def getinfo():
    output = execute_rpc(cp.getinfo)
    stdout = output[0]
    stderr = output[1]
    return stdout, stderr


def getaddresses():
    output = execute_rpc(cp.getaddressesbyaccount)
    stdout = output[0]
    stderr = output[1]
    return stdout, stderr


def stop_chain():
    output = execute_rpc(cp.stop)
    stdout = output[0]
    stderr = output[1]
    result = output[2]
    return stdout, stderr, result

