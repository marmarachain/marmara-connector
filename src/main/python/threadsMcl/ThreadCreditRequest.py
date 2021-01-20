import json
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class CreditRequest(QThread):

    change_value_information_credit_request = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_credit_request = ""
    command_mcl_credit_request_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.request()

    def request(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_credit_request)
        stdout = ssh.command(self.command_mcl_credit_request)
        lines = stdout.readlines()
        print(lines)
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)


        try:
            y = json.loads(out_)
            print(y["result"])

            if y["result"] == "success":
                print(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")
                stdout = ssh.command(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")

                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]
                print(out_)
                self.change_value_information_get_transactionID.emit(out_)
                self.change_value_information_credit_request.emit(True)
            else:
                self.change_value_information_credit_request.emit(False)
        except:
            self.change_value_information_credit_request.emit(False)
