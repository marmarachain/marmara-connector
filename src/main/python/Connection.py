import paramiko


class ServerConnect:

    def __init__(self, server_hostname, server_username, server_password):
        self.server_port = 22

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(server_hostname, self.server_port, server_username, server_password)

    def command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout
