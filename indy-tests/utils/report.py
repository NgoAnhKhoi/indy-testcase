"""
Created on Nov 9, 2017

@author: nhan.nguyen
"""

import json
import time
import os
import sys
import logging


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


class Printer(object):
    """
    Class that write content to several file.
    Use this class when you want to write log
    not only on console but only on some other files.
    """
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        """
        Write a content into several files.

        :param obj: content you want to write.
        """
        for f in self.files:
            f.write(obj)
            f.flush()  # Want this content is displayed immediately on file

    def flush(self):
        for f in self.files:
            f.flush()


class TestReport:
    __default_result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_output/"
    __json_dir = __default_result_dir + "test_results/"
    __log_dir = __default_result_dir + "log_files/"
    __log_level = logging.DEBUG

    def __init__(self, test_case_name):
        """
        Constructor of a TestReport instance.

        :param test_case_name:
        """
        self.__test_result = {}  # Store information of a test case
        self.__run = []  # Store information of steps in test case
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = Status.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y-%m-%d_%H-%M-%S"))
        self.__log_file_path = ""
        self.__log = None
        self.__original_stdout = None
        self.__json_file_path = ""

    def set_result(self, result):
        """
        Set a result (PASSED or FAILED) for test case.

        :param result:
        """
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        """
        Set duration for test.

        :param duration: (second)
        """
        self.__test_result[KeyWord.DURATION] = round(duration * 1000)

    def set_step_status(self, step_summary: str, status: str = Status.PASSED, message: str = None):
        """
        Set status and message for specify step.

        :param step_summary: title of step.
        :param status: PASSED or FAILED.
        :param message: anything that involve to step like Exception, Log,...
        """
        temp = {KeyWord.STEP: step_summary, KeyWord.STATUS: status, KeyWord.MESSAGE: message}
        self.__run.append(temp)

    def setup_json_report(self):
        """
        Create the result folder for json and log file
        """
        self.__log_file_path = "{0}/{1}_{2}.log".format(TestReport.__log_dir, self.__test_result[KeyWord.TEST_CASE],
                                                        self.__test_result[KeyWord.START_TIME])
        self.__json_file_path = "{0}/{1}_{2}.json".format(TestReport.__json_dir, self.__test_result[KeyWord.TEST_CASE],
                                                          self.__test_result[KeyWord.START_TIME])
        self.__log = open(self.__log_file_path, "w")
        self.__original_stdout = sys.stdout
        sys.stdout = Printer(sys.stdout, self.__log)
        logging.basicConfig(stream=sys.stdout, level=TestReport.__log_level)

    def write_result_to_file(self):
        """
        Write the result as json and log file to folder.
        If test status is PASSED, delete log file.
        """
        self.__log.close()
        if self.__test_result[KeyWord.RESULT] == Status.PASSED:
            if os.path.isfile(self.__log_file_path):
                os.remove(self.__log_file_path)
        sys.stdout = self.__original_stdout

        self.__test_result[KeyWord.RUN] = self.__run
        with open(self.__json_file_path, "w+") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False, indent=2)

    def set_test_failed(self):
        """
        Set status of test to FAILED.
        """
        self.set_result(Status.FAILED)

    def set_test_passed(self):
        """
        Set status of test to PASSED.
        """
        self.set_test_passed(Status.PASSED)

    @staticmethod
    def change_result_dir(new_dir: str):
        """
        It will be used when you want to run multiple test case.
        Change the path where the tests save the result.

        :param new_dir:
        """
        if new_dir != "":
            if not new_dir.endswith("/"):
                new_dir += "/"
            TestReport.__result_dir = new_dir
