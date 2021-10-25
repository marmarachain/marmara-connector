from io import StringIO
import paramiko

server_hostname = ""
server_username = ""
server_password = ""
port = 22
timeout = 4
ssh_key = ""


def set_server_connection(ip, username, pw):
    global server_hostname, server_username, server_password
    server_hostname = ip
    server_username = username
    server_password = pw


def server_ssh_connect(ssh_key=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if ssh_key is not None:
        ssh_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
    ssh.connect(hostname=server_hostname, username=server_username, password=server_password, port=port, pkey=ssh_key)
    return ssh


def check_server_connection():
    try:
        client = server_ssh_connect()
        return client
    except paramiko.SSHException as e:
        return 'error'


def server_start_chain(command):
    client = server_ssh_connect()
    client.exec_command(command)
    return client


def server_execute_command(command, ss_client):
    # client = server_ssh_connect()
    stdin, stdout, stderr = ss_client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()  # Blocking call
    stdout.flush()
    stderr.flush()
    # client.close()
    return stdout.read().decode("utf8"), stderr.read().decode("utf8"), exit_status
