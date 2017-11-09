'''
Created on Nov 9, 2017

@author: khoi.ngo
'''


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


class Roles:
    TRUSTEE = "TRUSTEE"
    STEWARD = "STEWARD"
    TRUST_ANCHOR = "TRUST_ANCHOR"
    TGB = "TGB"
    NONE = ""


class Constant:
    import os
    work_dir = os.path.expanduser('~') + os.sep + ".indy"
    seed_default_trustee = "000000000000000000000000Trustee1"
    pool_genesis_txn_file = os.path.expanduser('~') + os.sep + ".sovrin/pool_transactions_sandbox_genesis"


def generate_random_string(prefix="", suffix="", length=20):
    """
    Generate random string .

    :param prefix: (optional) Prefix of a string.
    :param suffix: (optional) Suffix of a string.
    :param length: (optional) Max length of a string (exclude prefix and suffix)
    :return: The random string.
    """
    import random
    import string
    random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    result = str(prefix) + random_str + str(suffix)
    return result
