'''
Created on Nov 8, 2017

@author: khoi.ngo
'''
# /usr/bin/env python3.6
import sys
import json
import logging
import time
import os
from indy import ledger, signus
from indy.error import IndyError
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.utils import *
from utils.constant import Colors, Constant, Roles
from utils.report import TestReport, Status
from utils.common import Common
from utils.step import Step
# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class Variables:
    """  Needed some global variables. """
    test_report = TestReport("Test_Scenario_11_Special_Case_Trust_Anchor_Role")
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    debug = False
    steps = create_step(19)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    Variables.steps[0].set_name("Precondition")
    Common.clean_up_pool_and_wallet_folder(Variables.pool_name, Variables.wallet_name)
    Variables.steps[0].set_status(Status.PASSED)


async def test_scenario_11_special_case_trust_anchor_role():
    logger.info("Test Scenario 11 -> started")
    pool_handle = 0
    wallet_handle = 0
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    # Declare all values use in the test
    seed_trustee1 = generate_random_string(prefix="Trustee1", size=32)
    seed_trustee2 = generate_random_string(prefix="Trustee2", size=32)
    seed_steward1 = generate_random_string(prefix="Steward1", size=32)
    seed_steward2 = generate_random_string(prefix="Steward2", size=32)
    seed_trustanchor1 = generate_random_string(prefix="TrustAnchor1", size=32)
    seed_trustanchor2 = generate_random_string(prefix="TrustAnchor2", size=32)
    seed_trustanchor3 = generate_random_string(prefix="TrustAnchor3", size=32)

    try:
        # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
        Variables.steps[1].set_name("Create and open pool Ledger")
        result = await perform(Variables.steps[1], Common.prepare_pool_and_wallet, Variables.pool_name,
                               Variables.wallet_name, pool_genesis_txn_file)

        pool_handle, wallet_handle = raise_if_exception(result)

        # 2. Create DIDs ----------------------------------------------------
        Variables.steps[2].set_name("Create DIDs")
        (default_trustee_did, default_trustee_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                                      wallet_handle, json.dumps({"seed": Constant.seed_default_trustee}))

        (trustee1_did, trustee1_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                        wallet_handle, json.dumps({"seed": seed_trustee1}))
        (trustee2_did, trustee2_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                        wallet_handle, json.dumps({"seed": seed_trustee2}))
        (steward1_did, steward1_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                        wallet_handle, json.dumps({"seed": seed_steward1}))
        (steward2_did, steward2_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                        wallet_handle, json.dumps({"seed": seed_steward2}))
        (trustanchor1_did, trustanchor1_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                                wallet_handle, json.dumps({"seed": seed_trustanchor1}))
        (trustanchor2_did, trustanchor2_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                                wallet_handle, json.dumps({"seed": seed_trustanchor2}))
        (trustanchor3_did, trustanchor3_verkey) = await perform(Variables.steps[2], signus.create_and_store_my_did,
                                                                wallet_handle, json.dumps({"seed": seed_trustanchor3}))

        # 3. Using the default Trustee create a TrustAnchor and a new Trustee---------------
        Variables.steps[3].set_name("Use default Trustee to create a Trustee")
        nym_txn_req3 = await perform(Variables.steps[3], ledger.build_nym_request, default_trustee_did, trustee1_did,
                                     trustee1_verkey, None, Roles.TRUSTEE)
        await perform(Variables.steps[3], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                      default_trustee_did, nym_txn_req3)

        # 4. Verify GET_NYM for trustee1-----------------------------------------------------------------------------------
        Variables.steps[4].set_name("Verify get nym for Trustee")
        get_nym_txn_req4 = await perform(Variables.steps[4], ledger.build_get_nym_request, default_trustee_did, trustee1_did)
        await perform(Variables.steps[4], ledger.submit_request, pool_handle, get_nym_txn_req4)

        # 5. Create TrustAnchor1
        Variables.steps[5].set_name("Create TrustAnchor1")
        nym_txn_req5 = await perform(Variables.steps[5], ledger.build_nym_request, default_trustee_did, trustanchor1_did,
                                     trustanchor1_verkey, None, Roles.TRUST_ANCHOR)
        await perform(Variables.steps[5], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                      default_trustee_did, nym_txn_req5)

        # 6. Verify GET_NYM for TrustAnchor1-------------------------------------------------------------------------------
        Variables.steps[6].set_name("Verify GET_NYM for TrustAnchor1")
        get_nym_txn_req6 = await perform(Variables.steps[6], ledger.build_get_nym_request, default_trustee_did, trustanchor1_did)
        await perform(Variables.steps[6], ledger.submit_request, pool_handle, get_nym_txn_req6)

        # 7. Using the TrustAnchor create a Trustee (Trust Anchor should not be able to create Trustee) --------------------
        Variables.steps[7].set_name("Use TrustAnchor1 to create a Trustee")
        nym_txn_req7 = await perform(Variables.steps[7], ledger.build_nym_request, trustanchor1_did,
                                     trustee2_did, trustee2_verkey, None, Roles.TRUSTEE)
        await perform_with_expected_code(Variables.steps[7], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req7, expected_code=304)

        # 8. Verify GET_NYM for new Trustee--------------------------------------------------------------------------------
        Variables.steps[8].set_name("Verify get NYM for new trustee")
        get_nym_txn_req8 = await perform(Variables.steps[8], ledger.build_get_nym_request, trustanchor1_did, trustee2_did)
        await perform(Variables.steps[8], ledger.submit_request, pool_handle, get_nym_txn_req8)

        # 9. Verify that the TestTrustAnchorTrustee cannot create a new Steward
        Variables.steps[9].set_name("Verify a trustee cannot create a new Steward")
        nym_txn_req9 = await perform(Variables.steps[9], ledger.build_nym_request, trustee2_did, steward1_did,
                                     steward1_verkey, None, Roles.STEWARD)
        await perform_with_expected_code(Variables.steps[9], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustee2_did, nym_txn_req9, expected_code=304)

        # 10. Using the TrustAnchor blacklist a Trustee (TrustAnchor should not be able to blacklist Trustee)
        Variables.steps[10].set_name("Use TrustAnchor to blacklist a Trustee")
        nym_txn_req10 = await perform(Variables.steps[10], ledger.build_nym_request, trustanchor1_did, trustee1_did,
                                      trustee1_verkey, None, Roles.NONE)
        await perform_with_expected_code(Variables.steps[10], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req10, expected_code=304)

        # 11. Verify Trustee was not blacklisted by creating another Trustee------------------------------------------------
        Variables.steps[11].set_name("Verify Trustee was not blacklisted by creating another Trustee")
        nym_txn_req11 = await perform(Variables.steps[11], ledger.build_nym_request, trustee1_did, trustee2_did,
                                      trustee2_verkey, None, Roles.TRUSTEE)
        await perform(Variables.steps[11], ledger.sign_and_submit_request, pool_handle, wallet_handle, trustee1_did, nym_txn_req11)

        # 12. Using the TrustAnchor1 to create a Steward2 -----------------------------------------------------------------
        Variables.steps[12].set_name("TrustAnchor1 cannot create a Steward2")
        nym_txn_req12 = await perform(Variables.steps[12], ledger.build_nym_request, trustanchor1_did, steward2_did,
                                      steward2_verkey, None, Roles.STEWARD)
        await perform_with_expected_code(Variables.steps[12], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req12, expected_code=304)

        # 13. Using the Trustee1 create Steward1 -----------------------------------------------------------------
        Variables.steps[13].set_name("Using the Trustee1 create Steward1")
        nym_txn_req13 = await perform(Variables.steps[13], ledger.build_nym_request, trustee1_did, steward1_did,
                                      steward1_verkey, None, Roles.STEWARD)
        await perform(Variables.steps[13], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                      trustee1_did, nym_txn_req13)

        # 14. Now run the test to blacklist Steward1
        Variables.steps[14].set_name("Run the test to blacklist Steward1")
        nym_txn_req14 = await perform(Variables.steps[14], ledger.build_nym_request, trustanchor1_did, steward1_did,
                                      steward1_verkey, None, Roles.NONE)
        await perform_with_expected_code(Variables.steps[14], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req14, expected_code=304)

        # 15. Verify that a TrustAnchor1 cannot create another TrustAnchor3 -------------------------------------
        Variables.steps[15].set_name("Verify TrustAnchor1 cannot create a TrustAnchor3")
        nym_txn_req15 = await perform(Variables.steps[15], ledger.build_nym_request, trustanchor1_did, trustanchor3_did,
                                      trustanchor3_verkey, None, Roles.TRUST_ANCHOR)
        await perform_with_expected_code(Variables.steps[15], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req15, expected_code=304)

        # 16. Using the Trustee1 create TrustAnchor2 -----------------------------------------------------------------
        Variables.steps[16].set_name("Using the Trustee1 create Steward1")
        nym_txn_req16 = await perform(Variables.steps[16], ledger.build_nym_request, trustee1_did, trustanchor2_did,
                                      trustanchor2_verkey, None, Roles.TRUST_ANCHOR)
        await perform(Variables.steps[16], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                      trustee1_did, nym_txn_req16)

        # 17. Verify that a TrustAnchor1 cannot blacklist another TrustAnchor2 -------------------------------------
        Variables.steps[17].set_name("Verify TrustAnchor1 cannot blacklist TrustAnchor2")
        nym_txn_req17 = await perform(Variables.steps[17], ledger.build_nym_request, trustanchor1_did, trustanchor2_did,
                                      trustanchor2_verkey, None, Roles.NONE)
        await perform_with_expected_code(Variables.steps[17], ledger.sign_and_submit_request, pool_handle, wallet_handle,
                                         trustanchor1_did, nym_txn_req17, expected_code=304)

    except IndyError as e:
        print(Colors.FAIL + "Indy error: " + str(e) + Colors.ENDC)
    except Exception as ex:
        print(Colors.FAIL + "Exception: " + str(ex) + Colors.ENDC)
    finally:
        # 18. Close wallet and pool ------------------------------------------------------------------------------
        Variables.steps[18].set_name("Postcondition - Close and delete the wallet and the pool ledger...")
        await perform(Variables.steps[18], Common.clean_up_pool_and_wallet, Variables.pool_name,
                      pool_handle, Variables.wallet_name, wallet_handle)

        logger.info("Test Scenario 11 -> completed")


def test(folder_path=""):
    # Set up the report
    begin_time = time.time()
    Variables.test_report.setup_json_report()

    # Precondition
    test_precondition()

    # Run test case and collect result
    Common.run(test_scenario_11_special_case_trust_anchor_role)
    Common.final_result(Variables.test_report, Variables.steps, begin_time)


if __name__ == '__main__':
    test()
