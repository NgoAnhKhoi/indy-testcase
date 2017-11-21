import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from test_scenarios import test_scenario_02, test_scenario_03, test_scenario_04, test_scenario_09, test_scenario_11


def main():
    # list of test
    test_scenario_02.test()
    test_scenario_03.test()
    test_scenario_04.test()
    test_scenario_09.test()
    test_scenario_11.test()


if __name__ == '__main__':
    main()
