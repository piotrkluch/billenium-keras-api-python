"""This file contains usefull paths variables

Every directory has no trailing slashes at the end, e.g.:
".../Projects/app"
".../Projects/app/application"
".../Projects/app/temp"
"""
import os


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# =============================================================================
# Directories
#
MODELS_DIR = os.path.join(ROOT_DIR, "resources/models")
TEMP_DIR = os.path.join(ROOT_DIR, "tmp")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
DATABASE_DIR = os.path.join(ROOT_DIR, "database")
WEBAPI_DIR = os.path.join(ROOT_DIR, "webapi")

# =============================================================================
# Files
#
INFO_LOG_FILE = os.path.join(LOGS_DIR, "info.log")
ERRORS_LOG_FILE = os.path.join(LOGS_DIR, "error.log")


paths = {
    'directories': {
        'root_dir': ROOT_DIR,
        'models_dir': MODELS_DIR,
        'temp_dir': TEMP_DIR,
        'logs_dir': LOGS_DIR,
        'database_dir': DATABASE_DIR,
        'webapi_dir': WEBAPI_DIR
    },
    'files': {
        'info_log_file': INFO_LOG_FILE,
        'errors_log_file': ERRORS_LOG_FILE
    }
}

class Paths:
    directories = paths['directories']
    files = paths['files']
