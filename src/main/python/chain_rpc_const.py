import platform

import configuration

Linux = './komodo-cli -ac_name="MCL" '
windows = 'komodo-cli.exe -ac_name="MCL" '

getinfo = "getinfo"


def getinfo_remote():
    global getinfo
    getinfo = Linux + getinfo
    print(getinfo)
    return getinfo


def getinfo_local():
    global getinfo
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        getinfo = Linux + getinfo
    if platform.system() == 'Windows':
        getinfo = windows + getinfo
    print(getinfo)
    return getinfo
