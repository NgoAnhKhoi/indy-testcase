from typing import Optional
import asyncio
import json
import logging
import os
import signal
from subprocess import Popen, PIPE, TimeoutExpired, STDOUT, check_output
import subprocess
from sys import stdin
import sys
import time
import random
from indy import pool, ledger
from indy.error import IndyError
from distutils.command.config import config
from asyncio.tasks import sleep
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.paramiko import Paramiko, TerminalEnv



# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------
class Colors:
    """ Class to set the colors for text.  Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    folder_path = ".sovrin/"
    pool_genesis_txn_file = "pool_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = "original_pool_transactions_sandbox_genesis"

    pool_genesis_txn_file_path = folder_path + pool_genesis_txn_file
    original_pool_genesis_txn_file_path = folder_path + original_pool_genesis_txn_file
    pool_name = "test_wait_forever_" + str(random.randrange(100, 1000, 2))
    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Test 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_paramiko():
    ip_node5 = "10.20.30.205"
    user_name = "vagrant"
    password = "vagrant"
    paramk = Paramiko()
    terminal = paramk.connect(ip_node5, user_name, password)
    cmd = "echo 'hello'\n"
    stdout, stderr = paramk.run(terminal, cmd, 5)
    print("[stdout:%s], [stderr:%s]" % (str(stdout), str(stderr)))

#     paramk.close_connection(terminal)


test_paramiko()

# def test_precondition():
#     """  Make a copy of pool_transactions_sandbox_genesis  """
#     print(Colors.HEADER + "\n\ Precondition \n" + Colors.ENDC)
# #     work_dir = os.path.expanduser('~') + os.sep
#     data_folder ='/usr/local/bin' 
#     subprocess.run(["cd " + data_folder], shell=True)
#     p = subprocess.Popen(["reset_client"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#     p.stdin.write("YeS".encode(encoding='utf_8'))


# def test_cli_to_val():
#         machine_name = 'validator01'
#         password = 'vagrant'
#         p = subprocess.Popen(["ssh " + machine_name], shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#         print("stderr: " + str(p.stderr))
#         os.system(password)

# def test_start_stop_node():
#         p = subprocess.Popen(["systemctl start sovrin-node"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#         out, err = p.communicate(timeout=10)
#         print("[out:%s][err:%s]" % (str(out), str(err)))
# 
# 
# test_start_stop_node()







