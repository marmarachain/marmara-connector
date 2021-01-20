import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class AllWallet(QThread):
    change_value_information_wallet = pyqtSignal(str)

    command_mcl_all_wallet_list = ""
    command_mcl_get_pubkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.accept()

    def accept(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_all_wallet_list)
        stdout = ssh.command(self.command_mcl_all_wallet_list)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        y = json.loads(out_)

        wallets = []

        print("=========")
        print(len(y))
        for w in y:
            try:
                print(w)
                wallets.append(w)
                stdout = ssh.command(self.command_mcl_get_pubkey + w)
                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                wallet_info = json.loads(out_)
                print(wallet_info["pubkey"])
                wallet_and_pubkey = w + "," + wallet_info["pubkey"]
                self.change_value_information_wallet.emit(wallet_and_pubkey)

                print("----------")
                time.sleep(0.5)
            except:
                self.change_value_information_wallet.emit("0")
                print("stopped chain")
                break
        self.change_value_information_wallet.emit("0")
