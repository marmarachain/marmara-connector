import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect



class ImportPrivkey(QThread):

    change_value_information_get_wallet = pyqtSignal(str)
    change_value_information_get_pubkey = pyqtSignal(str)

    command_mcl_import_privkey = ""
    command_mcl_get_pubkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.importPrivkey()

    def importPrivkey(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        #----------------------------------------------
        #Import Privkey and Get Wallet Address
        print(self.command_mcl_import_privkey)
        stdout = ssh.command(self.command_mcl_import_privkey)
        print("^^^^^^^^")
        print(stdout)
        lines = stdout.readlines()
        print(lines)
        if 0 == len(lines):
            self.change_value_information_get_wallet.emit("")
            self.change_value_information_get_pubkey.emit("")
        else:
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]

            self.change_value_information_get_wallet.emit(out_)

            #----------------------------------------------
            #Get Pubkey
            print(self.command_mcl_get_pubkey +" "+out_)
            stdout = ssh.command(self.command_mcl_get_pubkey +" "+out_)
            print("^^^^^^^")
            print(stdout)
            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]

            wallet_info = json.loads(out_)
            print(wallet_info["pubkey"])
            self.change_value_information_get_pubkey.emit(wallet_info["pubkey"])
