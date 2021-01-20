import time
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class StopChain(QThread):
    change_value_did_run_chain = pyqtSignal(bool)

    command_mcl_stop_chain = ""
    command_mcl_get_info = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.stopChain()

    def stopChain(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_stop_chain)
        stdout = ssh.command(self.command_mcl_stop_chain)
        print("STOP")
        lines = stdout.readlines()
        out_ = ""
        print(lines)
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        print(out_)
        print("STOP Bitti")
        print("-------")

        while True:
            print(self.command_mcl_get_info)
            stdout = ssh.command(self.command_mcl_get_info)
            lines = stdout.readlines()
            print("Get Info")
            print(lines)
            print("Get Info Bitti")
            print("-------")

            if not lines:
                time.sleep(10)
                self.change_value_did_run_chain.emit(False)
                print("Zincir Çalışmıyor")
                break
        print("THREAD BİTTİ")
