'''
Created on Nov 9, 2017

@author: khoi.ngo
'''


def generate_random_string(prefix="", suffix="", size=20):
    """
    Generate random string .

    :param prefix: (optional) Prefix of a string.
    :param suffix: (optional) Suffix of a string.
    :param length: (optional) Max length of a string (include prefix and suffix)
    :return: The random string.
    """
    import random
    import string
    left_size = size - len(prefix) - len(suffix)
    random_str = ""
    if left_size > 0:
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(left_size))
    print("Warning: Length of prefix and suffix more than %s chars", str(size))
    result = str(prefix) + random_str + str(suffix)
    return result


def clean_up_pool_and_wallet(pool_name="", wallet_name=""):
    import os
    import shutil
    from .constant import Colors
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n" + Colors.ENDC)
    x = os.path.expanduser('~')
    work_dir = x + os.sep + ".indy"

    if os.path.exists(work_dir + "/pool/" + pool_name):
        try:
            shutil.rmtree(work_dir + "/pool/" + pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(work_dir + "/wallet/" + wallet_name):
        try:
            shutil.rmtree(work_dir + "/wallet/" + wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
