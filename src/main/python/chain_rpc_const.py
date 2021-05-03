import platform

import configuration
linux_d = './komodod -ac_name="MCL" '
windows_d = 'komodod.exe -ac_name="MCL" '
linux_cli = './komodo-cli -ac_name="MCL" '
windows_cli = 'komodo-cli.exe -ac_name="MCL" '
marmarad = '-ac_supply=2000000 -ac_cc=2 -addnode=37.148.210.158 -addnode=37.148.212.36 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000 &'
getinfo = "getinfo"


def start_param_local():
    global marmarad
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        marmarad = linux_d + marmarad
    if platform.system() == 'Windows':
        marmarad = windows_d + marmarad
    return marmarad


def start_param_remote():
    global marmarad
    marmarad = linux_d + marmarad
    return marmarad

def getinfo_remote():
    global getinfo
    getinfo = linux_cli + getinfo
    return getinfo


def getinfo_local():
    global getinfo
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        getinfo = linux_cli + getinfo
    if platform.system() == 'Windows':
        getinfo = windows_cli + getinfo
    return getinfo
