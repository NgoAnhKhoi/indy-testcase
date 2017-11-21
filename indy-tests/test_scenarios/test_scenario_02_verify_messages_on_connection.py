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
from utils.utils import *
from utils.report import TestReport, Status
from utils.step import Step
from utils.common import Common



# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class Variables:
    the_error_message = "the information needed to connect was not found"
    test_report = TestReport("Test_Scenario_02_Verify_Messages_On_Connection")
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    steps = create_step(5)

    """  Needed some global variables. """
    pool_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    original_pool_genesis_txn_file = Constant.original_pool_genesis_txn_file
    pool_name = generate_random_string("test_pool", size=20)
    debug = False

    # cmds
    back_up_pool_genesis_file = 'cp ' + pool_genesis_txn_file + " " + original_pool_genesis_txn_file
    exit_sovrin = 'exit'
    remove_pool_genesis_file = 'rm ' + pool_genesis_txn_file
    restore_pool_genesis_file = 'cp ' + original_pool_genesis_txn_file + " " + pool_genesis_txn_file


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run(cmd):
    os.system(cmd)


def test_precondition():
    """  Make a copy of pool_transactions_sandbox_genesis  """
    Variables.steps[0].set_name("Precondition")
    run(Variables.back_up_pool_genesis_file)
    open(Variables.pool_genesis_txn_file, 'w').close()
    Variables.steps[0].set_status(Status.PASSED)


async def test_scenario_02_verify_messages_on_connection():
    logger.info("Test Scenario 02 -> started")

    try:
        # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
        Variables.steps[1].set_name("Create Ledger")
        pool_config = json.dumps({"genesis_txn": str(Variables.pool_genesis_txn_file)})
        Variables.pool_handle = await perform(Variables.steps[1], pool.create_pool_ledger_config, Variables.pool_name, pool_config)

        # 2. Open pool ledger -----------------------------------------------------------------------------------
        Variables.steps[2].set_name("Open pool ledger")
        Variables.steps[2].set_message("Failed due to the Bug IS-332")
        Variables.steps[2].set_status(Status.FAILED)

        # 3. verifying the message ------------------------------------------------------------------------
        Variables.steps[3].set_name("verifying the message")
        Variables.steps[3].set_message("TODO after fix IS-332")
        Variables.steps[3].set_status(Status.FAILED)

    finally:
        # 4. Restore the pool_transactions_sandbox_genesis file-------------------------------------------------
        Variables.steps[4].set_name("Restore the pool_transactions_sandbox_genesis file")
        try:
            run(Variables.remove_pool_genesis_file)
            run(Variables.restore_pool_genesis_file)
            Variables.steps[4].set_status(Status.PASSED)
        except Exception as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            Variables.steps[4].set_status(Status.FAILED)
            Variables.steps[4].set_message(str(E))
        logger.info("Test Scenario 02 -> completed")


def test():
    # Set up the report
    begin_time = time.time()
    Variables.test_report.setup_json_report()

    # Precondition
    test_precondition()

    # Run test case and collect result
    Common.run(test_scenario_02_verify_messages_on_connection)
    Common.final_result(Variables.test_report, Variables.steps, begin_time)


if __name__ == '__main__':
    test()
