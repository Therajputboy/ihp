__author__ = "Rohit"
import logging
from utils.logging import logger

class ExceptionLogging():
    @staticmethod
    def LogException(exceptionstring, err):
        logger.error('Exception_Reason:' + str(err))
        logger.error('Exception_Traceback:' + exceptionstring)

    @staticmethod
    def LogWarnException(exceptionstring, err):
        logger.error('Exception_Reason:' + str(err))
        logger.error('Exception_Traceback:' + exceptionstring)