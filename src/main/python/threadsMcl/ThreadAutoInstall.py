import paramiko
from PyQt5.QtCore import QThread, pyqtSignal


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