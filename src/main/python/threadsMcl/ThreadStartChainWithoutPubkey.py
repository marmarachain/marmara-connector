import json
import time
from PyQt5.QtCore import QThread, pyqtSignal
from threadsMcl.Connection import ServerConnect



class StartChainWithoutPubkey(QThread):

    change_value_information_getinfo_check_chain_with_pubkey = pyqtSignal(str)
    change_value_information_wallet = pyqtSignal(str)

    command_mcl_start_chain_without_pubkey = ""
    command_mcl_get_info = ""

    command_mcl_all_wallet_list = ""
    command_mcl_get_pubkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.startChainWithoutPubkey()

    def startChainWithoutPubkey(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")
        print(self.command_mcl_start_chain_without_pubkey)
        __= ssh.command(self.command_mcl_start_chain_without_pubkey)

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
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                self.change_value_information_getinfo_check_chain_with_pubkey.emit(out_)

                # ---------------------------------------------------------------
                print(self.command_mcl_all_wallet_list)
                stdout = ssh.command(self.command_mcl_all_wallet_list)
                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                print(out_)
                y = json.loads(out_)

                wallets = []

                for w in y:
                    try:
                        print(w)
                        wallets.append(w)
                        stdout = ssh.command(self.command_mcl_get_pubkey + w)
                        lines = stdout.readlines()
                        out_ = ""
                        for deger in lines:
                            deger = deger.split("\n")
                            out_ = out_ + " " + deger[0]

                        wallet_info = json.loads(out_)
                        print(wallet_info["pubkey"])
                        wallet_and_pubkey = w + "," + wallet_info["pubkey"]
                        self.change_value_information_wallet.emit(wallet_and_pubkey)
                        print("----------")
                        time.sleep(0.3)
                    except:
                        self.change_value_information_wallet.emit("0")
                        print("stopped chain")
                        break
                self.change_value_information_wallet.emit("0")
                break
        print("THREAD BİTTİ")
