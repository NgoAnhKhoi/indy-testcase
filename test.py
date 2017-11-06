import sys
import os
import asyncio
import json
import logging
import subprocess
import tempfile
import shutil
from indy import ledger, signus, wallet, pool
from indy.error import IndyError

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
    folder_path = os.path.expanduser("~") + "/.sovrin"
    pool_genesis_txn_file = "pool_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = "original_pool_transactions_sandbox_genesis"

    pool_genesis_txn_file_path = folder_path + pool_genesis_txn_file
    original_pool_genesis_txn_file_path = folder_path + original_pool_genesis_txn_file

    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Test 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# noinspection PyUnresolvedReferences
def command(command_str):
    os.system(command_str)
    output = subprocess.getoutput(command_str)
    return output
    # with tempfile.TemporaryFile() as tempf:
    #     proc = subprocess.Popen(command_str, stdout=tempf)
    #     proc.wait()
    #     tempf.seek(0)
    #     print (tempf.read())


def precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    command('cd ~/.sovrin')
    output  = command('ls -l')
    print(output)
    # command('cp', MyVars.pool_genesis_txn_file, MyVars.original_pool_genesis_txn_file)
    # open(MyVars.pool_genesis_txn_file_path, 'w').close()


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
precondition()

# Create the loop instance using asyncio
# loop = asyncio.get_event_loop()
# loop.run_until_complete(verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool())
# loop.close()
#
# print("\n\nResults\n+" + 40*"=" + "+")
# final_results()
