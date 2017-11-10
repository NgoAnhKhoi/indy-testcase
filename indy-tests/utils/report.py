'''
Created on Nov 9, 2017

@author: nhan.nguyen
'''

import json
import time
import os


class TestReport:
    result_dir = os.path.join(os.path.dirname(__file__), '..') + "/test_results/"

    def __init__(self, test_case_name):
        self.__test_result = {}
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = KeyWord.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y%m%d_%H:%M:%S"))

    def set_result(self, result):
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        self.__test_result[KeyWord.DURATION] = duration

    def set_step_status(self, step, name, message):
        content = "{0}: {1}".format(str(name), str(message))
        step = KeyWord.STEP + str(step)
        self.__test_result[step] = content

    def write_result_to_file(self):
        filename = "{0}{1}_{3}.json".format(TestReport.result_dir, self.__test_result[KeyWord.TEST_CASE],
                                            self.__test_result[KeyWord.START_TIME])

        with open(filename, "w") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False)

    def set_test_failed(self):
        self.__test_result[KeyWord.RESULT] = KeyWord.FAILED

    def set_test_passed(self):
        self.__test_result[KeyWord.RESULT] = KeyWord.PASSED


class KeyWord:
    TEST_CASE = "testcase"
    RESULT = "result"
    START_TIME = "starttime"
    DURATION = "duration"
    STEP = "step"
    PASSED = "Passed"
    FAILED = "Failed"
