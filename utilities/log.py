import os

from config.config import Config
from utilities.logger import Logger
from utilities.singleton import Singleton


class Log(metaclass=Singleton):
    """Service, which operates over Logger utility

    Examples:
        1. Simple:
            print("Application started")
            print("Application started", __name__) # pass name of the file to logger
            Log.warning("Application started")
            Log.error("Application started")
            print("Application started {}".format('test'))
            Log.debug("Application started {}".format('test'))
            Log.critical("Application started {}".format('test'))

        2. Print exception info to logs
            try:
                raise Exception()
            except Exception as exc:
                Log.critical('Exception occured: %s' % exc, exc_info=True)
    """

    def __init__(self):
        # 1. Figure out logging level based on environment
        if Config['development_environment']:
            logging_debug_level = True
        else:
            logging_debug_level = False

        # 2. Init logger, set config
        self.logger = Logger(info_log=os.path.join(Config['root_dir'], Config['logging_dir'], 'info.log'),
                             error_log=os.path.join(Config['root_dir'], Config['logging_dir'], 'error.log'),
                             is_debug=logging_debug_level) #TODO: Extract config from here

    @classmethod
    def info(cls, msg, logger_name = None, **args):
        cls = Log()
        cls.logger.info(msg, logger_name, **args)

    @classmethod
    def warning(cls, msg, logger_name = None, **args):
        cls = Log()
        cls.logger.warning(msg, logger_name, **args)

    @classmethod
    def error(cls, msg, logger_name = None, **args):
        cls = Log()
        cls.logger.error(msg, logger_name, **args)

    @classmethod
    def debug(cls, msg, logger_name = None, **args):
        return # NOTE: Logging is disabled
        cls = Log()
        cls.logger.debug(msg, logger_name, **args)

    @classmethod
    def critical(cls, msg, logger_name = None, **args):
        cls = Log()
        cls.logger.critical(msg, logger_name, **args)
