import json
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class LockCoin(QThread):
    change_value_information_get_lock = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_lock_coin = ""
    command_mcl_lock_coin_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.lockCoin()

    def lockCoin(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print("bağlantı tamam.")
        print(self.command_mcl_lock_coin)
        stdout = ssh.command(self.command_mcl_lock_coin)
        print("Get Info")
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]


        print("Get Info Bitti")
        print("-------")

        print(out_)
        y = json.loads(out_)
        print(y["result"])

        if y["result"] == "success":

            # ---------------------------------------------------------------
            # Hex Onay

            print(self.command_mcl_lock_coin_sendrawtransaction + "\"" + y["hex"] + "\"")
            stdout = ssh.command(self.command_mcl_lock_coin_sendrawtransaction + "\"" + y["hex"] + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_get_lock.emit(True)
        else:
            self.change_value_information_get_lock.emit(False)
