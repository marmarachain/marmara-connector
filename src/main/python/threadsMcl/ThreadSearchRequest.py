from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class SearchRequest(QThread):
    change_value_information_loop_details = pyqtSignal(str)

    command_mcl_credit_loop_search = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22
    coun=0

    def run(self):
        self.details()

    def details(self):
        print(self.coun)
        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_credit_loop_search)
        stdout = ssh.command(self.command_mcl_credit_loop_search)
        lines = stdout.readlines()
        print(lines)
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        self.coun=self.coun+1
        self.change_value_information_loop_details.emit(out_)
