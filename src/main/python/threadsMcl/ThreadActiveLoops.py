import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect

class ActiveLoops(QThread):
    change_value_information = pyqtSignal(str)

    command_mcl_marmara_info = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.details()

    def details(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_marmara_info)
        stdout = ssh.command(self.command_mcl_marmara_info)
        lines = stdout.readlines()
        print(lines)
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information.emit(out_)
