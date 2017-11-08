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
from indy import pool
from indy.error import IndyError
from distutils.command.config import config


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
    folder_path = "~/.sovrin/" #os.path.expanduser("~") + "/.sovrin/"
    pool_genesis_txn_file = "pool_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = "original_pool_transactions_sandbox_genesis"

    pool_genesis_txn_file_path = folder_path + pool_genesis_txn_file
    original_pool_genesis_txn_file_path = folder_path + original_pool_genesis_txn_file
    pool_name = "t_pl123l"
    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Test 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def command(command_str):
#     print("in command")
    os.system(command_str)
#     stdout = ""
#     try:
#         process = Popen(['sovrin'], stdin = PIPE, stdout = PIPE)
#         subprocess.call(['connect test'], stdin = PIPE, stdout = PIPE)
#         subprocess.call(['exit'], stdin = PIPE, stdout = PIPE)
# #         while True:
# #             if 'connecting test' in str(process.stdout.readline()):
# #                 
# #                 break
# #         process.terminate()
#     except TimeoutExpired:
#         stdout = "asdf"
# #     subprocess.call(command_str)
# #     subprocess.run(command_str, time_out=30)
# #     stdout = check_output(command_str, stderr=STDOUT, timeout=30)
# #     stdout = "" #"p.communicate()[0]
# #     try:
# #         stdout = process.communicate(timeout=10)[0]
# #     except TimeoutExpired:
# #         os.kill(process.pid, signal.SIGINT) # send signal to the process group
# #         stdout = process.communicate()[0]
# #     print("out command")
#     return stdout

def test_precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    print(Colors.HEADER + "\n\ Precondition \n" + Colors.ENDC)
#     command(['cd', '~/.sovrin'])
    command(['cp', MyVars.pool_genesis_txn_file_path, MyVars.original_pool_genesis_txn_file_path])
#     open(MyVars.pool_genesis_txn_file_path, 'w').close()


async def verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool():
    logger.info("Test Scenario 02 -> started")

    # 1. Using sovrin command -----------------------------
    print(Colors.HEADER + "\n\t1. using sovrin\n" + Colors.ENDC)
    try:
        return_message = await command(['sovrin', 'connect test'])
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 2. connect test with the empty pool_transactions_sandbox_genesis file --------------------------
#     print(Colors.HEADER + "\n\t2.  Create Ledger\n" + Colors.ENDC)
#     pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file_path)})
#     try:
#         await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
#         sys.exit[1]
# 
#     await asyncio.sleep(1)

    # 3. verifying the message ------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t3. verifying the message\n" + Colors.ENDC)
    try:
        print("error_message: " + MyVars.the_error_message)
#         return_message = get_output()
        print("output_message: " + return_message)
        if (return_message != MyVars.the_error_message):
            MyVars.test_results['Test 3'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # 4. exit sovrin -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t4. exit sovrin\n" + Colors.ENDC)
    try:
        await command(['exit'])
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 5. Restore the pool_transactions_sandbox_genesis file ------------------------------------------------------------------------------
#     print(Colors.HEADER + "\n\t==Clean up==\n\t5. Restore the pool_transactions_sandbox_genesis file\n" + Colors.ENDC)
#     try:
#         await command(['rm', 'pool_transactions_sandbox_genesis', 'mv', 'original_pool_trasnsactions_sandbox_genesis', 'pool_transactions_sandbox_genesis'])
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test Scenario 02 -> completed")


def final_results():
    """  Show the test results  """

    if all(value == True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


# Run the cleanup first...
async def test_connect():
    print("Begin")
    pool_txn = ".sovrin/pool_transactions_sandbox_genesis"
    pool_config = json.dumps({"genesis_txn": str(pool_txn)})
    pool_name = "test_" + str(random.randrange(100, 1000, 2))
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
        res = await pool.open_pool_ledger(pool_name, None)
        print("result: " + str(res))
    except IndyError as E:
        print("do something with error_code: " + str(E))

    print("end")

# Create the loop instance using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(test_connect())
loop.close()





#     finally:
#         cmd = 'cp ' + MyVars.folder_path + "khoi_pool " + MyVars.pool_genesis_txn_file_path
#         os.system('cmd')
#     subprocess.call(['connect test'])
# command(test1)
# command(test1)

# async def abc():
#     test = ['sovrin','connect test']
#     test1 = ["exit"]
#     await command(test)
#     await command(test1)
# test_precondition()

# Create the loop instance using asyncio
# loop = asyncio.get_event_loop()
# loop.run_until_complete(khoi())
# loop.close()

print("done")
# print("\n\nResults\n+" + 40*"=" + "+")
# final_results()
