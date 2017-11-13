'''
Created on Nov 8, 2017

@author: khoi.ngo
'''
# /usr/bin/env python3.6
import sys
import asyncio
import json
import os.path
import logging
# import shutil
import time
from indy import signus, wallet, pool
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import generate_random_string, clean_up_pool_and_wallet
from utils.constant import Colors, Constant
from utils.report import TestReport
from utils.common import Common

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class MyVars:
    """  Needed some global variables. """
    begin_time = 0
    pool_handle = 0
    # Need the path to the pool transaction file location
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    wallet_handle = 0
    test_report = TestReport("Test_scenario_04_Keyrings_Wallets")
    pool_name = "test_pool_exists" #generate_random_string("test_pool", size=10)
    wallet_name = generate_random_string("test_wallet", size=10)
    debug = False
    test_results = {'Step 4': False, 'Step 5': False}

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

log_tm = time.strftime("%d-%m-%Y_%H-%M-%S")
name, ext = os.path.splitext(sys.argv[0])
log_name = str(name + '--test_' + log_tm + '.log')

# Setup logger with an output level
logger = logging.getLogger('LogiGear_log_test')
logger.setLevel(logging.INFO)


# Add the log message handler to the logger, set the max size for the log and the count for splitting the log
handler = logging.handlers.RotatingFileHandler(log_name, maxBytes=5000000, backupCount=10)
logger.addHandler(handler)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
    clean_up_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name)


async def test_scenario_04_keyrings_wallets():
    logger.info("Test Scenario 04 -> started")
    seed_default_trustee = "000000000000000000000000Trustee1"

    # 1. Create and open pool Ledger  ---------------------------------------------------------
    print((Colors.HEADER + "\n\t1.  Create and open pool Ledger\n" + Colors.ENDC) % (MyVars.current_step))
    try:
        MyVars.pool_handle = await Common.create_and_open_pool(MyVars.pool_name, MyVars.pool_genesis_txn_file)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(1, "Create and open pool Ledger", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nPoolHandle is %s" % str(MyVars.pool_handle) + Colors.ENDC)

    # 2. Create and open Wallet -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t2. Create wallet\n" + Colors.ENDC)
    try:
        MyVars.wallet_handle = await Common.create_and_open_wallet(MyVars.pool_name, MyVars.wallet_name)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(2, "Create and open wallet", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 3. verify wallet was created in .indy/wallet
    try:
        print(Colors.HEADER + "\n\t3. Verifying the new wallet was created\n" + Colors.ENDC)
        work_dir = os.path.expanduser('~') + os.sep + ".indy"
        wallet_path = work_dir + "/wallet/" + MyVars.wallet_name
        result = os.path.exists(wallet_path)
        print("===PASSED===")
        if result:
            MyVars.test_results['Step 3'] = True
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(4, "Verify wallet was created in \".indy/wallet\"", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 4. create DID to check the new wallet work well.
    print(Colors.HEADER + "\n\t4. Create DID to check the new wallet work well\n" + Colors.ENDC)
    try:
        # create and store did to check the new wallet work well.
        (default_trustee_did, default_trustee_verkey, default_trustee_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))
        if default_trustee_did:
            MyVars.test_results['Step 4'] = True
            print("===PASSED===")
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(5, "Create DID to check the new wallet work well", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 5. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t5. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 6. Delete wallet and pool ledger --------------------------------------------------------------------
    print(Colors.HEADER + "\n\t6. Delete the wallet and pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    logger.info("Test Scenario 04 -> completed")


def final_results():
    """  Show the test results  """
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)

    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()


def test():

    MyVars.begin_time = time.time()
    # Run the cleanup first...
    test_prep()

    # Create the loop instance using asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_scenario_04_keyrings_wallets())
    loop.close()

    print("\n\nResults\n+" + 40 * "=" + "+")
    final_results()


test()
