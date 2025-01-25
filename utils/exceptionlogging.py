__author__ = "Rohit"
import logging

class ExceptionLogging():
    @staticmethod
    def LogException(exceptionstring, err):
        logging.error('Exception_Reason:' + str(err))
        logging.error('Exception_Traceback:' + exceptionstring)

    @staticmethod
    def LogWarnException(exceptionstring, err):
        logging.error('Exception_Reason:' + str(err))
        logging.error('Exception_Traceback:' + exceptionstring)