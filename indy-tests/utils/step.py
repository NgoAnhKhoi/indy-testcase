'''
Created on Nov 20, 2017

@author: khoi.ngo
'''
from utils.report import Status


class Step():

    def __init__(self, step_id, name, status=Status.FAILED, message=""):
        self.__id = step_id
        self.__name = name
        self.__status = status
        self.__message = message

    def set_status(self, status):
        self.__status = status

    def set_name(self, name):
        self.__name = name

    def set_message(self, message):
        self.__message = message

    def to_string(self):
        print("Step ID: " + str(self.__id))
        print("Step Name: " + str(self.__name))
        print("Step Status: " + str(self.__status))
        print("Step Message: " + str(self.__message))
