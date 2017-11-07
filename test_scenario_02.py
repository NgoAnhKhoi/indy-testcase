import asyncio
import json
import logging
import os
import subprocess
import sys

from indy import pool
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
    folder_path = "~/.sovrin/" #os.path.expanduser("~") + "/.sovrin/"
    pool_genesis_txn_file = "pool_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = "original_pool_transactions_sandbox_genesis"

    pool_genesis_txn_file_path = folder_path + pool_genesis_txn_file
    original_pool_genesis_txn_file_path = folder_path + original_pool_genesis_txn_file
    pool_name = "test_pool02"
    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Test 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def command(command_str):
    print("in command")
    p = subprocess.Popen(command_str, shell=True)
    output = p.communicate()[0]
    subprocess._cleanup()
    return output


def get_output():
    return subprocess.getoutput()

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
test = ["sovrin 'connect test'"]
test1 = ["exit"]
command(test)
command(test1)
# test_precondition()

# Create the loop instance using asyncio
# loop = asyncio.get_event_loop()
# loop.run_until_complete(verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool())
# loop.close()

print("done")
# print("\n\nResults\n+" + 40*"=" + "+")
# final_results()
