import os, subprocess, pathlib
import remote_connection
import chain_rpc_const as cp

is_local = None


def set_connection_local():
    global is_local
    is_local = True


def set_connection_remote():
    global is_local
    is_local = False


def getinfo():
    if is_local:
        cp.getinfo_local()
    else:
        cp.getinfo_remote()
