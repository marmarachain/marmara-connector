from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class ShowPrivateKey(QThread):
    change_value_information_privkey = pyqtSignal(str)

    command_mcl_get_privkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.getPrivateKey()

    def getPrivateKey(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        # ---------------------------------------------------------------
        # Get Privkey
        command_getprivkey = self.command_mcl_get_privkey
        print(self.command_mcl_get_privkey)
        stdout = ssh.command(self.command_mcl_get_privkey)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        print(out_)
        self.change_value_information_privkey.emit(out_)
