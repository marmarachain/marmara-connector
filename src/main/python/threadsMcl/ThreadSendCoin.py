from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class SendCoin(QThread):
    change_value_information_txid = pyqtSignal(str)

    command_mcl_send_coin = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.sendCoin()

    def sendCoin(self):

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_send_coin)
        stdout = ssh.command(self.command_mcl_send_coin)
        lines = stdout.readlines()
        out_ = ""

        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        out_ = out_.strip()

        self.change_value_information_txid.emit(out_)
