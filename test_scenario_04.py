'''
Created on Nov 8, 2017

@author: khoi.ngo
'''
#! /usr/bin/env python3.6
import sys
import asyncio
import json
import os.path
import logging
import shutil
from indy import signus, wallet, pool
from indy.error import IndyError
from utils import Colors, Constant, generate_random_string

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------



class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    # Need the path to the pool transaction file location
    pool_genesis_txn_file = Constant.pool_genesis_txn_file
    wallet_handle = 0
    pool_name = generate_random_string("test_pool", length=10)
    wallet_name = generate_random_string("test_wallet", length=10)
    print(("pool_name: %s\nwallet_name: %s") % (pool_name, wallet_name))
    debug = False
    test_results = {'Test 4': [False, "no message"], 'Test 5': [False, "no message"]}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    """  Delete all files out of the .sovrin/pool and .sovrin/wallet directories  """
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n" + Colors.ENDC)
    work_dir = Constant.work_dir

    if os.path.exists(work_dir + "/pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(work_dir + "/pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(work_dir + "/wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(work_dir + "/wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "Pause after test prep\n" + Colors.ENDC)


async def verifying_that_the_Trust_Anchor_can_only_add_NYMs_for_identity_owners_and_not_blacklist_any_roles():
    logger.info("Test Scenario 04 -> started")
    seed_default_trustee = "000000000000000000000000Trustee1"

    # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    await asyncio.sleep(0)

    # 2. Open pool ledger -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t2.  Open pool ledger\n" + Colors.ENDC)
    try:
        pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.pool_handle = pool_handle
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nPoolHandle is %s" % str(MyVars.pool_handle) + Colors.ENDC)

    # 3. Create Wallet -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t3. Create wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # Get wallet handle
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 4. verify wallet was created in .indy/wallet
    try:
        print(Colors.HEADER + "\n\t4. Verifying the new wallet was created\n" + Colors.ENDC)
        work_dir = os.path.expanduser('~') + os.sep + ".indy"
        wallet_path = work_dir + "/wallet/" + MyVars.wallet_name
        result = os.path.exists(wallet_path)
        print("===PASSED===")
        if result:
            MyVars.test_results['Test 4'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 5. create DID to check the new wallet work well.
    print(Colors.HEADER + "\n\t5. Create DID to check the new wallet work well\n" + Colors.ENDC)
    try:
        # create and store did to check the new wallet work well.
        (default_trustee_did, default_trustee_verkey, default_trustee_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))
        if default_trustee_did:
            MyVars.test_results['Test 5'] = True
            print("===PASSED===")
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 6. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t6. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    #7. Delete wallet and pool ledger --------------------------------------------------------------------
    print(Colors.HEADER + "\n\t7. Delete the wallet and pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    logger.info("Test Scenario 04 -> completed")


def final_results():
    """  Show the test results  """

    if all(value == True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, [result, message] in MyVars.test_results.items():
            if not result:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed with reason: ' + message + Colors.ENDC)


# Run the cleanup first...
test_prep()

# Create the loop instance using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(verifying_that_the_Trust_Anchor_can_only_add_NYMs_for_identity_owners_and_not_blacklist_any_roles())
loop.close()

print("\n\nResults\n+" + 40*"=" + "+")
final_results()
