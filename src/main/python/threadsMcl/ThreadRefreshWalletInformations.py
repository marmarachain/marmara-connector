from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class RefreshWalletInformations(QThread):

    change_value_information_get_marmara_info = pyqtSignal(str)
    command_mcl_get_marmara_info = ""

    pubkey = ""
    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.refreshInfo()

    def refreshInfo(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        # ---------------------------------------------------------------
        # Get Marmara
        print(self.command_mcl_get_marmara_info + self.pubkey)
        stdout = ssh.command(self.command_mcl_get_marmara_info + self.pubkey)
        print("Marmara Info")
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        print(out_)
        self.change_value_information_get_marmara_info.emit(out_)
