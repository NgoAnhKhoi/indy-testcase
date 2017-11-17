'''
Created on Nov 16, 2017

@author: khoi.ngo
'''
import paramiko
import time
import socket


class TerminalEnv():
    """
    Class Terminal Environment was used to store shell and ssh object.
    """
    def __init__(self, o_ssh, o_shell):
        self._ssh = o_ssh
        self._shell = o_shell

    def ssh(self):
        return self._ssh

    def shell(self):
        return self._shell


class Paramiko():
    """
    Class Paramiko connect and run command from CLI to nodes, agents.
    """

    def __init__(self, o_node=None):
        self._node = o_node
        self._terminal = None
        self._retry_times = 3

    def connect(self, host_ip, username, password):
        """
        Connect to an SSH server and authenticate to it.

        :param host_ip: the server to connect to
        :param user_name: the username to authenticate as (defaults to the current localusername)
        :param password: Used for password authentication; is also used for private key
                         decryption if ``passphrase`` is not given.
        """
        i_time = 0
        shell = None
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        while i_time < self._retry_times:
            try:
                ssh_client.connect(hostname=host_ip, username=username, password=password)

                shell = ssh_client.invoke_shell()
                self._terminal = TerminalEnv(ssh_client, shell)

            except paramiko.AuthenticationException:
                print("AuthenticationException failed when connecting to %s" % host_ip)
                break
            except paramiko.BadHostKeyException:
                print("BadHostKeyException failed when connecting to %s" % host_ip)
                break
            except paramiko.SSHException:
                print("SSHException failed when connecting to %s" % host_ip)
                break
            except socket.error:
                print("Socket error when connecting to %s" % host_ip)
                break
            except Exception:
                i_time += 1
                if i_time == self._retry_times:
                    return None
                else:
                    time.sleep(2)

        return None

    def run(self, *cmds, wait=0):
        """
        Close connection to SSH Server.

        :param cmds: The list command will be run.
        :param wait: the time wait for chanel send cmd complete (seconds).
        :return: stdout and stderr of the last cmd.
        """
        if not self._terminal:
            print("Please using connect method before run.")
            return None

        chanel = self._terminal.shell()
        if not chanel:
            return None

        buffer = 65535
        stdout = ""
        stderr = ""

        for cmd in enumerate(cmds):
            if cmd[len(cmd) - 1] != '\n':
                cmd = '{0}{1}'.format(cmd, '\n')
            chanel.send(cmd)  # Applying await in the next sprint
            time.sleep(wait)

            if chanel.recv_ready():
                stdout = chanel.recv(buffer).decode("utf-8")
            if chanel.recv_stderr_ready():
                stderr = chanel.recv_stderr(buffer).decode("utf-8")
        return stdout, stderr

    def close_connection(self, terminal=None):
        """
        Close connection to SSH Server.
        """
        if terminal:
            return terminal.ssh().close()
        elif self._terminal:
            return self._terminal.ssh().close()
        time.sleep(3)
