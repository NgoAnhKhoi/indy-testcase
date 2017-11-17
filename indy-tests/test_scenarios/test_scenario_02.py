import asyncio
import json
import logging
import os
import sys
import time
from indy import pool
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Constant, Colors
from utils.utils import generate_random_string
from utils.paramiko import Paramiko
from utils.report import HTMLReport


# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    original_pool_genesis_txn_file = Constant.original_pool_genesis_txn_file
    pool_name = generate_random_string("test_pool", size=20)

    # cmds
    back_up_pool_genesis_file = 'cp ' + pool_genesis_txn_file + " " + original_pool_genesis_txn_file
    exit_sovrin = 'exit'
    remove_pool_genesis_file = 'rm ' + pool_genesis_txn_file
    restore_pool_genesis_file = 'cp ' + original_pool_genesis_txn_file + " " + pool_genesis_txn_file

    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Step3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_command(cmds):
    host_ip = "192.168.171.101"
    user_name = "vagrant"
    pass_word = "vagrant" 
    paramk = Paramiko.connect(host_ip, user_name, pass_word)
    paramk.run(*cmds)
    paramk.close_connection()

def test_precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    print(Colors.HEADER + "\n\ Precondition \n" + Colors.ENDC)
    run_command(MyVars.back_up_transacstion_file)
    open(MyVars.pool_genesis_txn_file, 'w').close()


async def test_scenario_02_verify_messages_on_connection():
    logger.info("Test Scenario 02 -> started")
    try:
        # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
        print(Colors.HEADER + "\n\Step1.  Create Ledger\n" + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})
        try:
            await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]
        await asyncio.sleep(0)

        # 2. Open pool ledger -----------------------------------------------------------------------------------
        print(Colors.HEADER + "\n\Step2.  Open pool ledger\n" + Colors.ENDC)
        try:
            print('%s: ' % str("Failed due to the Bug IS-332: https://jira.hyperledger.org/browse/IS-332") + Colors.FAIL + 'failed' + Colors.ENDC)
            return False
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit(1)

        # 3. verifying the message ------------------------------------------------------------------------
        print(Colors.HEADER + "\n\Step3. verifying the message\n" + Colors.ENDC)
        try:
            print("TODO after fix IS-332")
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]
    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    finally:
        # 4. Restore the pool_transactions_sandbox_genesis file ------------------------------------------------------------------------------
        print(Colors.HEADER + "\n\t==Clean up==\n\t4. Restore the pool_transactions_sandbox_genesis file\n" + Colors.ENDC)
        try:
            run_command(MyVars.remove_pool_genesis_file, MyVars.restore_pool_genesis_file)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test Scenario 02 -> completed")


def final_result():
    print("\nTest result================================================" + Colors.ENDC)
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)
    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()

    # Generate html single report:
    folder = MyVars.test_report.get_result_folder()
    if folder.find(MyVars.test_name) != -1:
        print("Making...")
        HTMLReport().make_html_report(folder, MyVars.test_name)


def test():
    MyVars.begin_time = time.time()
    test_precondition()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_scenario_02_verify_messages_on_connection())
    loop.close()

    final_result()

test()

