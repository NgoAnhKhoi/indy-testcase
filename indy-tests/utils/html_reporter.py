import os
import json
import datetime
import socket
import platform
import time
import glob
import sys
import subprocess

class Position:
    @staticmethod
    def get_date_position(str_len: int) -> (int, int):
        """
        Return date position in file name
        :param str_len: file name len (include file extension)
        :return: begin and end position of date
        """
        return str_len - 24, str_len - 14

    @staticmethod
    def get_name_position(str_len: int) -> (int, int):
        """
        Return test name position in file name
        :param str_len: file name len (include file extension)
        :return: begin and end position of test name
        """
        return 0, str_len - 25


class FileNameFilter:

    def __init__(self, arg: str):
        self.__filter = {}
        self.__parse_filter(arg)

    def check(self, filename: str) -> bool:
        """
        Check if the file name satisfy the condition
        :param filename:
        :return:
        """
        temp = {"name": True, "date": True}

        if "name" in self.__filter:
            (x, y) = Position.get_name_position(len(filename))
            if not filename[x:y].startswith(self.__filter["name"]):
                temp["name"] = False

        if "date" in self.__filter:
            (x, y) = Position.get_date_position(len(filename))
            if not filename[x:y].startswith(self.__filter["date"]):
                temp["date"] = False

        return all(value is True for value in temp.values())

    def do_filter(self, list_file_name) -> list:
        """
        :param list_file_name: list to filter
        :return: list of file name that satisfy condition
        """
        result = []
        for filename in list_file_name:
            if self.check(os.path.basename(filename)):
                result.append(filename)

        return result

    def get_filter(self):
        return self.__filter

    def __parse_filter(self, arg: str):
        """
        Parse "arg" to list of filter
        Now, just support "name" and "date"
        :param arg:
        :return:
        """
        if not arg:
            return

        list_filter = arg.split("&")
        for f in list_filter:
            temp = f.split("=")
            if len(temp) == 2:
                if temp[0] == "name" or temp[0] == "date":
                    self.__filter[temp[0]] = temp[1]

def get_version(program: str) -> str:
    """
    Return version of a program
    :param program:
    :return: version
    """
    cmd = "dpkg -l | grep '{}'".format(program)
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    (out, err) = process.communicate()
    result = out.decode()
    version = result.split()

    if len(version) >= 3:
        return version[2]
    return None


class HTMLReport:
    __default_dir = os.path.join(os.path.dirname(__file__), "..")

    __json_dir = __default_dir + "/test_output/test_results/"

    __report_dir = __default_dir + "/reporter_summary_report/"

    __head = """<html>
            <head>
             <meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
                <title>Summary Report</title>
                <style type="text/css">table {
                    margin-bottom: 10px;
                    border-collapse: collapse;
                    empty-cells: show
                }   

                th, td {
                    border: 1px solid #009;
                    padding: .25em .5em
                }

                th {
                    text-align: left
                }

                te {
                    border: 1px solid #009;
                    padding: .25em .5em
                    text-align: left
                    color_name: red
                }

                td {
                    vertical-align: top
                }

                table a {
                    font-weight: bold
                }

                .stripe td {
                    background-color: #E6EBF9
                }

                .num {
                    text-align: right
                }

                .passedodd td {
                    background-color: #3F3
                }

                .passedeven td {
                    background-color: #0A0
                }

                .skippedodd td {
                    background-color: #DDD
                }

                .skippedeven td {
                    background-color: #CCC
                }

                .failedodd td, .attn {
                    background-color: #F33
                }

                .failedeven td, .stripe .attn {
                    background-color: #D00
                }

                .stacktrace {
                    white-space: pre;
                    font-family: monospace
                }

                .totop {
                    font-size: 85%;
                    text-align: center;
                    border-bottom: 2px solid #000
                }</style>
            </head>"""

    __end_file = """</html>"""

    __suite_name = """<h3>s_name</h3>"""

    __configuration_table = """<table id="configuration">
            <tbody>
            <tr>
                <th>Run machine</th>
                <td>host_name</td>            
            </tr>
            <tr>
                <th>OS</th>
                <td>os_name</td>
            </tr>
            <tr>
                <th>indy - plenum</th>
                <td>v_plenum</td>            
            </tr>
             <tr>
                <th>indy - anoncreds</th>
                <td>v_anoncreds</td>            
            </tr>
            <tr>
                <th>indy - node</th>
                <td>v_indynode</td>            
            </tr>
            <tr>
                <th>sovrin</th>
                <td>v_sovrin</td>            
            </tr>
            </tbody>
        </table>"""

    __statictics_table = """<table border='1' width='800'>
            <tbody>
            <tr>
                <th>Test Plan</th>
                <th># Passed</th>       
                <th># Failed</th>
                <th>Time (ms)</th>
            </tr>
            <tr>
                <td>plan_name</td>
                <td class="num">passed_num</td>
                <td class="num">failed_num</td>            
                <td class="num">total_time</td>
            </tr>
            </tbody>
        </table>"""

    __passed_testcase_template = """<tr class="passedeven">
                                           <td rowspan="1">tc_name</td>
                                           <td>Passed</td>
                                           <td rowspan="1">tc_starttime</td>
                                           <td rowspan="1">tc_duration</td>
                                       </tr>"""

    __failed_testcase_template = """<tr class="failedeven">
                                            <td rowspan="1">tc_name</td>
                                            <td><a href='#tc_link'>Failed</a></td>
                                            <td rowspan="1">tc_starttime</td>
                                            <td rowspan="1">tc_duration</td>
                                        </tr>"""

    __summary_head = """<h2>Test Summary</h2>
            <table id="summary" border='1' width='800'>
            <thead>
            <tr>
                <th>Test Case</th>
                <th>Status</th>
                <th>Start Time</th>
                <th>Duration (ms)</th>
            </tr>
            </thead>"""

    __go_to_summary = """<a href = #summary>Back to summary.</a>"""

    __begin_summary_content = """ 
            <tbody>
            <tr>
                <th colspan="4"></th>
            </tr>"""

    __end_summary_content = """</tbody>"""

    __end_table = """ </table> """

    __passed_testcase_table = """ """

    __failed_testcase_table = """ """

    __test_log_head = """<h2>Test Execution Logs</h2>"""

    __table_test_log = """<h3 id = "tc_link">test_name</h3>
                            <table id="execution_logs" border='1' width='800'>"""

    __table_test_log_content = """ """

    __passed_test_log = """
            <tr>
                <td><font color="green">step_num : step_name :: step_status</font></td>       
            </tr>"""

    __failed_test_log = """
            <tr>
                <td><font color="red">step_num : step_name :: step_status
                <br>Traceback: error_message</br>
                </font>
                </td>            
            </tr>
            """

    def make_suite_name(self, suite_name):
        # os.path.basename(__file__)
        """
        Generating the statictics table
        :param suite_name:
        """
        time = datetime.datetime.now().time()
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        HTMLReport.__suite_name = HTMLReport.__suite_name.replace("s_name", "Summary_" + date + "_" + str(time))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("plan_name",
                                                                              suite_name + "_" + date + "_" + str(time))

    def make_configurate_table(self):
        """
        Generating the configuration table
        """
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("host_name", socket.gethostname())
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("os_name", os.name + platform.system() + platform.release())
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_plenum",
                                                                                    get_version("indy-plenum"))
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_anoncreds",
                                                                                    get_version("indy-anoncreds"))
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_indynode",
                                                                                    get_version("indy-node"))
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_sovrin", get_version("sovrin"))
        # dpkg -l | grep 'indy-plenum'
        # dpkg -l | grep 'indy-anoncreds'
        # dpkg -l | grep 'indy-node'
        # dpkg -l | grep 'sovrin'

    def make_report_content(self, path_to_json):
        """
        Generating the report content by reading all json file within the inputted path
        :param path_to_json:
        """

        # this finds our json files
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        passed = 0
        failed = 0
        total = 0

        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                json_text = json.load(json_file)

                # summary item
                testcase = json_text['testcase']
                result = json_text['result']
                starttime = json_text['starttime']
                duration = json_text['duration']

                # staticticTable items
                total = total + int(duration)
                if result == "Passed":
                    passed = passed + 1

                    temp_testcase = HTMLReport.__passed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    # Add passed test case into  table
                    HTMLReport.__passed_testcase_table = HTMLReport.__passed_testcase_table + temp_testcase

                elif result == "Failed":
                    failed = failed + 1

                    temp_testcase = HTMLReport.__failed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    temp_testcase = temp_testcase.replace("tc_link", testcase.replace(" ", ""))
                    # Add failed test case into  table
                    HTMLReport.__failed_testcase_table = HTMLReport.__failed_testcase_table + temp_testcase

                    test_log = HTMLReport.__table_test_log
                    test_log = test_log.replace("test_name", testcase)
                    test_log = test_log.replace("tc_link", testcase.replace(" ", ""))

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + test_log

                    # loop for each step
                    for i in range(0, len(json_text['run'])):
                        if (json_text['run'][i]['status'] == "Passed"):
                            temp = HTMLReport.__passed_test_log
                        else:
                            temp = HTMLReport.__failed_test_log
                            temp = temp.replace("error_message", json_text['run'][i]['message'])

                        temp = temp.replace("step_num", str(i + 1))
                        temp = temp.replace("step_name", json_text['run'][i]['step'])
                        temp = temp.replace("step_status", json_text['run'][i]['status'])
                        HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + temp

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + HTMLReport.__end_table + HTMLReport.__go_to_summary

        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("plan_name", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("passed_num", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("failed_num", str(failed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("total_time", str(total))

    def make_report_content_by_list(self, list_json: list):
        """
        Generating the report content by reading all json file within the inputted path
        :param list_json:
        """
        if not list_json:
            return

        passed = 0
        failed = 0
        total = 0

        for js in list_json:
            with open(js) as json_file:
                json_text = json.load(json_file)

                # summary item
                testcase = json_text['testcase']
                result = json_text['result']
                starttime = json_text['starttime']
                duration = json_text['duration']

                # staticticTable items
                total = total + int(duration)
                if result == "Passed":
                    passed = passed + 1

                    temp_testcase = HTMLReport.__passed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    # Add passed test case into  table
                    HTMLReport.__passed_testcase_table = HTMLReport.__passed_testcase_table + temp_testcase

                elif result == "Failed":
                    failed = failed + 1

                    temp_testcase = HTMLReport.__failed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    temp_testcase = temp_testcase.replace("tc_link", testcase.replace(" ", ""))
                    # Add failed test case into  table
                    HTMLReport.__failed_testcase_table = HTMLReport.__failed_testcase_table + temp_testcase

                    test_log = HTMLReport.__table_test_log
                    test_log = test_log.replace("test_name", testcase)
                    test_log = test_log.replace("tc_link", testcase.replace(" ", ""))

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + test_log

                    # loop for each step
                    for i in range(0, len(json_text['run'])):
                        if (json_text['run'][i]['status'] == "Passed"):
                            temp = HTMLReport.__passed_test_log
                        else:
                            temp = HTMLReport.__failed_test_log
                            temp = temp.replace("error_message", json_text['run'][i]['message'])

                        temp = temp.replace("step_num", str(i + 1))
                        temp = temp.replace("step_name", json_text['run'][i]['step'])
                        temp = temp.replace("step_status", json_text['run'][i]['status'])
                        HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + temp

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + HTMLReport.__end_table + HTMLReport.__go_to_summary

        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("plan_name", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("passed_num", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("failed_num", str(failed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("total_time", str(total))

    def make_html_report(self, json_folder, suite_name):
        """
        Generating completely the report.
        :param json_folder:
        :param suite_name:
        """

        self.make_suite_name(suite_name)
        self.make_configurate_table()
        self.make_report_content(json_folder)

        # Write to file.
        print("Refer to " + json_folder + '/summary.html')
        f = open(json_folder + '/summary.html', 'w')
        f.write(
            HTMLReport.__head + HTMLReport.__suite_name + HTMLReport.__configuration_table + HTMLReport.__statictics_table + HTMLReport.__summary_head + HTMLReport.__begin_summary_content + HTMLReport.__passed_testcase_table + HTMLReport.__end_summary_content + HTMLReport.__begin_summary_content + HTMLReport.__failed_testcase_table + HTMLReport.__end_summary_content + HTMLReport.__end_table + HTMLReport.__test_log_head +
            HTMLReport.__table_test_log_content + HTMLReport.__end_file)

        f.close()

    def __init__(self):
        self.__filter = None

    def create_result_folder(self, test_name):
        """
        Creating the folder for html summary report.
        :param test_name:
        :return: the actual folder path
        """
        temp_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"
        temp_dir = "{0}{1}_{2}".format(temp_dir, test_name, str(time.strftime("%Y-%m-%d_%H-%M-%S")))
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir)
            except IOError as E:
                print(str(E))
                raise E
        return temp_dir

    def generate_report(self, json_filter: str):
        print("Generating a html report...")
        self.__filter = FileNameFilter(json_filter)
        list_file_name = glob.glob(HTMLReport.__json_dir + "*.json")
        list_file_name = self.__filter.do_filter(list_file_name)
        report_file_name = self.__make_report_name(self.__filter.get_filter())
        self.make_suite_name(report_file_name)
        self.make_configurate_table()
        self.make_report_content_by_list(list_file_name)

        # Write to file.
        print(("Refer to " + self.__report_dir + "/{}.html").format(report_file_name))
        f = open((self.__report_dir + "/{}.html").format(report_file_name), 'w')
        f.write(
            HTMLReport.__head + HTMLReport.__suite_name +
            HTMLReport.__configuration_table +
            HTMLReport.__statictics_table +
            HTMLReport.__summary_head +
            HTMLReport.__begin_summary_content +
            HTMLReport.__passed_testcase_table +
            HTMLReport.__end_summary_content +
            HTMLReport.__begin_summary_content +
            HTMLReport.__failed_testcase_table +
            HTMLReport.__end_summary_content +
            HTMLReport.__end_table +
            HTMLReport.__test_log_head +
            HTMLReport.__table_test_log_content +
            HTMLReport.__end_file)

        f.close()

    def __make_report_name(self, json_filter: dict) -> str:
        """
        Generate report name from filter
        :param json_filter:
        :return:
        """
        name = ""
        if "name" in json_filter:
            name += json_filter["name"]

        if "date" in json_filter:
            if name is not "":
                name += "_"
            name = "{}{}".format(name, json_filter["date"])

        if name is not "":
            name += "_"
        name = "{}{}".format(name, "summary")

        return name


def print_help():
    content = "\nGenerate html report from serveral json files\n\n" \
              "-help: print help\n\n" \
              "-filter: the condition that allow you to filtering the json file that is used to make " \
              "html report\n" \
              "Syntax: -filter \"[filter_name=value]|[filter_name=value]\"\n" \
              "Example: -filter \"name=Test_senario_09&date=2017-11-16\"\n" \
              "With this filter, the HTMLReporter will select the json files that relate with scenario_09 run " \
              "on 2017-11-16 to make html report.\n" \
              "Note: format of date is yyyy-MM-dd\n\n"
    print(content)


if __name__ == "__main__":
    args = sys.argv
    if "-help" in args:
        print_help()
        exit(0)

    reporter = HTMLReport()
    json_filter = None
    if "-filter" in args:
        index = args.index("-filter")
        if index + 1 < len(args):
            json_filter = args[index + 1]

    reporter.generate_report(json_filter)
