import json
import sys
import logging
import os
import time
from indy import pool, signus, wallet
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Colors, Constant
from utils.report import TestReport, Status
from utils.common import Common
from utils.step import Step
from utils.utils import *


class Variables:
    # Data for generating report
    test_name = "Test_Scenario_03_Check_Connection"
    test_report = TestReport(test_name)

    # Data using in testcase
    begin_time = 0
    pool_name = "pool_genesis_test3"
    wallet_name = "test_wallet3"
    debug = False
    seed_steward01 = "000000000000000000000000Steward1"
    steps = create_step(8)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    # Precondition steps:
    Variables.steps[0].set_name("Precondition")
    Common.clean_up_pool_and_wallet_folder(Variables.pool_name, Variables.wallet_name)
    Variables.steps[0].set_status(Status.PASSED)


async def test_scenario_03_check_connection():
    logger.info("{0} -> started".format(Variables.test_name))
    pool_handle = 0
    wallet_handle = 0
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})
    try:
        # 1. Create pool ledger
        Variables.steps[1].set_name("Create pool ledger")
        await perform(Variables.steps[1], pool.create_pool_ledger_config, Variables.pool_name, pool_config)

        # 2. Create wallet
        Variables.steps[2].set_name("Create wallet")
        await perform(Variables.steps[2], wallet.create_wallet, Variables.pool_name, Variables.wallet_name, None, None, None)
        wallet_handle = await perform(Variables.steps[2], wallet.open_wallet, Variables.wallet_name, None, None)

        # 3. Create DID
        Variables.steps[3].set_name("Create DID")
        await perform(Variables.steps[3], signus.create_and_store_my_did, wallet_handle, json.dumps({"seed": Variables.seed_steward01}))

        # 4. Connect to pool.
        # Verify that the default wallet move to Test from NoEnv?
        # Cannot verify because ".indy/wallet" do not include any folder that name
        # no-env and test, and default wallet cannot be created via indy-sdk
        Variables.steps[4].set_name("Connect to pool")
        pool_handle = await perform(Variables.steps[4], pool.open_pool_ledger, Variables.pool_name, None)

        # 5. Disconnect from pool.
        Variables.steps[5].set_name("Disconnect form pool")
        await perform(Variables.steps[5], pool.close_pool_ledger, pool_handle)

        # 6. Reconnect to pool.
        Variables.steps[6].set_name("Reconnect to pool")
        pool_handle = await perform(Variables.steps[6], pool.open_pool_ledger, Variables.pool_name, None)
    finally:
        Variables.steps[7].set_name("Postcondition - Close and delete the wallet and the pool ledger...")
        await perform(Variables.steps[7], Common.clean_up_pool_and_wallet, Variables.pool_name,
                      pool_handle, Variables.wallet_name, wallet_handle)

        logger.info("Test scenario 3 -> finished")


def test(folder_path=""):
    # Set up the report
    begin_time = time.time()
    Variables.test_report.setup_json_report()

    # Precondition
    test_precondition()

    # Run test case and collect result
    Common.run(test_scenario_03_check_connection)
    Common.final_result(Variables.test_report, Variables.steps, begin_time)


if __name__ == '__main__':
    test()
