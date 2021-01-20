import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class FirstRefreshInformations(QThread):

    change_value_information_get_info = pyqtSignal(str)
    change_value_information_get_marmara_info = pyqtSignal(str)
    change_value_information_get_generate = pyqtSignal(str)
    change_value_did_run_chain = pyqtSignal(bool)

    command_mcl_get_info = ""
    command_mcl_get_marmara_info = ""
    command_mcl_get_wallet_list = ""
    command_mcl_get_stacking_and_mining = ""

    pubkey = ""
    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.refreshInfo()

    def refreshInfo(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        print(self.command_mcl_get_info)
        stdout = ssh.command(self.command_mcl_get_info)
        lines = stdout.readlines()
        print("Get Info")
        print(lines)
        print("Get Info Bitti")
        print("-------")

        # --------------------------------------------------
        # Get info
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        self.change_value_information_get_info.emit(out_)

        # ---------------------------------------------------------------
        # Get Marmara
        command_marmara_info = self.command_mcl_get_marmara_info + self.pubkey
        print(self.command_mcl_get_marmara_info + self.pubkey)
        stdout = ssh.command(self.command_mcl_get_marmara_info + self.pubkey)
        print("Marmara Info")
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_get_marmara_info.emit(out_)

        # ---------------------------------------------------------------
        # Get Generate
        print(self.command_mcl_get_stacking_and_mining)
        stdout = ssh.command(self.command_mcl_get_stacking_and_mining)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_get_generate.emit(out_)
        self.change_value_did_run_chain.emit(True)

