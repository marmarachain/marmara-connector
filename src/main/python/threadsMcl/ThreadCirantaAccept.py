import json
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class CirantaAccept(QThread):

    change_value_information_accept = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_ciranta_request_accept = ""
    command_mcl_credit_request_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.accept()

    def accept(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_ciranta_request_accept)
        stdout = ssh.command(self.command_mcl_ciranta_request_accept)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        y = json.loads(out_)

        print(y["result"])


        # Hex Onay
        # ---------------------------------------------------------------
        if y["result"] == "success":
            print(y["hex"])
            print(y["requesttxid"])
            print(y["receiverpk"])

            print(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")
            stdout = ssh.command(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_accept.emit(True)
        else:
            self.change_value_information_accept.emit(False)
