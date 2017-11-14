'''
Created on Nov 9, 2017

@author: nhan.nguyen
'''

import json
import time
import os


class TestReport:
    result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"

    def __init__(self, test_case_name):
        self.__error_id = 1
        self.__test_result = {}
        self.__run = []
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = Status.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y%m%d_%H-%M-%S"))

    def set_result(self, result):
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        self.__test_result[KeyWord.DURATION] = duration

    def set_step_status(self, step_summary: str, status, message: str = None):
        temp = {KeyWord.STEP: step_summary, KeyWord.STATUS: status, KeyWord.MESSAGE: message}
        self.__run.append(temp)

    def write_result_to_file(self):
        filename = "{0}{1}_{2}.json".format(TestReport.result_dir, self.__test_result[KeyWord.TEST_CASE],
                                            self.__test_result[KeyWord.START_TIME])
        self.__test_result[KeyWord.RUN] = self.__run
        with open(filename, "w+") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False)

    def set_test_failed(self):
        self.set_result(Status.FAILED)

    def set_test_passed(self):
        self.set_test_passed(Status.PASSED)

    @staticmethod
    def change_result_dir(new_dir):
        TestReport.result_dir = new_dir


class KeyWord:
    TEST_CASE = "testcase"
    RESULT = "result"
    START_TIME = "starttime"
    DURATION = "duration"
    RUN = "run"
    STEP = "step"
    STATUS = "status"
    MESSAGE = "message"


class Status:
    PASSED = "Passed"
    FAILED = "Failed"
