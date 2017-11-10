'''
Created on Nov 9, 2017

@author: khoi.ngo
'''

import json
import time

class TestReport:
    '''
    Contain all functions generating test summary report.
    '''

    def __init__(self, test_case_name):
        self.__test_result = {}
        self.__test_result["testcase"] = test_case_name
        self.__test_result["result"] = "Passed"
        self.__test_result["starttime"] = str(time.strftime("%Y%m%d_%H:%M:%S"))

    def set_result(self, result):
        self.__test_result["result"] = result

    def set_duration(self, duration):
        self.__test_result["duration"] = duration

    def set_step_status(self, step, name, message):
        content = "{0}: {1}".format(str(name), str(message))
        step = "step" + str(step)
        self.__test_result[step] = content

    def write_result_to_file(self, path):
        filename = "{0}{1}_{3}.json".format(str(path), self.__test_result["testcase"],
                                            self.__test_result["starttime"])

        with open(filename, "w") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False)

