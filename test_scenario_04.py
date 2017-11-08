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
import random
from indy import ledger, signus, wallet, pool
from indy.error import IndyError

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


class Colors:
    """ Class to set the colors for text.  Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    # Need the path to the pool transaction file location
    pool_genesis_txn_file = ".sovrin/pool_transactions_sandbox_genesis"
    wallet_handle = 0
    pool_name = "test_pool_" + str(random.randrange(100, 1000, 2))
    pool_name1 = "test_pool_" + str(random.randrange(100, 1000, 2))
    wallet_name = "test_wallet_" + str(random.randrange(100, 1000, 1))
    debug = False
    test_results = {'Test 6': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    """  Delete all files out of the .sovrin/pool and .sovrin/wallet directories  """
    import os
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n" + Colors.ENDC)
    x = os.path.expanduser('~')
    work_dir = x + os.sep + ".indy"

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
#     # create and open pool to check which wallet is active
#     # 4. Create ledger config from genesis txn file  ---------------------------------------------------------
#     print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
#     pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})
#     try:
#         await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
#         sys.exit[1]
# 
#     await asyncio.sleep(0)
# 
#     # 5. Open pool ledger -----------------------------------------------------------------------------------
#     print(Colors.HEADER + "\n\t2.  Open pool ledger\n" + Colors.ENDC)
#     try:
#         pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
#         MyVars.pool_handle = pool_handle
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
# 
#     await asyncio.sleep(0)
#     if MyVars.debug:
#         input(Colors.WARNING + "\n\nPoolHandle is %s" % str(MyVars.pool_handle) + Colors.ENDC)

    # 6. verify wallet moved to .indy/wallet
    try:
        wallet_path = ".indy/wallet/" + MyVars.wallet_name
        result = os.path.isfile(wallet_path)
        if result == True:
            MyVars.test_results['Test 6'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nWallet handle is %s" % str(MyVars.wallet_handle) + Colors.ENDC)


    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 13. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t13. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nClosed wallet and pool\n" + Colors.ENDC)

    # 14. Delete wallet and pool ledger --------------------------------------------------------------------
    print(Colors.HEADER + "\n\t14. Delete the wallet and pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nDeleted wallet and pool ledger\n" + Colors.ENDC)

    logger.info("Test Scenario 04 -> completed")


def final_results():
    """  Show the test results  """

    if all(value == True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


def log(str):
    print("\n\n" + str + "\n\n")

# Run the cleanup first...
test_prep()

# Create the loop instance using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(verifying_that_the_Trust_Anchor_can_only_add_NYMs_for_identity_owners_and_not_blacklist_any_roles())
loop.close()

print("\n\nResults\n+" + 40*"=" + "+")
final_results()