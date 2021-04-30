import paramiko


def connect_server(server_hostname, server_username, server_password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(port=22, hostname=server_hostname, username=server_username, password=server_password)
