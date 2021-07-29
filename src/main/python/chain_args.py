import platform

import configuration

linux_d = './komodod -ac_name=MCL '
windows_d = 'komodod.exe -ac_name=MCL '
linux_cli = './komodo-cli -ac_name=MCL '
windows_cli = 'komodo-cli.exe -ac_name=MCL '
marmarad = '-ac_supply=2000000 -ac_cc=2 -addnode=37.148.210.158 -addnode=37.148.212.36 -addnode=149.202.158.145 -addressindex=1 -spentindex=1 -ac_marmara=1 -ac_staked=75 -ac_reward=3000000000'
marmara_pid = 'pidof komodod'
getinfo = "getinfo"
validateaddress = 'validateaddress'
getaddressesbyaccount = 'getaddressesbyaccount ""'
listaddressgroupings = 'listaddressgroupings'
setpubkey = 'setpubkey'
getnewaddress = 'getnewaddress'
stop = 'stop'
marmaraunlock = 'marmaraunlock'
marmaralock = 'marmaralock'
getbalance = 'getbalance'
getaddressbalance = 'getaddressbalance '  # +  '{"addresses": ["address"]}'
convertpassphrase = 'convertpassphrase'  # + "agamapassphrase"
importprivkey = 'importprivkey'  # + "wifkey"
dumpprivkey = 'dumpprivkey'  # + "address"
marmarainfo = 'marmarainfo' # 0 0 0 pubkey

def start_param_local(marmarad):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        marmarad = linux_d + marmarad
    if platform.system() == 'Windows':
        marmarad = windows_d + marmarad
    return marmarad


def start_param_remote():
    global marmarad
    marmarad = linux_d + marmarad
    return marmarad


def set_remote(command):
    command = linux_cli + command
    return command


def set_local(command):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        command = linux_cli + command
    if platform.system() == 'Windows':
        if command.find("{"):
            command = command.replace("'{", '{').replace("}'", '}').replace('"', '\\"')
        command = windows_cli + command
    return command


def set_pid_local(command):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return command
    if platform.system() == 'Windows':
        marmara_pid = 'tasklist | findstr komodod'
        return marmara_pid