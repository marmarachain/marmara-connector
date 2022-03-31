from io import StringIO
import paramiko

server_hostname = ""
server_username = ""
server_password = ""
port = 22
ssh_key = None


def set_server_connection(ip, username, pw, ssh_port=None, sshkey=None):
    global server_hostname, server_username, server_password, port, ssh_key
    server_hostname = ip
    server_username = username
    server_password = pw
    port = int(ssh_port)
    ssh_key = sshkey

def server_ssh_connect(time_out=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # global ssh_key
    # if ssh_key:
    #     # ssh_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
    #     print(ssh_key)
    ssh.connect(hostname=server_hostname, username=server_username, password=server_password, port=port, timeout=time_out)
    return ssh

def check_server_connection():
    try:
        client = server_ssh_connect(time_out=15)
        return client
    except Exception as e:
        print(e)
        return 'error'


def server_start_chain(command):
    client = server_ssh_connect()
    client.exec_command(command)
    return client


def server_execute_command(command, ssh_client):
    # client = server_ssh_connect()
    stdin, stdout, stderr = ssh_client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()  # Blocking call
    stdout.flush()
    stderr.flush()
    # client.close()
    return stdout.read().decode("utf8"), stderr.read().decode("utf8"), exit_status
