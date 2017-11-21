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
    else:
        print("Warning: Length of prefix and suffix more than %s chars" % str(size))
    result = str(prefix) + random_str + str(suffix)
    return result


def create_step(size):
    from utils.step import Step
    lst_step = []
    for i in range(0, size):
        step = Step(i, "")
        lst_step.append(step)
    return lst_step


def handle_exception(code, *agrs):
    if not isinstance(code, IndexError or Exception):
        *agrs = code
    else:
        raise code

async def perform(step, func, *agrs):
    from indy.error import IndyError
    from utils.report import Status
    result = None
    try:
        result = await func(*agrs)
        step.set_status(Status.PASSED)
    except IndyError as E:
        print("Indy error" + str(E))
        step.set_message(str(E))
        return E
    except Exception as Ex:
        print("Exception" + str(Ex))
        step.set_message(str(E))
        return Ex
    return result


async def perform_with_expected_code(func, *agrs, expected_code=0):
    from indy.error import IndyError
    result = None
    try:
        result = await func(*agrs)
    except IndyError as E:
        if E == expected_code:
            print("PASSED")
        else:
            print("[NAK-perform] Indy error" + str(E))
            raise E
    except Exception as Ex:
        print("[NAK-perform] Exception" + str(Ex))
        return Ex
    return result
