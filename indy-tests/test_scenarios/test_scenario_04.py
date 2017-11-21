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
import time
from indy import signus
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import generate_random_string, create_step, perform
from utils.constant import Colors, Constant
from utils.common import Common
from utils.step import Step
from utils.report import TestReport, Status

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class Variables:
    """  Needed some global variables. """
    begin_time = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    test_name = "Test_scenario_04_Keyrings_Wallets"
    test_report = TestReport(test_name)
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    steps = create_step(5)
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False, "Step 5": False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    Common.clean_up_pool_and_wallet_folder(Variables.pool_name, Variables.wallet_name)


async def test_scenario_04_keyrings_wallets():
    logger.info("Test Scenario 04 -> started")
    seed_default_trustee = "000000000000000000000000Trustee1"
    pool_handle = 0
    wallet_handle = 0
    pool_name = Variables.pool_name
    wallet_name = Variables.wallet_name
    pool_genesis_txn_file = Constant.pool_genesis_txn_file

    try:
        # 1. Create and open pool Ledger  ---------------------------------------------------------
        Variables.steps[0].set_name("Create and open pool Ledger")
        pool_handle, wallet_handle = await perform(Variables.steps[0], Common.prepare_pool_and_wallet, pool_name,
                                                   wallet_name, pool_genesis_txn_file)

        # 2. verify wallet was created in .indy/wallet
        Variables.steps[1].set_name("Verify wallet was created in .indy/wallet")
        wallet_path = Constant.work_dir + "/wallet/" + wallet_name
        result = os.path.exists(wallet_path)
        if result:
            Variables.steps[1].set_status(Status.PASSED)

        # 3. create DID to check the new wallet work well.
        Variables.steps[2].set_name("Create DID to check the new wallet work well")
        await perform(Variables.steps[2], signus.create_and_store_my_did,
                      wallet_handle, json.dumps({"seed": seed_default_trustee}))

    except IndyError as e:
        print(Colors.FAIL + "IndyError: " + str(e) + Colors.ENDC)
    except Exception as ex:
        print(Colors.FAIL + "Exception: " + str(ex) + Colors.ENDC)
    finally:
        # 4. Close wallet and pool ------------------------------------------------------------------------------
        Variables.steps[2].set_name("Close and delete the wallet and the pool ledger...")
        await perform(Variables.steps[2], Common.clean_up_pool_and_wallet, pool_name,
                      pool_handle, wallet_name, wallet_handle)

        for item in Variables.steps:
            item.to_string()
        logger.info("Test Scenario 04 -> completed")


def final_result():
    print("\nTest result================================================" + Colors.ENDC)
    if all(value is True for value in Variables.test_results.values()):
        print(Colors.OKGREEN + "\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in Variables.test_results.items():
            if not value:
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)
    Variables.test_report.set_duration(time.time() - Variables.begin_time)
    Variables.test_report.write_result_to_file()


def test(folder_path=""):
    # Set up the report
    Variables.begin_time = time.time()
    Variables.test_report.change_result_dir(folder_path)
    Variables.test_report.setup_json_report()

    test_precondition()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_scenario_04_keyrings_wallets())
    loop.close()

    final_result()


if __name__ == '__main__':
    test()
