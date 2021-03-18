"""This file contains config necessary to run application instance or test the instance
"""
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) # source/app/root

Config = {
    'root_dir': ROOT_DIR,                  # e.g. '/path/to/app', it is automatically detected, otherwise set it here specifically
    'development_environment': True,       # development_environment: True, False => affects logging level
    'logging_level': 'debug',              # logging_level: 'debug', 'info'
    'logging_dir': './logs/',              # usually './logs'
    'webapi_host': '127.0.0.1',
    'webapi_port': 8080,
    'keras_model_name': 'twitter_to_lang'
}

# Env variables, which the application requires are set/assigned here
os.environ['DEVELOPMENT_ENVIRONMENT'] = str(Config['development_environment'])
