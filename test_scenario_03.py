import json
import sys
import logging
import os
import asyncio
import shutil
from indy import agent, ledger, pool, signus, wallet
from indy.error import IndyError
from utils import Colors, Constant


class MyVars:
    pool_handle = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test3"
    wallet_name = "test_wallet3"
    debug = False
    test_results = {"Test 5": False, "Test 6": False, "Test 7": False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(Constant.work_dir + "wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(Constant.work_dir + "pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)


async def do():
    logger.info("Test scenario 3 -> started")

    seed_steward01 = "000000000000000000000000Steward1"
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})

    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    print(Colors.HEADER + "\n\t3. Create wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 4. Create DID
    print(Colors.HEADER + "\n\t4. Create DID's\n" + Colors.ENDC)
    try:
        await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({"seed": seed_steward01}))
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5. Connect to pool.
    # Verify that the default wallet move to Test from NoEnv?
    # Cannot verify because ".indy/wallet" do not include any folder that name
    # no-env and test, and default wallet cannot be created via indy-sdk
    print(Colors.HEADER + "\n\t5.  Connect to pool\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Test 5"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 6. Disconnect from pool.
    print(Colors.HEADER + "\n\t6.  Disconnect from pool\n" + Colors.ENDC)
    try:
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Test 6"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 7. Reconnect to pool.
    print(Colors.HEADER + "\n\t7.  Reconnect to pool\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Test 7"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 8. Close pool ledger and wallet.
    print(Colors.HEADER + "\n\t8.  Close pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 9. Delete wallet.
    print(Colors.HEADER + "\n\t9.  Delete pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test scenario 3 -> finished")


def final_result():
    print(Colors.HEADER + "\n\tTest result\n" + Colors.ENDC)
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


def test():
    test_prep()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do())
    loop.close()
    final_result()


test()
