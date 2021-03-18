import inspect
import logging, logging.config


class LoggerSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(LoggerSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=LoggerSingleton):
    """Logs messages to the console, as well as log files (info and errors).

        Args:
            info_log_file_path: A file path where to save info level messages
                default is /dev/null

            error_log_file_path: A file path where to save error level messages
                default is /dev/null

            debug_logging_level: A boolean, which sets the debug logging level
                default is False
    """

    def __init__(self, info_log='/dev/null', error_log='/dev/null', is_debug=False):
        self._info_log_file_path = info_log
        self._error_log_file_path = error_log
        self._debug_logging_level = is_debug
        self._logger_name = None

        self._init_logger_configuration()

    def _init_logger_configuration(self):
        self._set_config_file(self._info_log_file_path, self._error_log_file_path)
        self._set_debug_logging_level(self._debug_logging_level)

    def _set_config_file(self, info_path, error_path):
        logging_config = create_config_for(info_path, error_path)
        logging.config.dictConfig(logging_config)

    def _set_debug_logging_level(self, debug_logging_level):
        if debug_logging_level:
            logging.root.setLevel(level=logging.DEBUG)

    @property
    def logger_name(self):
        return self._logger_name


    # ===========================================================================
    # Logger actions
    #
    def logger(self, logger_name):
        """Returns actual logging module logger and sets name

        Args:
            logger_name: A string, name of the logger to display in logs
                default is module name of callee obtained by inspect
        """
        self._logger_name = logger_name
        return logging.getLogger(self.logger_name)

    def info(self, msg, logger_name = None, **args):
        self.logger(logger_name).info(msg, **args)

    def warning(self, msg, logger_name = None, **args):
        self.logger(logger_name).warning(msg, **args)

    def error(self, msg, logger_name = None, **args):
        self.logger(logger_name).error(msg, **args)

    def debug(self, msg, logger_name = None, **args):
        self.logger(logger_name).debug(msg, **args)

    def critical(self, msg, logger_name = None, **args):
        self.logger(logger_name).critical(msg, **args)


# =======================
# Config Factory
#
def create_config_for(info_path, error_path):
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'info_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'filename': info_path,
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf-8'
            },
            'error_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'simple',
                'filename': error_path,
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'my_module': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': 'no'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'info_file_handler', 'error_file_handler']
        }
    }
    return logging_config
