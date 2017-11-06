import sys
import os
import asyncio
import logging
import subprocess
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
    folder_path = os.path.expanduser("~") + "/.sovrin/"
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
async def command(command_str):
    print("in command")
    subprocess.run(command_str, shell=True)
    output = subprocess.getoutput(command_str)
    print("output: [" + output + "]")
    return output


def test_precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    command(['cd', '~/.sovrin'])
    command(['cp', MyVars.pool_genesis_txn_file_path, MyVars.original_pool_genesis_txn_file_path])
    open(MyVars.pool_genesis_txn_file_path, 'w').close()


async def verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool():
    logger.info("Test Scenario 02 -> started")

    # 1. Using sovrin command -----------------------------
    print(Colors.HEADER + "\n\t1. using sovrin\n" + Colors.ENDC)
    try:
        await command(['sovrin'])
        await command(['connect test'])
        return_message = ""
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 2. connect test with the empty pool_transactions_sandbox_genesis file --------------------------
#     print(Colors.HEADER + "\n\t2. connect test with the empty pool_transactions_sandbox_genesis file\n" + Colors.ENDC)
#     try:
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(command(['connect test']))
#         return_message = "" #await command(['connect test'])
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
#         sys.exit[1]

    # 3. verifying the message ------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t3. verifying the message\n" + Colors.ENDC)
    try:
        print("error_message: " + MyVars.the_error_message)
        if (return_message != MyVars.the_error_message):
            MyVars.test_results['test 3'] = True
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
    print(Colors.HEADER + "\n\t==Clean up==\n\t5. Restore the pool_transactions_sandbox_genesis file\n" + Colors.ENDC)
    try:
        await command(['rm', 'pool_transactions_sandbox_genesis'])
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    try:
        await command(['mv', 'original_pool_trasnsactions_sandbox_genesis', 'pool_transactions_sandbox_genesis'])
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

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
test_precondition()

# Create the loop instance using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool())
loop.close()

print("\n\nResults\n+" + 40*"=" + "+")
final_results()
