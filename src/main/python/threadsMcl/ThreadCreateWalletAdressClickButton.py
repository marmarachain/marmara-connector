import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class CreateWalletAdressClickButton(QThread):
    change_value_information_pubkey = pyqtSignal(str)
    change_value_information_adress = pyqtSignal(str)
    change_value_information_privkey = pyqtSignal(str)
    change_value_information_getinfo_check_chain_with_pubkey = pyqtSignal(str)

    command_mcl_start_chain_without_pubkey = ""
    command_mcl_get_info = ""
    command_mcl_create_wallet_adress = ""
    command_mcl_get_pubkey = ""
    command_mcl_get_privkey = ""


    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.startChainForCreatingWallet()

    def startChainForCreatingWallet(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        print(self.command_mcl_get_info)
        stdout = ssh.command(self.command_mcl_get_info)
        lines = stdout.readlines()
        print("Get Info")
        print(lines)
        print("Get Info Bitti")
        print("-------")

        if not lines:
            print("Zincir Çalışmıyor")
            time.sleep(1)

            print(self.command_mcl_start_chain_without_pubkey)
            stdout = ssh.command(self.command_mcl_start_chain_without_pubkey)
            print(stdout)

            while True:
                print(self.command_mcl_get_info)
                stdout = ssh.command(self.command_mcl_get_info)
                lines = stdout.readlines()
                print("Get Info")
                print(lines)
                print("Get Info Bitti")
                print("-------")

                if not lines:
                    print("Zincir Çalışmıyor")
                    time.sleep(1)
                else:
                    print("Zincir çalışıyor.")
                    # --------------------------------------------------
                    # Get New Adress
                    out_ = ""
                    for deger in lines:
                        deger = deger.split("\n")
                        out_ = out_ + " " + deger[0]
                    break
        else:
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]

        self.change_value_information_getinfo_check_chain_with_pubkey.emit(out_)

        # ---------------------------------------------------------------
        # Get Adress
        print(self.command_mcl_create_wallet_adress)
        stdout = ssh.command(self.command_mcl_create_wallet_adress)
        lines = stdout.readlines()
        adress_ = ""
        for deger in lines:
            deger = deger.split("\n")
            adress_ = adress_ + " " + deger[0]
        self.change_value_information_adress.emit(adress_)

        # ---------------------------------------------------------------
        # Get Privkey
        command_getprivkey = self.command_mcl_get_privkey + adress_
        print(self.command_mcl_get_privkey + adress_)
        stdout = ssh.command(self.command_mcl_get_privkey + adress_)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        print(out_)
        self.change_value_information_privkey.emit(out_)

        # ---------------------------------------------------------------
        # Get Pubkey
        print(self.command_mcl_get_pubkey + " " + adress_)
        stdout = ssh.command(self.command_mcl_get_pubkey + " " + adress_)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        y = json.loads(out_)
        print(y["pubkey"])

        self.change_value_information_pubkey.emit(y["pubkey"])
        print("THREAD BİTTİ")