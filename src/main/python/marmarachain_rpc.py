import json
import os
import platform
import time
import subprocess
import pathlib
import logging
from datetime import datetime, timedelta

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import remote_connection
import chain_args as cp
import configuration
import local_connection
import api_request

marmara_path = None
is_local = None
logging.getLogger(__name__)
ssh_client = None
zcash_path = None
zcash_files = ['/sapling-output.params', '/sapling-spend.params', '/sprout-groth16.params',
               '/sprout-proving.key', '/sprout-verifying.key']
zcash_files_size = [3592860, 47958396, 725523612, 910173851, 1449]


def set_connection_local():
    global is_local
    is_local = True


def set_connection_remote():
    global is_local
    is_local = False


def set_sshclient(client):
    global ssh_client
    ssh_client = client


def set_marmara_path(path):
    global marmara_path
    marmara_path = path


def get_zcash_path():
    global zcash_path
    if is_local:
        if platform.system() == 'Win64' or platform.system() == 'Windows':
            zcash_path = '%s/ZcashParams' % os.environ['APPDATA']
        if platform.system() == 'Linux':
            zcash_path = str(pathlib.Path.home()) + '/.zcash-params'
        logging.info('zcash_path= ' + zcash_path)
        return zcash_path
    else:
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        pwd_r = remote_connection.server_execute_command('pwd', ssh_client)
        time.sleep(0.2)
        if not pwd_r[0]:
            set_sshclient(remote_connection.server_ssh_connect())
            pwd_r = remote_connection.server_execute_command('pwd', ssh_client)
            time.sleep(0.1)
        zcash_path = str(pwd_r[0]).replace('\n', '').replace('\r', '') + '/.zcash-params'
        logging.info('zcash_path_r= ' + zcash_path)
        return zcash_path


def start_param_local(marmarad):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        marmarad = cp.linux_d + marmarad
    if platform.system() == 'Windows':
        marmarad = cp.windows_d + marmarad
    return marmarad


def start_param_remote():
    marmarad = cp.linux_d + cp.marmarad
    return marmarad


def set_remote(command):
    command = cp.linux_cli + command
    return command


def set_pid_local(command):
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return command
    if platform.system() == 'Windows':
        marmara_pid = 'tasklist | findstr komodod'
        return marmara_pid


def do_search_path(cmd):
    if is_local:
        try:
            mcl_path = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            mcl_path.wait()
            mcl_path.terminate()
            return mcl_path.stdout.read().decode().split('\n'), mcl_path.stdout.read().decode().split('\n')
        except Exception as error:
            logging.error(error)
    else:
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        try:
            mcl_path = remote_connection.server_execute_command(cmd, ssh_client)
            return mcl_path[0].split('\n'), mcl_path[1].split('\n'),
        except Exception as error:
            logging.error(error)


def search_marmarad_path():  # will be added for windows search
    windows = False
    if is_local:  # add for windows and mac
        pwd = str(pathlib.Path.home())
        logging.info('pwd local :' + pwd)
        if platform.system() == 'Windows':
            windows = True
            pwd = pwd.replace(' ', '` ')
        else:
            windows = False
    else:
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        pwd_r = remote_connection.server_execute_command('pwd', ssh_client)
        time.sleep(0.2)
        if not pwd_r[0]:
            set_sshclient(remote_connection.server_ssh_connect())
            pwd_r = remote_connection.server_execute_command('pwd', ssh_client)
            time.sleep(0.1)
        pwd = str(pwd_r[0]).replace('\n', '').replace('\r', '')
        logging.info('pwd_remote= ' + pwd)
    search_list_linux = ['ls ' + pwd, 'ls ' + pwd + '/marmara/src', 'ls ' + pwd + '/komodo/src']
    search_list_windows = ['PowerShell ls ' + pwd + '\marmara -name']
    if windows:
        out_path = check_path_windows(search_list_windows)
        return out_path
    else:
        out_path = check_path_linux(search_list_linux)
        return out_path


def check_path_linux(search_list):
    i = 0
    while True:
        search_path = search_list[i]
        logging.info('search_path= ' + search_path)
        path = do_search_path(search_path)
        if not path[0] == ['']:
            if 'komodod' in path[0] and 'komodo-cli' in path[0]:
                out_path = search_path
                out_path = out_path.replace('ls ', '') + '/'
                logging.info('out_path= ' + out_path)
                break
            else:
                i = i + 1
        else:
            i = i + 1
        if i == len(search_list):
            out_path = ""
            break
    return out_path


def check_path_windows(search_list):
    i = 0
    while True:
        search_path = search_list[i]
        logging.info('search_path= ' + search_path)
        path = do_search_path(search_path)
        logging.info(path)
        if not path[0] == ['']:
            out = str(path[0]).replace('.exe', '').replace('\r', '')
            if 'komodod' in out and 'komodo-cli' in out:
                out_path = search_path.replace('` ', ' ')
                out_path = out_path.replace('PowerShell ls ', '').replace(' -name', '') + '\\'
                logging.info('out_path= ' + out_path)
                break
            else:
                i = i + 1
        else:
            i = i + 1
        if i == len(search_list):
            out_path = ""
            break
    return out_path


def check_zcashparams():
    zcash_path = get_zcash_path()
    if is_local:
        if os.path.exists(zcash_path):
            missing = []
            currupted = []
            for item in zcash_files:
                index = zcash_files.index(item)
                if os.path.exists(zcash_path + item):
                    file_size = os.stat(zcash_path + item).st_size
                    if file_size < zcash_files_size[index]:
                        currupted.append(item)
                else:
                    missing.append(item)
            if missing == [] and currupted == []:
                return 0, None
            else:
                return 1, currupted, missing
        else:
            return 1, ' folder missing', None
    else:
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        try:
            cmd = 'ls -l ' + zcash_path
            zcp_path = remote_connection.server_execute_command(cmd, ssh_client)
            if zcp_path[1]:
                return 1, ' folder missing', None
            if zcp_path[0]:
                missing = []
                currupted = []
                for item in zcash_files:
                    index = zcash_files.index(item)
                    cmd = 'stat -c %s ' + zcash_path + item
                    zcp_file_size = remote_connection.server_execute_command(cmd, ssh_client)
                    if zcp_file_size[0] and not zcp_file_size[1]:
                        if int(zcp_file_size[0].strip('\n')) < zcash_files_size[index]:
                            currupted.append(item)
                    if not zcp_file_size[0] and zcp_file_size[1]:
                        missing.append(item)
                if missing == [] and currupted == []:
                    return 0, None
                else:
                    return 1, currupted, missing
        except Exception as error:
            logging.error(error)


def start_chain(pubkey=None):
    if is_local:
        marmara_param = start_param_local(cp.marmarad)
        if pubkey is None:
            marmara_param = marmara_param + ' &'
        if pubkey is not None:
            marmara_param = marmara_param + ' -pubkey=' + str(pubkey) + ' &'
        try:
            start = subprocess.Popen(marmara_param, cwd=marmara_path, shell=True, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            while True:
                pid = mcl_chain_status()
                if not len(pid) == 0:
                    break
            return
        except Exception as error:
            logging.error(error)
    else:
        marmara_param = start_param_remote()
        if not pubkey:
            marmara_param = marmara_path + marmara_param
        if pubkey:
            marmara_param = marmara_path + marmara_param + ' -pubkey=' + str(pubkey)
        try:
            start = remote_connection.server_start_chain(marmara_param)
            time.sleep(0.3)
            while True:
                pid = mcl_chain_status()
                if not len(pid) == 0:
                    start.close()
                    logging.info('shell closed')
                    break
        except Exception as error:
            logging.error(error)


def mcl_chain_status():
    if is_local:
        marmara_pid = set_pid_local('pidof komodod')
        try:
            marmarad_pid = subprocess.Popen(marmara_pid, shell=True, stdout=subprocess.PIPE)
            marmarad_pid.wait()
            marmarad_pid.terminate()
            return marmarad_pid.stdout.read().decode(), marmarad_pid.stdout.read().decode()
        except Exception as error:
            logging.error(error)
    else:
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        try:
            marmarad_pid = remote_connection.server_execute_command('pidof komodod', ssh_client)
            return marmarad_pid
        except Exception as error:
            logging.error(error)


def handle_rpc(method, params):
    if is_local:
        if method == cp.convertpassphrase or method == cp.importprivkey:
            logging.info('------sending command----- \n ' + method)
        else:
            logging.info('------sending command----- \n ' + method + str(params))
        try:
            result = local_connection.curl_response(method, params)
            return result
        except Exception as error:
            logging.error(error)
            return None, error, 1
    else:
        cmd = set_remote(method)
        cmd = marmara_path + cmd
        for item in params:
            if method == 'convertpassphrase':
                cmd = cmd + ' "' + item + '"'
            elif method == 'getaddressesbyaccount':
                cmd = cmd + ' ""'
            elif method == 'getaddresstxids' or method == 'marmaraissue' or method == 'marmaratransfer' \
                    or method == 'marmarareceive' or method == 'getaddressbalance':
                cmd = cmd + ' ' + json.dumps(item)
            elif method == 'setgenerate':
                cmd = cmd + ' ' + str(item).lower()
            else:
                cmd = cmd + ' ' + str(item)
        cmd = cmd.replace('{', "'{").replace('}', "}'")
        if method == cp.convertpassphrase or method == cp.importprivkey:
            logging.info('------sending command----- \n ' + method)
        else:
            logging.info('------sending command----- \n ' + cmd)
        if not ssh_client:
            set_sshclient(remote_connection.server_ssh_connect())
        try:
            result = remote_connection.server_execute_command(cmd, ssh_client)
            return result
        except Exception as error:
            logging.error(error)
            set_sshclient(remote_connection.server_ssh_connect())
            return None, error, 1


class RpcHandler(QtCore.QObject):
    command_out = pyqtSignal(tuple)
    output = pyqtSignal(str)
    walletlist_out = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self):
        super(RpcHandler, self).__init__()
        self.method = ""
        self.params = []
        self.command = ""

    @pyqtSlot(str)
    def set_command(self, value):
        self.command = value

    @pyqtSlot(str)
    def set_method(self, method):
        self.method = method

    @pyqtSlot(list)
    def set_params(self, params):
        self.params = params

    @pyqtSlot()
    def do_execute_rpc(self):
        result_out = handle_rpc(self.method, self.params)
        self.command_out.emit(result_out)
        time.sleep(0.1)
        self.finished.emit()

    @pyqtSlot()
    def check_marmara_path(self):
        self.output.emit('get marmarad path')
        path_key = ""
        if is_local:
            path_key = 'local'
        if not is_local:
            path_key = remote_connection.server_hostname
        marmarad_path = configuration.ApplicationConfig().get_value('PATHS', path_key)
        if marmarad_path:  # if these is path in configuration
            self.output.emit('marmarad_path= ' + marmarad_path)
            if platform.system() == 'Windows':
                ls_cmd = 'PowerShell ls ' + marmarad_path.replace(' ', '` ') + ' -name'
            else:
                ls_cmd = 'ls ' + marmarad_path
            self.output.emit('verifiying path')
            verify_path = do_search_path(ls_cmd)
            if not verify_path[0] == ['']:
                verify_path_out = str(verify_path[0]).replace('.exe', '')
                if 'komodod' in verify_path_out and 'komodo-cli' in verify_path_out:
                    self.output.emit('marmarad found.')
                    set_marmara_path(marmarad_path)
                    self.finished.emit()
                else:
                    self.get_marmarad_path(path_key)  # search path for marmarad
            elif verify_path[1]:
                self.get_marmarad_path(path_key)  # search path for marmarad
        else:
            self.get_marmarad_path(path_key)

    @pyqtSlot()
    def get_marmarad_path(self, path_key):
        self.output.emit('no path config')
        search_result = search_marmarad_path()
        if search_result:
            self.output.emit('marmarad found.')
            configuration.ApplicationConfig().set_key_value('PATHS', path_key, search_result)
            if marmara_path != search_result:
                set_marmara_path(search_result)
            self.finished.emit()
        else:
            self.output.emit('need to install mcl')
            self.finished.emit()

    @pyqtSlot()
    def is_chain_ready(self):
        i = 0
        while True:
            getinfo = handle_rpc(cp.getinfo, [])
            if getinfo[0]:
                logging.info('----getinfo result ----- \n' + str(getinfo[0]))
                self.command_out.emit(getinfo)
                time.sleep(0.1)
                addresses = self._get_addresses()
                time.sleep(0.1)
                if type(addresses) == list:
                    self.walletlist_out.emit(addresses)
                    activated_address_list = handle_rpc(cp.marmaralistactivatedaddresses, [])
                    time.sleep(0.1)
                    self.command_out.emit(activated_address_list)
                    getgenerate = handle_rpc(cp.getgenerate, [])
                    time.sleep(0.1)
                    self.command_out.emit(getgenerate)
                    self.finished.emit()
                    # print('chain ready')
                else:
                    # self.output.emit(addresses)
                    logging.warning('could not get addresses')
                    self.finished.emit()
                break
            if getinfo[1]:
                self.command_out.emit(getinfo)
            if getinfo[2] == 1:
                i = i + 1
                if i >= 10:
                    logging.error('could not start marmarachain')
                    getinfo = None, 'could not start marmarachain'
                    self.command_out.emit(getinfo)
                    self.finished.emit()
                    break
            # print('chain is not ready')
            time.sleep(2)

    @pyqtSlot()
    def stopping_chain(self):
        result_out = handle_rpc(cp.stop, [])
        if result_out[0]:
            self.command_out.emit(result_out)
            while True:
                pid = mcl_chain_status()
                if len(pid[0]) == 0:
                    self.finished.emit()
                    out = 0, None, 0
                    self.command_out.emit(out)
                    logging.info('chain stopped')
                    break
                time.sleep(1)
        elif result_out[1]:
            self.command_out.emit(result_out)
            self.finished.emit()

    def _get_addresses(self):
        addresses = handle_rpc(cp.getaddressesbyaccount, [''])
        if addresses[0]:
            addresses_js = json.loads(addresses[0])
            wallet_list = []
            amount = 0
            pubkey = ""
            for address in addresses_js:
                validation = handle_rpc(cp.validateaddress, [address])
                if validation[0]:
                    if json.loads(validation[0])['ismine']:
                        pubkey = json.loads(validation[0])['pubkey']
                elif validation[1]:
                    logging.info(validation[1])
                address_js = {'addresses': [address]}
                amounts = handle_rpc(cp.getaddressbalance, [address_js])
                if amounts[0]:
                    amount = json.loads(amounts[0])['balance']
                    amount = str(int(amount) / 100000000)
                elif amounts[1]:
                    logging.info('getting error in getbalance :' + str(amounts[1]))
                address_list = [amount, address, pubkey]
                wallet_list.append(address_list)
            return wallet_list
        elif addresses[1]:
            logging.error(addresses[1])
            return False

    @pyqtSlot()
    def get_addresses(self):
        addresses = self._get_addresses()
        if type(addresses) == list:
            self.walletlist_out.emit(addresses)
        else:
            self.walletlist_out.emit([])
            logging.info('could not get addresses')
            self.finished.emit()
        time.sleep(0.2)
        self.finished.emit()

    @pyqtSlot()
    def refresh_sidepanel(self):
        getinfo = handle_rpc(cp.getinfo, [])
        if getinfo[0]:
            self.command_out.emit(getinfo)
            time.sleep(0.1)
            activated_address_list = handle_rpc(cp.marmaralistactivatedaddresses, [])
            self.command_out.emit(activated_address_list)
            self.finished.emit()
        elif getinfo[1]:
            self.command_out.emit(getinfo)
            self.finished.emit()

    @pyqtSlot()
    def setgenerate(self):
        setgenerate = handle_rpc(self.method, self.params)
        if setgenerate[2] == 0 or setgenerate[2] == 200:
            getgenerate = handle_rpc(cp.getgenerate, [])
            time.sleep(0.1)
            self.command_out.emit(getgenerate)
            self.finished.emit()
        else:
            self.finished.emit()
            self.command_out.emit(setgenerate)

    @pyqtSlot()
    def get_balances(self):
        getbalance = handle_rpc(cp.getbalance, [])
        time.sleep(0.1)
        listaddressgroupings = handle_rpc(cp.listaddressgroupings, [])
        time.sleep(0.1)
        activated_address_list = handle_rpc(cp.marmaralistactivatedaddresses, [])
        time.sleep(0.1)
        if (getbalance[2] == 200 and listaddressgroupings[2] == 200 and activated_address_list[2] == 200) \
                or (getbalance[2] == 0 and listaddressgroupings[2] == 0 and activated_address_list[2] == 0):
            result = str(getbalance[0]).replace('\n', ''), json.loads(str(listaddressgroupings[0])), \
                     json.loads(str(activated_address_list[0])), 0
            self.command_out.emit(result)
            self.finished.emit()
        else:
            result = getbalance[1], listaddressgroupings[1], activated_address_list[1], 1
            self.command_out.emit(result)
            self.finished.emit()

    @pyqtSlot()
    def txids_detail(self):
        get_txids = handle_rpc(self.method, self.params)
        if get_txids[2] == 200 or get_txids[2] == 0:
            if get_txids[0] or get_txids[0] == []:
                details_list = []
                if len(get_txids[0]) != 0:
                    for txid in json.loads(get_txids[0]):
                        txid_detail = handle_rpc(cp.gettransaction, [txid])
                        if txid_detail[2] == 200 or txid_detail[2] == 0:
                            if txid_detail[0]:
                                detail = json.loads(txid_detail[0])
                                amount = detail.get('amount')
                                block_time = detail.get('blocktime')
                                txid_list = [txid, amount, block_time]
                                details_list.append(txid_list)
                        else:
                            print(txid_detail[1])
                            self.finished.emit()
                            break
                    result = details_list, 0
                    self.command_out.emit(result)
                    self.finished.emit()
                else:
                    result = details_list, 0
                    self.command_out.emit(result)
                    self.finished.emit()
        else:
            result_err = get_txids[1], 1
            self.command_out.emit(result_err)
            self.finished.emit()

    @pyqtSlot()
    def extract_bootstrap(self):
        cmd_list = []
        if os.path.exists(self.method + '/blocks'):
            if platform.system() == 'Linux':
                cmd_list.append('rm -r ' + self.method + '/blocks')
            if platform.system() == 'Win64' or platform.system() == 'Windows':
                cmd_list.append('rmdir /s /q ' + self.method + '\blocks')
        if os.path.exists(self.method + '/chainstate'):
            if platform.system() == 'Linux':
                cmd_list.append('rm -r ' + self.method + '/chainstate')
            if platform.system() == 'Win64' or platform.system() == 'Windows':
                cmd_list.append('rmdir /s /q ' + self.method + '\chainstate')
        cmd_list.append(self.command)
        self.do_execute_extract(cmd_list)

    def do_execute_extract(self, cmd_list):
        pwd_home = str(pathlib.Path.home())
        for cmd in cmd_list:
            proc = subprocess.Popen(cmd, cwd=pwd_home, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retvalue = proc.poll()
            while True:
                stdout = proc.stdout.readline().replace(b'\n', b'').replace(b'\r', b'').decode()
                self.output.emit(str(stdout))
                logging.info(str(stdout))
                if not stdout:
                    break
            self.output.emit(str(retvalue))
        self.finished.emit()

    def get_loop_detail(self, txid, holder=False):
        loop_detail = handle_rpc(cp.marmaracreditloop, [txid])
        if loop_detail[2] == 200 or loop_detail[2] == 0:
            if loop_detail[0]:
                loop_amount = json.loads(loop_detail[0]).get('amount')
                loop_matures = json.loads(loop_detail[0]).get('matures')
                pubkey = json.loads(loop_detail[0]).get('batonpk')
                creditloop = json.loads(loop_detail[0]).get('creditloop')
                loop_address = json.loads(loop_detail[0]).get('LockedInLoopCCaddr')
                loop_create_block = ""
                for item in creditloop:
                    if item.get('funcid') == 'B':
                        loop_create_block = item.get('height')
                        issuer_pk = item.get('issuerpk')
                        if holder:
                            pubkey = issuer_pk
                        break
                return [txid, loop_amount, pubkey, loop_matures, loop_create_block, loop_address]
        else:
            logging.error(loop_detail[1])
            return False

    @pyqtSlot()
    def active_loops_details(self):
        marmarainfo = handle_rpc(self.method, self.params)
        if marmarainfo[2] == 200 or marmarainfo[2] == 0:
            if marmarainfo[0]:
                marmarainfo_result = json.loads(marmarainfo[0])
                issuances_issuer = marmarainfo_result.get('issuances')
                issuer_details_list = []
                for issuance in issuances_issuer:
                    issuance_details = self.get_loop_detail(issuance)
                    if issuance_details:
                        issuer_details_list.append(issuance_details)
                    else:
                        logging.error('some error in getting loopdetail')
                        self.finished.emit()
                        break
                result = issuer_details_list, marmarainfo_result, 0
                self.command_out.emit(result)
                self.finished.emit()
        else:
            result_err = None, marmarainfo[1], 1
            self.command_out.emit(result_err)
            self.finished.emit()

    @pyqtSlot()
    def holder_loop_detail(self):
        marmaraholderloops = handle_rpc(self.method, self.params)
        if marmaraholderloops[2] == 200 or marmaraholderloops[2] == 0:
            if marmaraholderloops[0]:
                holer_result = json.loads(marmaraholderloops[0])
                issuances_holder = holer_result.get('issuances')
                holder_details_list = []
                for issuance in issuances_holder:
                    issuance_details = self.get_loop_detail(issuance, holder=True)
                    if issuance_details:
                        holder_details_list.append(issuance_details)
                    else:
                        logging.error('some error in getting loopdetail')
                        self.finished.emit()
                        break
                result = holder_details_list, holer_result, 0
                self.command_out.emit(result)
                self.finished.emit()
        else:
            result_err = None, marmaraholderloops[1], 1
            self.command_out.emit(result_err)
            self.finished.emit()

    @pyqtSlot()
    def check_fork_api(self):
        getblock = handle_rpc(self.method, self.params)
        if getblock[2] == 200 or getblock[2] == 0:
            if getblock[0]:
                result_json = json.loads(getblock[0])
                block = result_json.get('height')
                hash = result_json.get('hash')
                previous_hash = result_json.get('previousblockhash')
                # next_hash = result_json.get('nextblockhash')
                result_list = [block, hash, previous_hash]
                blocks_detail_api = api_request.get_blocks_details(block, hash)
                result_out = result_list, blocks_detail_api, 0
                self.command_out.emit(result_out)
                self.finished.emit()
        else:
            result_err = None, getblock[1], 1
            self.command_out.emit(result_err)
            self.finished.emit()

    @pyqtSlot()
    def calc_wallet_earnings(self):
        method_list = [self.method, self.method, cp.listaddressgroupings, cp.marmaralistactivatedaddresses]
        param_list = [[str(self.params[0])], [str(self.params[1])], [], []]
        normaladdresseslist = []
        activatedaddresslist = []
        days = []
        begin_day = None
        end_day = None
        index = 0
        for method in method_list:
            result = handle_rpc(method, param_list[index])
            if result[2] == 200 or result[2] == 0:
                if index == 0:
                    begin_day = datetime.fromtimestamp(json.loads(result[0]).get('time')).date()
                if index == 1:
                    end_day = datetime.fromtimestamp(json.loads(result[0]).get('time')).date()
                if index == 2:
                    normaladdresses = json.loads(result[0])
                    if len(normaladdresses) > 0:
                        normaladdresses = normaladdresses[0]
                    else:
                        normaladdresses = normaladdresses
                    for item in normaladdresses:
                        normaladdresseslist.append(item[0])
                if index == 3:
                    for item in json.loads(result[0]).get("WalletActivatedAddresses"):
                        activatedaddresslist.append(item.get('activatedaddress'))
            else:
                result_err = None, result[1], 1
                self.command_out.emit(result_err)
                self.finished.emit()
            if index < 3:
                index = index + 1
        days.append(begin_day)
        day_delta = (end_day - begin_day).days
        count = 0
        while day_delta != count:
            days.append(days[count] + timedelta(days=1))
            count = count + 1
        normaladdresstxidslist = []
        activatedaddresstxidslist = []
        self.output.emit('normal txids')
        for naddress in normaladdresseslist:
            normaladdresstxids = handle_rpc(cp.getaddresstxids, [{'addresses': [naddress], 'start': self.params[0],
                                                                  'end': self.params[1]}])[0]
            if normaladdresstxids:
                for txid in json.loads(normaladdresstxids):
                    normaladdresstxidslist.append(txid)
        self.output.emit('activated txids')
        for activatedaddress in activatedaddresslist:
            activatedaddresstxids = handle_rpc(cp.getaddresstxids, [{'addresses': [activatedaddress],
                                                                     'start': self.params[0],
                                                                     'end': self.params[1]}, 0])[0]
            if activatedaddresstxids:
                for txid in json.loads(activatedaddresstxids):
                    activatedaddresstxidslist.append(txid)
        na_earninglist = {}
        aa_earninglist = {}
        self.output.emit('calculating earnings')
        for daytime in days:
            na_earninglist.__setitem__(daytime, 0)
            aa_earninglist.__setitem__(daytime, 0)
        for txid in normaladdresstxidslist:
            coinbase = self.get_coinbase(txid)
            if coinbase[0]:  # coinbase[0]= timestamp, coinbase[1] = amount
                prv_value = na_earninglist.__getitem__(coinbase[0])
                na_earninglist.__setitem__(coinbase[0], (prv_value + coinbase[1]))
        for txid in activatedaddresstxidslist:
            coinbase = self.get_coinbase(txid)
            if coinbase[0]:
                prv_value = aa_earninglist.__getitem__(coinbase[0])
                aa_earninglist.__setitem__(coinbase[0], (prv_value + coinbase[1]))
        earningresult = na_earninglist, aa_earninglist, 0
        self.command_out.emit(earningresult)
        self.finished.emit()

    def get_coinbase(self, txid):
        rawtxid = handle_rpc(cp.getrawtransaction, [txid])
        if rawtxid[2] == 200 or rawtxid[2] == 0:
            if is_local:
                rawtx = json.loads(rawtxid[0])
            if not is_local:
                rawtx = rawtxid[0]
            decodedtx = handle_rpc(cp.decoderawtransaction, [str(rawtx)])
            if decodedtx[2] == 200 or decodedtx[2] == 0:
                txdetail = json.loads(decodedtx[0])
                for vin in txdetail.get('vin'):
                    if vin.get('coinbase'):
                        timestmp = datetime.fromtimestamp(txdetail.get('locktime')).date()
                        amount = txdetail.get('vout')[0].get('value')
                        return timestmp, amount
                    else:
                        return None, None
            else:
                return None, None
        else:
            return None, None

class Autoinstall(QtCore.QObject):
    out_text = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super(Autoinstall, self).__init__()
        self.mcl_download_url = api_request.latest_marmara_download_url()
        self.mcl_linux_zipname = 'MCL-linux.zip'
        self.mcl_win_zipname = 'MCL-win.zip'
        self.linux_command_list = ['sudo apt-get update', 'sudo apt-get install libgomp1 -y',
                                   'wget ' + str(self.mcl_download_url) + '/' + self.mcl_linux_zipname +
                                   " -O " + self.mcl_linux_zipname, 'sudo apt-get install unzip -y',
                                   'unzip -o MCL-linux.zip', 'sudo chmod +x komodod komodo-cli fetch-params.sh',
                                   './fetch-params.sh']

        self.win_command_list = ['mkdir marmara',
                                 'curl -L ' + str(self.mcl_download_url) + '/' + self.mcl_win_zipname +
                                 " > " + self.mcl_win_zipname, 'PowerShell Expand-Archive .\MCL-win.zip . -Force',
                                 'fetch-params.bat']
        self.sudo_password = ""
        self.input_list = None

    def set_password(self, password):
        self.sudo_password = password

    def set_input_list(self, value):
        self.input_list = value

    @pyqtSlot()
    def start_install(self):
        if is_local:
            if platform.system() == 'Linux':
                self.out_text.emit(str("installing on linux"))
                self.linux_install()
            if platform.system() == 'Windows':
                self.windows_install()
        else:
            self.out_text.emit(str("installing on linux"))
            self.linux_install()

    def linux_install(self):
        self.out_text.emit(str("update linux"))
        i = 0
        while True:
            cmd = self.linux_command_list[i]
            if cmd.startswith('sudo'):
                cmd = 'sudo -k -S -- ' + cmd + '\n'
            logging.info(cmd)
            if is_local:
                proc = subprocess.Popen(cmd, cwd=str(pathlib.Path.home()), shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if cmd.startswith('sudo'):
                    proc.stdin.write(bytes(self.sudo_password + '\n', encoding='utf-8'))
                    proc.stdin.flush()
                while not proc.stdout.closed:
                    out = proc.stdout.readline().decode()
                    self.out_text.emit(out)
                    if out.find('Sorry, try again.') > 0:
                        logging.warning('wrong password')
                        proc.stdout.close()
                        i = len(self.linux_command_list)
                    if not out:
                        proc.stdout.close()
                exit_status = proc.poll()
                logging.info('exit_status  :' + str(exit_status))
                proc.terminate()
                i = i + 1
                if i >= len(self.linux_command_list):
                    self.progress.emit(int(i * 14))
                    break
            else:
                sshclient = remote_connection.server_ssh_connect()
                session = sshclient.get_transport().open_session()
                stdin = session.makefile_stdin('wb', -1)
                stdout = session.makefile('rb', -1)
                session.exec_command(cmd)
                if cmd.startswith('sudo'):
                    stdin.write(remote_connection.server_password + '\n')
                    stdin.flush()
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        out = stdout.channel.recv(65535).decode()
                        time.sleep(2)
                        logging.info(str(out))
                        self.out_text.emit(str(out))
                    if stdout.channel.recv_stderr_ready():
                        time.sleep(2)
                        err = stdout.channel.recv_stderr(65535).decode()
                        self.out_text.emit(str(err))
                        logging.error(str(err))
                exit_status = session.recv_exit_status()  # Blocking call
                logging.info(exit_status)
                session.close()
                sshclient.close()
                i = i + 1
            if exit_status == 0:
                self.progress.emit(int(i * 14))
            else:
                self.out_text.emit('Something Went Wrong ' + cmd)
                self.finished.emit()
                break
        self.finished.emit()

    def windows_install(self):
        self.out_text.emit(str("installing on windows"))
        i = 0
        while True:
            cmd = self.win_command_list[i]
            self.out_text.emit(cmd)
            if i == 0:
                cwd = str(pathlib.Path.home())
                if os.path.isdir(cwd + '\marmara'):
                    cwd = cwd + '\marmara'
                    i = 1
                    cmd = self.win_command_list[i]
                    self.progress.emit(10)
            else:
                cwd = str(pathlib.Path.home()) + '\marmara'
            logging.info(cwd)
            proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while not proc.stdout.closed:
                out = proc.stdout.readline()
                try:
                    out_d = out.decode()
                except:
                    out_d = '*-*-'
                self.out_text.emit(out_d)
                if not out:
                    proc.stdout.close()
            exit_status = proc.poll()
            logging.info('exit_status  ' + str(exit_status))
            proc.terminate()
            i = i + 1
            if i >= len(self.win_command_list):
                self.progress.emit(int(i * 24))
                break
            if exit_status == 0 or exit_status is None:
                self.progress.emit(int(i * 24))
            else:
                self.out_text.emit('Something Went Wrong ' + cmd)
                self.finished.emit()
                break
        self.finished.emit()
        # update = subprocess.Popen

    @pyqtSlot()
    def update_chain(self):
        if is_local:
            self.local_chain_update()
        if not is_local:
            self.remote_chain_update()

    def local_chain_update(self):
        cmd_list = None
        if platform.system() == 'Linux':
            cmd_list = ['wget ' + str(self.mcl_download_url) + '/' + self.mcl_linux_zipname + " -O " +
                        self.mcl_linux_zipname, 'unzip -o ' + self.mcl_linux_zipname]
        if platform.system() == 'Windows':
            cmd_list = [self.win_command_list[1], self.win_command_list[2]]
        if cmd_list:
            for cmd in cmd_list:
                proc = subprocess.Popen(cmd, cwd=marmara_path, shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while not proc.stdout.closed:
                    out = proc.stdout.readline()
                    try:
                        out_d = out.decode().replace('\n', '')
                    except Exception as e:
                        out_d = e
                    logging.info(out_d)
                    self.out_text.emit(out_d)
                    if not out:
                        proc.stdout.close()
                exit_status = proc.poll()
                logging.info('exit_status  ' + str(exit_status))
                proc.terminate()
            self.finished.emit()

    def remote_chain_update(self):
        cmd_list = ['curl -L ' + str(self.mcl_download_url) + '/' + self.mcl_linux_zipname + ' > ' + marmara_path +
                    self.mcl_linux_zipname, 'unzip -o ' + marmara_path + self.mcl_linux_zipname + ' -d ' + marmara_path]
        sshclient = remote_connection.server_ssh_connect()
        for cmd in cmd_list:
            session = sshclient.get_transport().open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            session.exec_command(cmd)
            stdout = session.makefile('rb', -1)
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    out = stdout.channel.recv(65535)
                    try:
                        out_d = out.decode()
                    except Exception as e:
                        out_d = e
                    logging.info(str(out_d))
                    self.out_text.emit(str(out_d))
                else:
                    time.sleep(1)
            exit_status = session.recv_exit_status()  # Blocking call
            logging.info(exit_status)
            session.close()
        self.finished.emit()
        sshclient.close()

    def fetch_params_install(self):
        cmd_lst = []
        if is_local:
            if platform.system() == 'Win64' or platform.system() == 'Windows':
                if self.input_list:
                    for file in self.input_list:
                        cmd_lst.append('del ' + zcash_path + str(file).replace('/', '\\'))
                cmd_lst.append(marmara_path + 'fetch-params.bat')
            if platform.system() == 'Linux':
                if self.input_list:
                    for file in self.input_list:
                        cmd_lst.append('rm ' + zcash_path + file)
                cmd_lst.append(marmara_path + 'fetch-params.sh')
            for cmd in cmd_lst:
                self.out_text.emit(cmd)
                proc = subprocess.Popen(cmd, cwd=str(pathlib.Path.home()), shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while not proc.stdout.closed:
                    out = proc.stdout.readline()
                    try:
                        out_d = out.decode().replace('\n', '')
                    except Exception as e:
                        out_d = e
                    logging.info(out_d)
                    self.out_text.emit(out_d)
                    if not out:
                        proc.stdout.close()
                exit_status = proc.poll()
                logging.info('exit_status  ' + str(exit_status))
                proc.terminate()
            self.finished.emit()
        if not is_local:
            if self.input_list:
                for file in self.input_list:
                    cmd_lst.append('rm ' + zcash_path + file)
            cmd_lst.append(marmara_path + 'fetch-params.sh')
            sshclient = remote_connection.server_ssh_connect()
            for cmd in cmd_lst:
                session = sshclient.get_transport().open_session()
                session.set_combine_stderr(True)
                session.get_pty()
                session.exec_command(cmd)
                stdout = session.makefile('rb', -1)
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        out = stdout.channel.recv(65535)
                        try:
                            out_d = out.decode()
                        except Exception as e:
                            out_d = e
                        logging.info(str(out_d))
                        self.out_text.emit(str(out_d))
                    else:
                        time.sleep(1)
                exit_status = session.recv_exit_status()  # Blocking call
                logging.info(exit_status)
                session.close()
            self.finished.emit()
            sshclient.close()


class ApiWorker(QtCore.QObject):
    out_list = pyqtSignal(list)
    out_dict = pyqtSignal(dict)
    out_err = pyqtSignal(str)
    out_str = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super(ApiWorker, self).__init__()
        self.api_key = ""

    @pyqtSlot(str)
    def set_api_key(self, key):
        self.api_key = key

    @pyqtSlot()
    def exchange_api_run(self):
        mcl_market_values = api_request.mcl_exchange_market(self.api_key)
        self.out_list.emit(mcl_market_values)
        self.finished.emit()

    @pyqtSlot()
    def mcl_stats_api(self):
        mcl_stats = api_request.get_marmara_stats()
        if type(mcl_stats) is dict:
            self.out_dict.emit(mcl_stats)
        if type(mcl_stats) is str:
            self.out_err.emit(mcl_stats)
        self.finished.emit()

    @pyqtSlot()
    def mcl_update_check(self):
        tag_name = api_request.git_request_tag(api_request.marmara_api_url)
        if type(tag_name) is str:
            self.out_str.emit(tag_name)
            self.finished.emit()
        else:
            self.out_err.emit('Connection Error')
            self.finished.emit()

    @pyqtSlot()
    def app_ver_check(self):
        latest_app_tag = api_request.git_request_tag(api_request.app_api_url)
        latest_app_version = api_request.latest_app_release_url()
        if latest_app_tag == 'Connection Error' or latest_app_version == 'Connection Error':
            self.out_err.emit('Connection Error')
            self.finished.emit()
        else:
            out_list = [latest_app_tag, latest_app_version]
            self.out_list.emit(out_list)
            self.finished.emit()
