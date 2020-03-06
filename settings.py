#
# Global default configuration
#
# You can change your settings here, but it's recommended that you use
# settings_local.py in this same directory instead to override the settings.
# This file can then be updated via git or whatever when updates are made to
# the project.
#

# Storage engine configuration.
STORAGE = {
    "engine": "pytasched.engines:MongoDBStorageEngine",
    "params": {"indices": {},},
}

# Task engine configuration
TASKS = {"engine": "pytasched.engines:ShellTaskEngine", "params": {"style": "system",}}

# None if no locks are needed
# "sherlock" - If we should use Sherlock for memcached based locks
# "shylock" - If we should use Shylock for MongoDB based locks
LOCKS = False

# MongoDB connection information, needed if above is "shylock"
MONGODB_CONNECTION_STRING = "mongodb://localhost"
MONGODB_DATABASE = "pytasched"
MONGODB_COLLECTION = "pytasched_tasks"

# Addresses to Memcached servers, needed if above is "sherlock"
MEMCACHED = ["127.0.0.1:11211"]

# How many seconds to wait between checks for tasks to be run
SECONDS_PER_TICK = 1.0

# Auto-reload the app if changes to files are detected
AUTORELOAD = False

try:
    from settings_local import *
except ImportError:
    pass
