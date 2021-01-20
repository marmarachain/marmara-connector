import json
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class UnlockCoin(QThread):
    change_value_information_get_unlock = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_unlock_coin = ""
    command_mcl_unlock_coin_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.unlockCoin()

    def unlockCoin(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_unlock_coin)
        stdout = ssh.command(self.command_mcl_unlock_coin)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]


        print("Get Info Bitti")
        print("-------")
        print(out_)

        out_ = out_.strip()


        try:
           y = json.loads(out_)
           tmp=y["result"]
           self.change_value_information_get_unlock.emit(False)

        except:
            # Hex Onay
            # ---------------------------------------------------------------

            print(self.command_mcl_unlock_coin_sendrawtransaction + "\"" + out_ + "\"")
            stdout = ssh.command(self.command_mcl_unlock_coin_sendrawtransaction + "\"" + out_ + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_get_unlock.emit(True)
