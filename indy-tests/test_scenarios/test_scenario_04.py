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
from utils.utils import *
from utils.constant import Colors, Constant
from utils.common import Common
from utils.step import Step
from utils.report import TestReport, Status

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class Variables:
    """  Needed some global variables. """
    test_report = TestReport("Test_scenario_04_Keyrings_Wallets")
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    steps = create_step(5)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    Variables.steps[0].set_name("Precondition")
    Common.clean_up_pool_and_wallet_folder(Variables.pool_name, Variables.wallet_name)
    Variables.steps[0].set_status(Status.PASSED)


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
        Variables.steps[1].set_name("Create and open pool Ledger")
        result = await perform(Variables.steps[1], Common.prepare_pool_and_wallet, pool_name,
                               wallet_name, pool_genesis_txn_file)

        pool_handle, wallet_handle = raise_if_exception(result)

        # 2. verify wallet was created in .indy/wallet
        Variables.steps[2].set_name("Verify wallet was created in .indy/wallet")
        wallet_path = Constant.work_dir + "/wallet/" + wallet_name
        result = os.path.exists(wallet_path)
        if result:
            Variables.steps[2].set_status(Status.PASSED)

        # 3. create DID to check the new wallet work well.
        Variables.steps[3].set_name("Create DID to check the new wallet work well")
        await perform(Variables.steps[3], signus.create_and_store_my_did,
                      wallet_handle, json.dumps({"seed": seed_default_trustee}))
    except IndyError as e:
        print(Colors.FAIL + "Indy error: " + str(e) + Colors.ENDC)
    except Exception as ex:
        print(Colors.FAIL + "Exception: " + str(ex) + Colors.ENDC)
    finally:
        # 4. Close and delete the wallet and pool ------------------------------------------------------------------------------
        Variables.steps[4].set_name("Postcondition - Close and delete the wallet and the pool ledger...")
        await perform(Variables.steps[4], Common.clean_up_pool_and_wallet, pool_name,
                      pool_handle, wallet_name, wallet_handle)

        for item in Variables.steps:
            item.to_string()
        logger.info("Test Scenario 04 -> completed")


def test(folder_path=""):
    # Set up the report
    begin_time = time.time()
    Variables.test_report.setup_json_report()

    # Precondition
    test_precondition()

    # Run test case and collect result
    Common.run(test_scenario_04_keyrings_wallets)
    Common.final_result(Variables.test_report, Variables.steps, begin_time)


if __name__ == '__main__':
    test()
