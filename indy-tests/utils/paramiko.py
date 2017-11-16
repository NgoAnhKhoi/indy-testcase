'''
Created on Nov 16, 2017

@author: khoi.ngo
'''
import paramiko
import time
import socket
from _sqlite3 import connect


class TerminalEnv():
    def __init__(self, o_ssh, o_shell):
        self._ssh = o_ssh
        self._shell = o_shell

    def ssh(self):
        return self._ssh

    def shell(self):
        return self._shell


class Paramiko():
    '''
    classdocs
    '''

    def __init__(self, o_node=None):
        self._node = o_node
        self._terminal = None
        self._retry_time = 3

    def connect(self, host_ip, user_name, pass_word):

        i = 0
        shell = None
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        while i < self._retry_time:
            try:
                ssh_client.connect(hostname=host_ip, username=user_name, password=pass_word)

                shell = ssh_client.invoke_shell()
                return TerminalEnv(ssh_client, shell)

            except paramiko.AuthenticationException:
                break

            except paramiko.BadHostKeyException:
                # print("BadHostKeyException failed when connecting to %s" % host_ip)
                break

            except paramiko.SSHException:
                # print("SSHException failed when connecting to %s" % host_ip)
                break

            except socket.error:
                # print("Socket error when connecting to %s" % host_ip)
                break

            except:

                i += 1
                # If we could not connect within time limit

                if i == self._retry_time:
                    return None
                else:
                    time.sleep(2)

        return None

    def run(self, terminal, cmd, wait=0):
        if not terminal:
            return None

        chanel = terminal.shell()
        if not chanel:
            return None

        buffer = 65535
        stdout = ""
        stderr = ""
        if cmd[len(cmd) - 1] != '\n':
            cmd = '{0}{1}'.format(cmd, '\n')
        chanel.send(cmd)
        time.sleep(wait) # remove

        if chanel.recv_ready(): # wait in case False. A False result does not mean that the channel has closed (API docs)
            stdout = chanel.recv(buffer).decode("utf-8")
        if chanel.recv_stderr_ready():
            stderr = chanel.recv_stderr(buffer).decode("utf-8")
        return [stdout, stderr]

    def o__runCmd(self, terminal, cmd):
        buff_size = 2048
        stdout = ""
        stderr = ""

        # print("Run command: %s" % cmd)
        if not terminal:
            return None

        transport = terminal.get_transport()
        channel = transport.open_session()
        channel.settimeout(0.0)
        channel.setblocking(0)
        channel.exec_command(cmd)

        while not channel.exit_status_ready():
            time.sleep(2)
            if channel.recv_ready():
                stdout += channel.recv(buff_size).decode("utf-8")

            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(buff_size).decode("utf-8")

        # Need to gobble up any remaining output after program terminates...
        while channel.recv_ready():
            stdout += channel.recv(buff_size).decode("utf-8")

        while channel.recv_stderr_ready():
            stderr += channel.recv_stderr(buff_size).decode("utf-8")

        # print ("exit status: %s" % chan.recv_exit_status())
        # print("stdout:\n%s" % stdout.encode('utf_8'))
        # print("stderr:\n%s" % stderr.encode('utf_8'))

        return stdout, stderr

#     def run(self, cmd, wait=0, terminal=None):
#         if terminal:
#             return self.__runCmd(terminal, cmd, wait)
#         elif self._terminal:
#             return self.__runCmd(self._terminal, cmd, wait)
# 
#         else:
#             return None

#     # Connect to a remote machine whose information is specified in node para
#     def connection(self, o_node=None):
# 
#         if o_node:
#             node = o_node
#         elif self._node:
#             node = self._node
#         else:
#             return None
#         self._terminal = self.__connect(node.host_name, node.user_name, node.password)
# 
#         return self._terminal

    def close_connection(self, terminal=None):
        if terminal:
            return terminal.ssh().close()
        elif self._terminal:
            return self._terminal.ssh().close()
        time.sleep(3)
