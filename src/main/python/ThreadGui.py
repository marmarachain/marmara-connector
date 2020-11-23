import json
import time
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal
from Connection import ServerConnect


class AutoInstall(QThread):
    change_value_text_edit = pyqtSignal(str)
    change_value_progressbar = pyqtSignal(int)

    withBootstrap = True
    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.mcl_install_connect_ssh()

    def mcl_install_connect_ssh(self):
        print("Sunucya bağlanmak için bilgiler alindi.")
        self.change_value_text_edit.emit(str("Get Info..."))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.server_hostname, self.server_port, self.server_username, self.server_password)
        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()

        print("bağlantı tamam.")
        self.change_value_text_edit.emit(str("Connection ok."))
        self.change_value_progressbar.emit(2)

        #Install Lib
        self.change_value_text_edit.emit(str("Installing some libs..."))

        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("sudo apt-get install libgomp1")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(self.server_password + '\n')
        stdin.write("yes" + '\n')
        stdin.write("yes" + '\n')

        self.change_value_text_edit.emit("Install depends...")
        for line in stdout:
            print(line.rstrip())
            # self.change_value_text_edit.emit(str(line.rstrip()))
            # stdin.write("yes" + '\n')

        print("Downloaded depends.")
        self.change_value_text_edit.emit(str("*** Downloaded Depends. ***"))
        self.change_value_progressbar.emit(7)

        # Install mcl zip in remote server
        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("wget http://marmara.io/guifiles/MCL-linux.zip -O MCL-linux.zip")
        # stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)

        for line in stdout:
            print(line.rstrip())
            self.change_value_text_edit.emit(str(line.rstrip()))

        self.change_value_text_edit.emit(str("** Installed ZIP. ***"))
        self.change_value_progressbar.emit(8)

        # Install unzip in remote server
        print("Installing Unzip...")
        self.change_value_text_edit.emit(str("Installing Unzip..."))

        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("sudo apt install unzip")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(self.server_password + '\n')
        stdin.write("yes" + '\n')

        for line in stdout:
            print(line.rstrip())
            self.change_value_text_edit.emit("Unzip ....")

        print("Unzip İndirildi.")
        self.change_value_text_edit.emit(str("*** Installed Unzip ***"))
        self.change_value_progressbar.emit(15)

        # Unzip mcl zip file in remote server
        print("İndirilen dosya zipten çıkartılıyor.")
        self.change_value_text_edit.emit(str("Extracting Files..."))

        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("unzip MCL-linux.zip")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write("A" + '\n')

        for line in stdout:
            print(line.rstrip())
            self.change_value_text_edit.emit(str(line.rstrip()))

        print("Zipten Çıkarıldı")
        self.change_value_text_edit.emit("Extracted Files.")
        self.change_value_progressbar.emit(22)

        # Set sermission mcl files
        print("İzinler Ayarlanılıyor...")
        self.change_value_text_edit.emit("Setting permissions...")

        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("sudo chmod +x komodod komodo-cli fetch-params.sh")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write(self.server_password + '\n')
        stdin.write("yes" + '\n')

        for line in stdout:
            print(line.rstrip())
            self.change_value_text_edit.emit("setting permissions...")

        self.change_value_progressbar.emit(25)

        # Run fetch parameters in remote server
        print("Fetch Parametrs Çalıştırıldı...")
        self.change_value_text_edit.emit("Running Fetch Parameters...")

        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command("./fetch-params.sh")
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.write("yes" + '\n')

        count_ = 0
        for line in stdout:
            count_ = count_ + 1
            print(line.rstrip())
            self.change_value_text_edit.emit(str(line.rstrip()))
            if count_ == 20:
                self.change_value_progressbar.emit(33)
            elif count_ == 50:
                self.change_value_progressbar.emit(47)
            elif count_ == 65:
                self.change_value_progressbar.emit(65)

        self.change_value_progressbar.emit(67)

        print("Fetch Parametrs bitti...")
        self.change_value_text_edit.emit("Finished Fetch Parameters.")

        stdin.flush()

        print("DONE")

        if self.withBootstrap:
            session = ssh.get_transport().open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            session.exec_command("wget https://eu.bootstrap.dexstats.info/MCL-bootstrap.tar.gz -O MCL-bootstrap.tar.gz")
            stdout = session.makefile('rb', -1)

            for line in stdout:
                print(line.rstrip())
                self.change_value_text_edit.emit(str(line.rstrip()))

            self.change_value_progressbar.emit(78)

            session = ssh.get_transport().open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            session.exec_command("mkdir -p ~/.komodo/MCL")
            session.makefile('rb', -1)

            session = ssh.get_transport().open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            session.exec_command("tar -xvf MCL-bootstrap.tar.gz -C .komodo/MCL")
            stdout = session.makefile('rb', -1)

            for line in stdout:
                print(line.rstrip())
                self.change_value_text_edit.emit(str(line.rstrip()))

        self.change_value_text_edit.emit("**********")
        self.change_value_text_edit.emit("**DONE**")
        self.change_value_text_edit.emit("**********")
        self.change_value_progressbar.emit(100)


class CreateWalletAdressAfterInstall(QThread):
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
        print(self.command_mcl_start_chain_without_pubkey)
        stdout = ssh.command(self.command_mcl_start_chain_without_pubkey)

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
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                self.change_value_information_getinfo_check_chain_with_pubkey.emit(out_)

                # ---------------------------------------------------------------
                # Get Adress
                print(self.command_mcl_create_wallet_adress)
                stdout = ssh.command(self.self.command_mcl_create_wallet_adress)
                lines = stdout.readlines()
                adress_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    adress_ = adress_ + " " + deger[0]
                self.change_value_information_adress.emit(adress_)

                # ---------------------------------------------------------------
                # Get Privkey
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
                stdout = ssh.command(self.command_mcl_get_privkey + adress_)
                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                y = json.loads(out_)
                print(y["pubkey"])

                self.change_value_information_pubkey.emit(y["pubkey"])
                break
        print("THREAD BİTTİ")


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


class StartChain(QThread):
    change_value_information_get_info = pyqtSignal(str)
    change_value_information_get_marmara_info = pyqtSignal(str)
    change_value_information_get_generate = pyqtSignal(str)
    change_value_did_run_chain = pyqtSignal(bool)

    command_mcl_start_chain = ""
    command_mcl_get_info = ""
    command_mcl_get_marmara_info = ""
    command_mcl_get_stacking_and_mining = ""

    pubkey = ""
    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.startChain()

    def startChain(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        print(self.command_mcl_start_chain + self.pubkey)
        stdout = ssh.command(self.command_mcl_start_chain + self.pubkey)

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
                self.change_value_did_run_chain.emit(False)
                print("Zincir Çalışmıyor")
                time.sleep(1)
            else:

                self.is_chain_run = True
                print("Zincir çalışıyor.")
            # --------------------------------------------------
                #Get info
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]
                self.change_value_information_get_info.emit(out_)

            # ---------------------------------------------------------------
                #Get Marmara
                print(self.command_mcl_get_marmara_info + self.pubkey)
                stdout = ssh.command(self.command_mcl_get_marmara_info + self.pubkey)
                print("Marmara Info")
                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                self.change_value_information_get_marmara_info.emit(out_)

            # ---------------------------------------------------------------
                # Get Generate
                print(self.command_mcl_get_stacking_and_mining)
                stdout = ssh.command(self.command_mcl_get_stacking_and_mining)
                lines = stdout.readlines()
                out_ = ""
                for deger in lines:
                    deger = deger.split("\n")
                    out_ = out_ + " " + deger[0]

                self.change_value_information_get_generate.emit(out_)
                self.change_value_did_run_chain.emit(True)
                break

        print("THREAD BİTTİ")


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


class RefreshInformations(QThread):

    change_value_information_get_info = pyqtSignal(str)
    change_value_information_get_generate = pyqtSignal(str)
    change_value_did_run_chain = pyqtSignal(bool)

    command_mcl_get_info = ""
    command_mcl_get_wallet_list = ""
    command_mcl_get_stacking_and_mining = ""

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

        print(self.command_mcl_get_info)
        stdout = ssh.command(self.command_mcl_get_info)
        lines = stdout.readlines()
        print("Get Info")
        print(lines)
        print("Get Info Bitti")
        print("-------")

        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        self.change_value_information_get_info.emit(out_)

        # ---------------------------------------------------------------
        # Get Generate
        print(self.command_mcl_get_stacking_and_mining)
        stdout = ssh.command(self.command_mcl_get_stacking_and_mining)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_get_generate.emit(out_)
        self.change_value_did_run_chain.emit(True)


class FirstRefreshInformations(QThread):

    change_value_information_get_info = pyqtSignal(str)
    change_value_information_get_marmara_info = pyqtSignal(str)
    change_value_information_get_generate = pyqtSignal(str)
    change_value_did_run_chain = pyqtSignal(bool)

    command_mcl_get_info = ""
    command_mcl_get_marmara_info = ""
    command_mcl_get_wallet_list = ""
    command_mcl_get_stacking_and_mining = ""

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
        print("bağlantı tamam.")

        print(self.command_mcl_get_info)
        stdout = ssh.command(self.command_mcl_get_info)
        lines = stdout.readlines()
        print("Get Info")
        print(lines)
        print("Get Info Bitti")
        print("-------")

        # --------------------------------------------------
        # Get info
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]
        self.change_value_information_get_info.emit(out_)

        # ---------------------------------------------------------------
        # Get Marmara
        command_marmara_info = self.command_mcl_get_marmara_info + self.pubkey
        print(self.command_mcl_get_marmara_info + self.pubkey)
        stdout = ssh.command(self.command_mcl_get_marmara_info + self.pubkey)
        print("Marmara Info")
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_get_marmara_info.emit(out_)

        # ---------------------------------------------------------------
        # Get Generate
        print(self.command_mcl_get_stacking_and_mining)
        stdout = ssh.command(self.command_mcl_get_stacking_and_mining)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information_get_generate.emit(out_)
        self.change_value_did_run_chain.emit(True)


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


class LockCoin(QThread):
    change_value_information_get_lock = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_lock_coin = ""
    command_mcl_lock_coin_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.lockCoin()

    def lockCoin(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print("bağlantı tamam.")
        print(self.command_mcl_lock_coin)
        stdout = ssh.command(self.command_mcl_lock_coin)
        print("Get Info")
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]


        print("Get Info Bitti")
        print("-------")

        print(out_)
        y = json.loads(out_)
        print(y["result"])

        if y["result"] == "success":

            # ---------------------------------------------------------------
            # Hex Onay

            print(self.command_mcl_lock_coin_sendrawtransaction + "\"" + y["hex"] + "\"")
            stdout = ssh.command(self.command_mcl_lock_coin_sendrawtransaction + "\"" + y["hex"] + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_get_lock.emit(True)
        else:
            self.change_value_information_get_lock.emit(False)


class UnlockCoin(QThread):
    change_value_information_get_unlock = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_unlock_coin = ""
    command_mcl_unlock_coin_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.unlockCoin()

    def unlockCoin(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_unlock_coin)
        stdout = ssh.command(self.command_mcl_unlock_coin)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]


        print("Get Info Bitti")
        print("-------")
        print(out_)

        out_ = out_.strip()


        try:
           y = json.loads(out_)
           tmp=y["result"]
           self.change_value_information_get_unlock.emit(False)

        except:
            # Hex Onay
            # ---------------------------------------------------------------

            print(self.command_mcl_unlock_coin_sendrawtransaction + "\"" + out_ + "\"")
            stdout = ssh.command(self.command_mcl_unlock_coin_sendrawtransaction + "\"" + out_ + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_get_unlock.emit(True)


class SendCoin(QThread):
    change_value_information_txid = pyqtSignal(str)

    command_mcl_send_coin = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.sendCoin()

    def sendCoin(self):

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_send_coin)
        stdout = ssh.command(self.command_mcl_send_coin)
        lines = stdout.readlines()
        out_ = ""

        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        out_ = out_.strip()

        self.change_value_information_txid.emit(out_)


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


class CreditAccept(QThread):

    change_value_information_accept = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_credit_request_accept = ""
    command_mcl_credit_request_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.accept()

    def accept(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_credit_request_accept)
        stdout = ssh.command(self.command_mcl_credit_request_accept)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        y = json.loads(out_)

        print(y["result"])


        # Hex Onay
        # ---------------------------------------------------------------
        if y["result"] == "success":
            print(y["hex"])
            print(y["requesttxid"])
            print(y["receiverpk"])

            print(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")
            stdout = ssh.command(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_accept.emit(True)
        else:
            self.change_value_information_accept.emit(False)


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


class SearchHolders(QThread):
    change_value_information = pyqtSignal(str)

    command_mcl_marmara_holders = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.details()

    def details(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_marmara_holders)
        stdout = ssh.command(self.command_mcl_marmara_holders)
        lines = stdout.readlines()
        print(lines)
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        self.change_value_information.emit(out_)


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


class CirantaAccept(QThread):

    change_value_information_accept = pyqtSignal(bool)
    change_value_information_get_transactionID = pyqtSignal(str)

    command_mcl_ciranta_request_accept = ""
    command_mcl_credit_request_sendrawtransaction = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.accept()

    def accept(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

        print(self.command_mcl_ciranta_request_accept)
        stdout = ssh.command(self.command_mcl_ciranta_request_accept)
        lines = stdout.readlines()
        out_ = ""
        for deger in lines:
            deger = deger.split("\n")
            out_ = out_ + " " + deger[0]

        print(out_)
        y = json.loads(out_)

        print(y["result"])


        # Hex Onay
        # ---------------------------------------------------------------
        if y["result"] == "success":
            print(y["hex"])
            print(y["requesttxid"])
            print(y["receiverpk"])

            print(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")
            stdout = ssh.command(self.command_mcl_credit_request_sendrawtransaction + "\"" + y["hex"] + "\"")

            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]
            print(out_)
            self.change_value_information_get_transactionID.emit(out_)
            self.change_value_information_accept.emit(True)
        else:
            self.change_value_information_accept.emit(False)


class AllWallet(QThread):
    change_value_information_wallet = pyqtSignal(str)

    command_mcl_all_wallet_list = ""
    command_mcl_get_pubkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.accept()

    def accept(self):

        print("Sunucya bağlanmak için bilgiler alindi.")

        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)

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

        print("=========")
        print(len(y))
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
                time.sleep(0.5)
            except:
                self.change_value_information_wallet.emit("0")
                print("stopped chain")
                break
        print("NOOOOLLDUUUU")
        self.change_value_information_wallet.emit("0")


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
        stdout = ssh.command(self.command_mcl_start_chain_without_pubkey)

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


class ImportPrivkey(QThread):

    change_value_information_get_wallet = pyqtSignal(str)
    change_value_information_get_pubkey = pyqtSignal(str)

    command_mcl_import_privkey = ""
    command_mcl_get_pubkey = ""

    server_username = ""
    server_hostname = ""
    server_password = ""
    server_port = 22

    def run(self):
        self.importPrivkey()

    def importPrivkey(self):

        print("Sunucya bağlanmak için bilgiler alindi.")
        ssh = ServerConnect(self.server_hostname, self.server_username, self.server_password)
        print("bağlantı tamam.")

        #----------------------------------------------
        #Import Privkey and Get Wallet Address
        print(self.command_mcl_import_privkey)
        stdout = ssh.command(self.command_mcl_import_privkey)
        print("^^^^^^^^")
        print(stdout)
        lines = stdout.readlines()
        print(lines)
        if 0 == len(lines):
            self.change_value_information_get_wallet.emit("")
            self.change_value_information_get_pubkey.emit("")
        else:
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]

            self.change_value_information_get_wallet.emit(out_)

            #----------------------------------------------
            #Get Pubkey
            print(self.command_mcl_get_pubkey +" "+out_)
            stdout = ssh.command(self.command_mcl_get_pubkey +" "+out_)
            print("^^^^^^^")
            print(stdout)
            lines = stdout.readlines()
            out_ = ""
            for deger in lines:
                deger = deger.split("\n")
                out_ = out_ + " " + deger[0]

            wallet_info = json.loads(out_)
            print(wallet_info["pubkey"])
            self.change_value_information_get_pubkey.emit(wallet_info["pubkey"])


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

