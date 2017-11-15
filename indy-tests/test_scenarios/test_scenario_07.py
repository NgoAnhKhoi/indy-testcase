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
from utils.constant import Colors, Constant, Roles
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
    pool_genesis_bak = Constant.original_pool_genesis_txn_file + str(random.randrange(10, 1000, 2))

    domain_transactions_sandbox_genesis = Constant.domain_transactions_sandbox_genesis
    domain_transactions_sandbox_genesis_bak = Constant.domain_transactions_sandbox_genesis + str(random.randrange(10, 1000, 2))

    wallet_handle = 0
    test_report = TestReport("Test_scenario_07_Add_Node")
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    test_results = {'Step 2': False, 'Step 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def command(command_str):
    os.system(command_str)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
#     print(Colors.HEADER + "\nMake a copy of pool_transactions_sandbox file\n" + Colors.ENDC)
#     copy_file(MyVars.pool_genesis_txn_file, MyVars.pool_genesis_bak)
#     open(MyVars.pool_genesis_txn_file, 'w').close()


async def test_scenario_04_keyrings_wallets():
    logger.info("Test Scenario 07 -> started")
    seed_default_trustee = generate_random_string(prefix="Trustee1", size=32) #"000000000000000000000000Trustee1"
    seed_steward_node5 = generate_random_string(prefix="StewardNode5", size=32)
    seed_steward_node6 = generate_random_string(prefix="StewardNode6", size=32)
    seed_trust_anchor = generate_random_string(prefix="TrustAnchor", size=32)
    seed_identity_owner = generate_random_string(prefix="IdentityOwner", size=32)
#     seed_tgb = generate_random_string(prefix="TGB", size=32)

    # data
    data_node5={'client_port': 9702, 'client_ip': '10.0.0.105', 'alias': 'Node5', 'node_ip': '10.0.0.105',
                 'node_port': 9701, 'services': ['VALIDATOR']}
    data_node6={'client_port': 9702, 'client_ip': '10.0.0.106', 'alias': 'Node6', 'node_ip': '10.0.0.106',
                 'node_port': 9701, 'services': ['VALIDATOR']}

    # 1. Create and open pool Ledger  ---------------------------------------------------------
    print(Colors.HEADER + "\n\t1. Create and open pool Ledger\n" + Colors.ENDC)
    try:
        MyVars.pool_handle, MyVars.wallet_handle = await Common.prepare_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name, MyVars.pool_genesis_txn_file)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(1, "Create and open pool Ledger", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 2. Create DIDs ----------------------------------------------------
    print(Colors.HEADER + "\n\t2. Create DID's\n" + Colors.ENDC)
    try:
        (default_trustee_did, default_trustee_verkey, default_trustee_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))

        (steward_node_5_did, steward_node_5_verkey, steward_node_5_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_steward_node5}))
        (steward_node_6_did, steward_node_6_verkey, steward_node_6_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_steward_node6}))

        (trust_anchor_did, trust_anchor_verkey, trust_anchor_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_trust_anchor}))
        (identity_owner_did, identity_owner_verkey, identity_owner_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_identity_owner}))
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDID's created..." + Colors.ENDC)

    # 3. Trustee create a steward
    print(Colors.HEADER + "\n\t3. Trustee create a steward\n" + Colors.ENDC)
    try:
        await Common.build_and_send_nym(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did, steward_node_5_did,
                                         steward_node_5_verkey, None, Roles.STEWARD)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None
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
