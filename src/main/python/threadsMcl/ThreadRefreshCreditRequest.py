import json
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class RefreshCreditRequest(QThread):
    change_value_information = pyqtSignal(str)

    command_mcl_credit_request_list = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.refreshRequest()

    def refreshRequest(self):

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_credit_request_list)
        stdout = ssh.command(self.command_mcl_credit_request_list)
        lines = stdout.readlines()
        out_ = ""

        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)

        self.change_value_information.emit(out_)
