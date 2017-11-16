import json
import sys
import logging
import os
import asyncio
import shutil
import time
from indy import agent, ledger, pool, signus, wallet
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Constant, Colors, Roles
from utils.report import TestReport, Status
from utils.common import Common


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    test_report = TestReport("Test_Scenario_09_Remove_And_Add_Role")
    # Need the path to the pool transaction file location
    begin_time = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test08"
    wallet_name = "test_wallet08"
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False,
                    "Step 5": False, "Step 6": False, "Step 7": False, "Step 8": False, "Step 9": False,
                    "Step 10": False, "Step 13": False,"Step 11": False, "Step 12": False, "Step 14": False,
                    "Step 15": False, "Step 16": False, "Step 17": False, }
    base_58_node_5 = "4Tn3wZMNCvhSTXPcLinQDnHyj56DTLQtL61ki4jo2Loc"
    base_58_node_6 = "6G9QhQa3HWjRKeRmEvEkLbWWf2t7cw6KLtafzi494G4G"

    data_add_node5 = {'client_port': 9702, 'client_ip': '10.20.30.205', 'alias': 'Node5', 'node_ip': '10.20.30.205',
                      'node_port': 9701, 'services': ['VALIDATOR']}
    data_add_node6 = {'client_port': 9702, 'client_ip': '10.20.30.206', 'alias': 'Node6', 'node_ip': '10.20.30.206',
                      'node_port': 9701, 'services': ['VALIDATOR']}

    data_promote_node5 = {'alias': 'Node5', 'services': ['VALIDATOR']}
    data_demote_node5 = {'client_port': 9702, 'client_ip': '10.20.30.205', 'alias': 'Node5', 'node_ip': '10.20.30.205',
                         'node_port': 9701, 'services': []}

    data_promote_node6 = {'alias': 'Node6', 'services': ['VALIDATOR']}
    data_demote_node6 = {'client_port': 9702, 'client_ip': '10.20.30.206', 'alias': 'Node6', 'node_ip': '10.20.30.206',
                         'node_port': 9701, 'services': []}


def test_prep():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    Common.clean_up_pool_and_wallet_files(MyVars.pool_name, MyVars.wallet_name)


async def test_08_promote_and_demote_node():

    # 1. Create and open pool.
    step = "Step01. Create and open pool"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await Common().create_and_open_pool(MyVars.pool_name, Constant.pool_genesis_txn_file)
        MyVars.test_report.set_step_status(step, Status.PASSED)
        MyVars.test_results["Step 1"] = True
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)
        return

    # 2. Create and open wallet.
    step = "Step02. Create and open wallet"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        MyVars.wallet_handle = await Common().create_and_open_wallet(MyVars.pool_name, MyVars.wallet_name)
        MyVars.test_report.set_step_status(step, Status.PASSED)
        MyVars.test_results["Step 2"] = True
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)
        return

    # 3. Create DIDs.
    step = "Step03. Create DIDs"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        (default_trustee_did,
         default_trustee_verkey,
         default_trustee_pk) \
            = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                   json.dumps({"seed": Constant.seed_default_trustee}))

        (steward_node5_did,
         steward_node5_verkey,
         steward_node5_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward_node6_did,
         steward_node6_verkey,
         steward_node6_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustee1_did,
         trustee1_verkey,
         trustee1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor1_did,
         trustanchor1_verkey,
         trustanchor1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (identity_did,
         identity_verkey,
         identity_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        MyVars.test_results["Step 3"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)
        return

    # ==================================================================================================================
    # Precondition here!!!
    # ==================================================================================================================

    # 4. Demote node5 and node6 by default Trustee
    step = "Step04. Demote Node5 and Node6 by default Trustee"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    temp = False
    message = ""

    # Demote Node5
    try:
        node_request = await ledger.build_node_request(default_trustee_did, MyVars.base_58_node_5,
                                                       json.dumps(MyVars.data_demote_node5))
        await ledger.submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                    default_trustee_did, node_request)
        temp = True
    except IndyError as E:
        message = "\n{0} - {1}".format("Cannot demote Node5 by default Trustee", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Demote Node6
    try:
        node_request = await ledger.build_node_request(default_trustee_did, MyVars.base_58_node_6,
                                                       json.dumps(MyVars.data_demote_node6))
        await ledger.submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                    default_trustee_did, node_request)
        temp = temp and True
    except IndyError as E:
        message = "{0}\n{1} - {2}".format(message, "Cannot demote Node5 by default Trustee", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 4"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 5. Add role for Stewards, Trustee, TrustAnchor and Identity User
    # Skip any step involve with TGB because role TGB is not supported by libindy
    step = "Step05. Add role for Stewards, Trustee, TrustAnchor and Identity User"
    temp = False
    message = ""
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    # Add role for Trustee
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                trustee1_did, trustee1_verkey, None, Roles.TRUSTEE)
        temp = True
    except IndyError as E:
        message = "\n{} - {}".format("Cannot add role for Trustee", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Add role for StewardNode5
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                steward_node5_did, steward_node5_verkey, None, Roles.STEWARD)
        temp = temp and True
    except IndyError as E:
        message = "{}\n{} - {}".format(message, "Cannot add role for StewardNode5", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Add role for StewardNode6
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                steward_node6_did, steward_node6_verkey, None, Roles.STEWARD)
        temp = temp and True
    except IndyError as E:
        message = "{}\n{} - {}".format(message, "Cannot add role for StewardNode6", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Add role for TrustAnchor
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                trustanchor1_verkey, trustanchor1_verkey, None, Roles.TRUST_ANCHOR)
        temp = temp and True
    except IndyError as E:
        message = "{}\n{} - {}".format(message, "Cannot add role for TrustAnchor", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Add role for Identity Owner
    try:
        await Common.build_and_send_nym_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                                identity_did, identity_verkey, None, None)
        temp = temp and True
    except IndyError as E:
        message = "{}\n{} - {}".format(message, "Cannot add role for Identity Owner", str(E))
        temp = False
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 5"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 6. Add Node5 by StewardNode5
    step = "Step06. Add Node5 by StewardNode5"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    try:
        node5_request = await ledger.build_node_request(steward_node5_did, MyVars.base_58_node_5,
                                                        json.dumps(MyVars.data_add_node5))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                             steward_node5_did, node5_request)
        MyVars.test_results["Step 6"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)
        return

    # 7. Add Node6 by StewardNode6
    step = "Step07. Add Node5 by StewardNode6"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    try:
        node6_request = await ledger.build_node_request(steward_node6_did, MyVars.base_58_node_6,
                                                        json.dumps(MyVars.data_add_node6))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                             steward_node6_did, node6_request)
        MyVars.test_results["Step 7"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)
        return

    # ==================================================================================================================
    # Begin test here!!!
    # ==================================================================================================================

    # 8. Verify that a Steward cannot demote another Steward's node
    step = "Step08. Verify that a Steward cannot demote another Steward's node"
    message = ""
    temp = False
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    # Demote Node5 by StewardNode6
    try:
        node5_request = await ledger.build_node_request(steward_node6_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_demote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node6_did, node5_request)
        temp = False
        message = "\n{}".format("StewardNode6 can demote Node5 (should fail)")
        print(Colors.FAIL + "\n\t" + "StewardNode6 can demote Node5 (should fail)" + "\n" + Colors.ENDC)
    except IndyError as E:
        temp = True
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Demote Node6 by StewardNode5
    try:
        node6_request = await ledger.build_node_request(steward_node5_did, MyVars.base_58_node_6,
                                                        json.dump({MyVars.data_demote_node6}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node6_did, node6_request)
        temp = False
        message = "{}\n{}".format(message, "StewardNode5 can demote Node6 (should fail)")
        print(Colors.FAIL + "\n\t" + "StewardNode5 can demote Node6 (should fail)" + "\n" + Colors.ENDC)
    except IndyError as E:
        temp = True and temp
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 8"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 9. Verify that a TrustAnchor cannot demote any nodes
    step = "Step09. Verify that TrustAnchor cannot demote any nodes"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        node5_request = await ledger.build_node_request(trustanchor1_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_demote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, node5_request)
        print(Colors.FAIL + "\n\t" + "TrustAnchor can demote Node5 (should fail)" + "\n" + Colors.ENDC)
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, "TrustAnchor can demote Node5 (should fail)")
    except IndyError as E:
        MyVars.test_results["Step 9"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # 10. Verify that an Identity Owner cannot demote any nodes
    step = "Step10. Verify that an Identity Owner cannot demote any nodes"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        node5_request = await ledger.build_node_request(identity_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_demote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, identity_did, node5_request)
        print(Colors.FAIL + "\n\t" + "Identity Owner can demote Node5 (should fail)" + "\n" + Colors.ENDC)
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, "Identity Owner can demote Node5 (should fail)")
    except IndyError as E:
        MyVars.test_results["Step 10"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # 11. Verify that a Steward cannot promote another Steward's node
    step = "Step11. Verify that a Steward cannot promote another Steward's node"
    message = ""
    temp = False
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    # Promote Node5 by StewardNode6
    try:
        node5_request = await ledger.build_node_request(steward_node6_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_promote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node6_did, node5_request)
        temp = False
        message = "\n{}".format("StewardNode6 can promote Node5 (should fail)")
        print(Colors.FAIL + "\n\t" + "StewardNode6 can promote Node5 (should fail)" + "\n" + Colors.ENDC)
    except IndyError as E:
        temp = True
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Promote Node6 by StewardNode5
    try:
        node6_request = await ledger.build_node_request(steward_node5_did, MyVars.base_58_node_6,
                                                        json.dump({MyVars.data_promote_node6}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node5_did, node6_request)
        temp = False
        message = "{}\n{}".format(message, "StewardNode5 can promote Node6 (should fail)")
        print(Colors.FAIL + "\n\t" + "StewardNode5 can promote Node6 (should fail)" + "\n" + Colors.ENDC)
    except IndyError as E:
        temp = True and temp
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 11"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 12. Verify that a Steward can promote their own node
    step = "Step12. Verify that a Steward can promote their own node"
    message = ""
    temp = False
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    # Promote Node5 by StewardNode5
    try:
        node5_request = await ledger.build_node_request(steward_node5_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_promote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node5_did, node5_request)
        temp = True
    except IndyError as E:
        temp = False
        message = "\n{} - {}".format("StewardNode5 cannot promote Node5 (should pass)", str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Promote Node6 by StewardNode6
    try:
        node6_request = await ledger.build_node_request(steward_node6_did, MyVars.base_58_node_6,
                                                        json.dump({MyVars.data_promote_node6}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward_node6_did, node6_request)
        temp = temp and True
    except IndyError as E:
        temp = False
        message = "{}\n{} - {}".format(message, "StewardNode5 cannot promote Node6 (should pass)", str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 12"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 13. Verify that Trustee can demote any node
    step = "Step13. Verify that Trustee can demote any node"
    message = ""
    temp = False
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)

    # Promote Node5 by default Trustee
    try:
        node5_request = await ledger.build_node_request(default_trustee_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_demote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                             default_trustee_did, node5_request)
        temp = True
    except IndyError as E:
        temp = False
        message = "\n{} - {}".format("Default Trustee cannot demote Node5 (should pass)", str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # Promote Node6 by default Trustee
    try:
        node6_request = await ledger.build_node_request(default_trustee_did, MyVars.base_58_node_6,
                                                        json.dump({MyVars.data_demote_node6}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle,
                                             default_trustee_did, node6_request)
        temp = temp and True
    except IndyError as E:
        temp = False
        message = "{}\n{} - {}".format(message, "Default Trustee cannot demote Node6 (should pass)", str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    MyVars.test_results["Step 13"] = temp
    if temp:
        MyVars.test_report.set_step_status(step, Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, message[1:])

    # 14. Verify any Trustee can promote the node
    step = "Step14. Verify that any Trustee can promote the node"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        node5_request = await ledger.build_node_request(trustee1_did, MyVars.base_58_node_5,
                                                        json.dump({MyVars.data_demote_node5}))
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, node5_request)
        MyVars.test_results["Step 14"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # ==================================================================================================================
    # Clean up here!!!
    # ==================================================================================================================
    print(Colors.HEADER + "\n\t==CleanUp==\n" + Colors.ENDC)
    # 15. Remove Node5 and Node6 from ledger
    # Investigating

    # 16. Close pool and wallet
    step = "Step16. Close pool and wallet"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        await Common().close_pool_and_wallet(MyVars.pool_handle, MyVars.wallet_handle)
        MyVars.test_results["Step 16"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)

    # 17. Delete pool and wallet
    step = "Step17. Delete pool and wallet"
    print(Colors.HEADER + "\n\t" + step + "\n" + Colors.ENDC)
    try:
        await Common().delete_pool_and_wallet(MyVars.pool_name, MyVars.wallet_name)
        MyVars.test_results["Step 17"] = True
        MyVars.test_report.set_step_status(step, Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status(step, Status.FAILED, str(E))
        print(Colors.FAIL + "\n\t" + str(E) + "\n" + Colors.ENDC)


def final_result():
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)
    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()


def test():
    MyVars.begin_time = time.time()
    test_prep()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_08_promote_and_demote_node())
    loop.close()
    final_result()


test()