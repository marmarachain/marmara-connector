import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect


class CreateWalletAdressConvertpassphrase(QThread):
    change_value_information_pubkey = pyqtSignal(str)
    change_value_information_adress = pyqtSignal(str)
    change_value_information_privkey = pyqtSignal(str)
    change_value_information_getinfo_check_chain_with_pubkey = pyqtSignal(str)

    command_mcl_start_chain_without_pubkey = ""
    command_mcl_get_info = ""
    command_mcl_create_convertpassphrase = ""
    command_mcl_import_private_Key = ""

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
            stdout = ssh.command(self.self.command_mcl_start_chain_without_pubkey)

            print("Başlangıç Çıktı")
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
        print(self.command_mcl_create_convertpassphrase)
        stdout = ssh.command(self.command_mcl_create_convertpassphrase)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        convertpassphrase_out= json.loads(out_)

        print(self.command_mcl_import_private_Key + convertpassphrase_out["wif"])
        stdout = ssh.command(self.command_mcl_import_private_Key + convertpassphrase_out["wif"])
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_adress.emit(convertpassphrase_out["address"])
        self.change_value_information_pubkey.emit(convertpassphrase_out["pubkey"])
        self.change_value_information_privkey.emit(convertpassphrase_out["wif"])
        print("THREAD BİTTİ")