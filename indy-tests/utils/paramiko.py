'''
Created on Nov 16, 2017

@author: khoi.ngo
'''
import paramiko
import time
import socket


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
                self._terminal = TerminalEnv(ssh_client, shell)

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

    def run(self, *cmds, terminal=None, wait=0):
        if not self._terminal:
            print("Please using connect method before run.")
            return None

        chanel = terminal.shell()
        if not chanel:
            return None

        buffer = 65535
        stdout = ""
        stderr = ""

        for cmd in enumerate(cmds):    
            if cmd[len(cmd) - 1] != '\n':
                cmd = '{0}{1}'.format(cmd, '\n')
            chanel.send(cmd) # Applying await in the next sprint
            time.sleep(wait)
    
            if chanel.recv_ready():
                stdout = chanel.recv(buffer).decode("utf-8")
            if chanel.recv_stderr_ready():
                stderr = chanel.recv_stderr(buffer).decode("utf-8")
        return stdout, stderr

    def close_connection(self, terminal=None):
        if terminal:
            return terminal.ssh().close()
        elif self._terminal:
            return self._terminal.ssh().close()
        time.sleep(3)
