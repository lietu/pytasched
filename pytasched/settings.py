#
# Global default configuration
#
# You can change your settings here, but it's recommended that you use
# local_settings.py in this same directory instead to override the settings.
# This file can then be updated via git or whatever when updates are made to
# the project.
#

# Storage engine configuration.
STORAGE = {
    "engine": "pytasched.engines:MongoDBStorageEngine",
    "params": {
        "host": "localhost",
        "port": 27017,
        "replica_set": None,
        "database": "pytasched",
        "collection": "tasks",
        "indices": {

        }
    }
}

# Task engine configuration
TASKS = {
    "engine": "pytasched.engines:ShellTaskEngine",
    "params": {
        "style": "system",
    }
}


# How many seconds to wait between checks for tasks to be run
SECONDS_PER_TICK = 1.0


try:
    from pytasched.local_settings import *
except ImportError:
    pass