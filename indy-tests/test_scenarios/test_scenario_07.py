'''
Created on Nov 13, 2017

@author: khoi.ngo
'''
# /usr/bin/env python3.6
import sys
import asyncio
import json
import os.path
import logging.handlers
# import shutil
import time
import random
from indy import signus, wallet, pool
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import *
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
    file_target = Constant.original_pool_genesis_txn_file
    wallet_handle = 0
    test_report = TestReport("Test_scenario_07_Add_Node")
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    test_results = {'Step 2': False, 'Step 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def command(command_str):
    os.system(command_str)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
    print(Colors.HEADER + "\nMake a copy of pool_transactions_sandbox file\n" + Colors.ENDC)
    MyVars.file_target += str(random.randrange(10, 1000, 2))
    copy_file(Constant.pool_genesis_txn_file, MyVars.file_target)


async def test_scenario_04_keyrings_wallets():
    logger.info("Test Scenario 07 -> started")
    seed_default_trustee = "000000000000000000000000Trustee1"

#     # 1. Create and open pool Ledger  ---------------------------------------------------------
#     print(Colors.HEADER + "\n\t1.  Create and open pool Ledger\n" + Colors.ENDC)
#     try:
#         MyVars.pool_handle, MyVars.wallet_handle = await Common.prepare_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name, MyVars.pool_genesis_txn_file)
#     except IndyError as E:
#         MyVars.test_report.set_test_failed()
#         MyVars.test_report.set_step_status(1, "Create and open pool Ledger", str(E))
#         print(Colors.FAIL + str(E) + Colors.ENDC)
#         return None
# 
#     # 2. verify wallet was created in .indy/wallet
#     try:
#         print(Colors.HEADER + "\n\t2. Verifying the new wallet was created\n" + Colors.ENDC)
#         work_dir = os.path.expanduser('~') + os.sep + ".indy"
#         wallet_path = work_dir + "/wallet/" + MyVars.wallet_name
#         result = os.path.exists(wallet_path)
#         if result:
#             MyVars.test_results['Step 2'] = True
#             print("===PASSED===")
#     except IndyError as E:
#         MyVars.test_report.set_test_failed()
#         MyVars.test_report.set_step_status(4, "Verify wallet was created in \".indy/wallet\"", str(E))
#         print(Colors.FAIL + str(E) + Colors.ENDC)
# 
#     await asyncio.sleep(0)
# 
#     # 3. create DID to check the new wallet work well.
#     print(Colors.HEADER + "\n\t3. Create DID to check the new wallet work well\n" + Colors.ENDC)
#     try:
#         # create and store did to check the new wallet work well.
#         (default_trustee_did, default_trustee_verkey, default_trustee_pk) = await signus.create_and_store_my_did(
#             MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))
#         if default_trustee_did:
#             MyVars.test_results['Step 3'] = True
#             print("===PASSED===")
#     except IndyError as E:
#         MyVars.test_report.set_test_failed()
#         MyVars.test_report.set_step_status(5, "Create DID to check the new wallet work well", str(E))
#         print(Colors.FAIL + str(E) + Colors.ENDC)
# 
#     # ==================================================================================================================
#     #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     # ==================================================================================================================
#     # 4. Close wallet and pool ------------------------------------------------------------------------------
#     print(Colors.HEADER + "\n\t==Clean up==\n\t4. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
#     try:
#         await Common.clean_up_pool_and_wallet(MyVars.pool_name, MyVars.pool_handle, MyVars.wallet_name, MyVars.wallet_handle)
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
# 
#     await asyncio.sleep(0)

    # Revert pool transactions sandbox file ------------------------------------------------------------------------------
    try:
        copy_file(MyVars.file_target, Constant.pool_genesis_txn_file)
    except Exception as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test Scenario 07 -> completed")


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
