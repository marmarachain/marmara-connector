import paramiko

server_hostname = ""
server_username = ""
server_password = ""


def set_server_connection(ip, username, pw):
    global server_hostname, server_username, server_password
    server_hostname = ip
    server_username = username
    server_password = pw


def check_server_connection():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=server_hostname, username=server_username, password=server_password, port=22)
        ssh.close()
        return
    except paramiko.SSHException as e:
        return e

def server_execute_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=server_hostname, username=server_username, password=server_password, port=22)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout