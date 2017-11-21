'''
Created on Nov 20, 2017

@author: khoi.ngo
'''


class Step():

    from utils.report import Status

    def __init__(self, step_id, name, status=Status.FAILED, message=""):
        self.__id = step_id
        self.__name = name
        self.__status = status
        self.__message = message

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_status(self):
        return self.__status

    def get_message(self):
        return self.__message

    def set_status(self, status):
        self.__status = status

    def set_name(self, name):
        from utils.constant import Colors
        print(Colors.HEADER + "\n{0}. {1}\n".format(self.__id, name) + Colors.ENDC)
        self.__name = name

    def set_message(self, message):
        self.__message = message

    def to_string(self):
        print("Step ID: " + str(self.__id))
        print("Step Name: " + str(self.__name))
        print("Step Status: " + str(self.__status))
        print("Step Message: " + str(self.__message))
