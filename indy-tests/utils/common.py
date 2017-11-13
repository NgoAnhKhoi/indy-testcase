'''
Created on Nov 13, 2017

@author: khoi.ngo
'''

from .constant import Colors
import asyncio
import json
from indy import wallet, pool
from indy.error import IndyError


class Common():
    '''
    Wrapper common steps.
    '''

    @staticmethod
    async def prepare_pool_and_wallet(pool_name, wallet_name, pool_genesis_txn_file):
        pool_handle = await Common.create_and_open_pool(pool_name, pool_genesis_txn_file)
        wallet_handle = await Common.create_and_open_wallet(pool_name, wallet_name)
        return pool_handle, wallet_handle


    async def create_and_open_pool(self, pool_name, pool_genesis_txn_file):
        print(Colors.HEADER + "\nCreate Ledger\n" + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_file)})
        # Create pool
        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise Exception
        print(Colors.HEADER + "\nOpen pool ledger\n" + Colors.ENDC)
        # get pool handle
        try:
            pool_handle = await pool.open_pool_ledger(pool_name, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)
        return pool_handle


    async def create_and_open_wallet(self, pool_name, wallet_name):
        print(Colors.HEADER + "\nCreate wallet\n" + Colors.ENDC)
        try:
            await wallet.create_wallet(pool_name, wallet_name, None, None, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise Exception

        print(Colors.HEADER + "\nGet wallet handle\n" + Colors.ENDC)
        try:
            wallet_handle = await wallet.open_wallet(wallet_name, None, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)
        return wallet_handle
