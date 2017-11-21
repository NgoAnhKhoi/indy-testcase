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
from indy import signus, wallet, pool, ledger
from indy.error import IndyError
import abc
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
    pool_genesis_txn_file = os.path.expanduser('~') + os.sep + "Git/indy-testcase/khoi"

#     domain_transactions_sandbox_genesis = Constant.domain_transactions_sandbox_genesis
#     domain_transactions_sandbox_genesis_bak = Constant.domain_transactions_sandbox_genesis + str(random.randrange(10, 1000, 2))

    wallet_handle = 0
    test_report = TestReport("Test_scenario_07_Add_Node")
    pool_name = generate_random_string("test_pool", size=32)
    wallet_name = generate_random_string("test_wallet", size=32)
    debug = False
    test_results = {'Step3': False, 'Step4': False, 'Step5': False, 'Step6': False, 'Step7': False, 'Step8': False, 'Step9': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """
    print(Colors.HEADER + "\nPrecondition. Clean up pools and wallets\n" + Colors.ENDC)
    Common.clean_up_pool_and_wallet_folder(MyVars.pool_name, MyVars.wallet_name)


async def test_scenario_07_add_node():
    logger.info("Test Scenario 07 -> started")
    seed_default_trustee = Constant.seed_default_trustee
    seed_steward_node5 = generate_random_string(prefix="StewardNode5", size=32)
    seed_steward_node6 = generate_random_string(prefix="StewardNode6", size=32)
    seed_trust_anchor = generate_random_string(prefix="TrustAnchor", size=32)
    seed_identity_owner = generate_random_string(prefix="IdentityOwner", size=32)
    base_58_node_5 = "4Tn3wZMNCvhSTXPcLinQDnHyj56DTLQtL61ki4jo2Loc"
    base_58_node_6 = "6G9QhQa3HWjRKeRmEvEkLbWWf2t7cw6KLtafzi494G4G"
#     seed_tgb = generate_random_string(prefix="TGB", size=32)

    # data
    data_node5={'client_port': 9702, 'client_ip': '10.20.30.205', 'alias': 'Node5', 'node_ip': '10.20.30.205',
                 'node_port': 9701, 'services': ['VALIDATOR']}
    data_node6={'client_port': 9702, 'client_ip': '10.20.30.206', 'alias': 'Node6', 'node_ip': '10.20.30.206',
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

    # 3. Trustee create a steward5
    print(Colors.HEADER + "\n\t3. Trustee create a steward5, steward6, trust anchor, identity owner\n" + Colors.ENDC)
    parts3={'3': False, '3a': False, '3b': False, '3c': False}
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                steward_node_5_did, steward_node_5_verkey, None, Roles.STEWARD)
        parts3['3'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 3a. Trustee create a steward6
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                steward_node_6_did, steward_node_6_verkey, None, Roles.STEWARD)
        parts3['3a'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 3b. Trustee create a trustanchor
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                trust_anchor_did, trust_anchor_verkey, None, Roles.TRUST_ANCHOR)
        parts3['3b'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # 3c. Trustee create a identityowner
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                identity_owner_did, identity_owner_verkey, None, Roles.NONE)
        parts3['3c'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return None

    # If any of the results are are not true, then fail the test
    if not all(value is True for value in parts3.values()):
        print(Colors.FAIL + "\n\tOne of the commands in step 3 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Step3'] = True

    await asyncio.sleep(0)

    # 4. Verify that a Trustee cannot add a validator node
    print(Colors.HEADER + "\n\t4. Verify that a Trustee cannot add a validator node\n" + Colors.ENDC)
    node_req4 = await ledger.build_node_request(default_trustee_did, base_58_node_5, json.dumps(data_node5))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did, node_req4)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results['Step4'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Trustee cannot add a validator node\n" + Colors.ENDC))
        else:
            print(str(E))

    # 5. Verify that a Trust Anchor cannot add a validator node
    print(Colors.HEADER + "\n\t5. Verify that a Trust Anchor cannot add a validator node\n" + Colors.ENDC)
    node_req5 = await ledger.build_node_request(trust_anchor_did, base_58_node_5, json.dumps(data_node5))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trust_anchor_did, node_req5)
    except IndyError as E:
        print("\nError: %s\n" % str(E.error_code))
        if E.error_code == 304:
            MyVars.test_results['Step5'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Trust Anchor cannot add a validator node\n" + Colors.ENDC))
        else:
            print(str(E))

    # 6. Verify that a Identity Owner cannot add a validator node
    print(Colors.HEADER + "\n\t6. Verify that a Identity Owner cannot add a validator node\n" + Colors.ENDC)
    node_req6 = await ledger.build_node_request(identity_owner_did, base_58_node_5, json.dumps(data_node5))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, identity_owner_did, node_req6)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results['Step6'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Identity Owner cannot add a validator node\n" + Colors.ENDC))
        else:
            print(str(E))

    # 7. Verify that a Steward5 can add a validator node
    print(Colors.HEADER + "\n\t7. Verify that a Steward_node_5 can add a validator node\n" + Colors.ENDC)
    node_req7 = await ledger.build_node_request(steward_node_5_did, base_58_node_5, json.dumps(data_node5))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node_5_did, node_req7)
        MyVars.test_results['Step7'] = True
        print(Colors.OKGREEN + ("::PASS::Validated that a Steward_node_5 can add a validator node\n" + Colors.ENDC))
    except IndyError as E:
        print(str(E))

    # 8. Verify that a steward can only add one node by trying to add another one.
    print(Colors.HEADER + "\n\t8. Verify that a Steward_node_5 can only add one node by trying to add another one\n" + Colors.ENDC)
    node_req8 = await ledger.build_node_request(steward_node_5_did, base_58_node_6, json.dumps(data_node6))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node_5_did, node_req8)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results['Step8'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Steward_node_5 can only add one node by trying to add another one\n" + Colors.ENDC))
        else:
            print(str(E))

    # 9. Verify that a Steward_node_6 can add a validator node.
    print(Colors.HEADER + "\n\t9. Verify that a Steward_node_6 can add a validator node\n" + Colors.ENDC)
    node_req9 = await ledger.build_node_request(steward_node_6_did, base_58_node_6, json.dumps(data_node6))
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node_6_did, node_req9)
        MyVars.test_results['Step9'] = True
        print(Colors.OKGREEN + ("::PASS::Validated that a Steward_node_6 can add a validator node\n" + Colors.ENDC))
    except IndyError as E:
        print(str(E))

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 10. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t10. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await Common.clean_up_pool_and_wallet(MyVars.pool_name, MyVars.pool_handle, MyVars.wallet_name, MyVars.wallet_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
    await asyncio.sleep(0)

    logger.info("Test Scenario 07 -> completed")


def final_results():
    """  Show the test results  """
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                print('%s: ' % str(test_num) + Colors.FAIL + 'Failed' + Colors.ENDC)
            else:
                print('%s: ' % str(test_num) + Colors.OKGREEN + 'Passed' + Colors.ENDC)

    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()


def test():

    MyVars.begin_time = time.time()
    # Run the cleanup first...
    test_prep()

    # Create the loop instance using asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_scenario_07_add_node())
    loop.close()

    print("\n\nResults\n+" + 40 * "=" + "+")
    final_results()


test()
