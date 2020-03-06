from os import environ

STORAGE = None
LOCKS = environ.get("LOCKS")
STORAGE_ENGINE = environ.get("STORAGE_ENGINE", "pytasched.engines:MongoDBStorageEngine")
SECONDS_PER_TICK = float(environ.get("SECONDS_PER_TICK", "1.0"))

# Comma separated list of memcached server addresses for Sherlock
MEMCACHED = environ.get("MEMCACHED", "").split(",")

# E.g. mongodb://hostname:port/?ssl=True&replicaSet=globaldb
# https://docs.mongodb.com/manual/reference/connection-string/
MONGODB_CONNECTION_STRING = environ.get("MONGODB_CONNECTION_STRING")

# Override to which database and collection to use for storing tasks
MONGODB_DATABASE = environ.get("MONGODB_DATABASE", "pytasched")
MONGODB_COLLECTION = environ.get("MONGODB_COLLECTION", "pytasched_tasks")

if STORAGE_ENGINE == "pytasched.engines:MongoDBStorageEngine":
    if not MONGODB_CONNECTION_STRING:
        raise ValueError(
            "Missing MONGODB_CONNECTION_STRING for use with MongoDBStorageEngine."
        )

    STORAGE = {
        "engine": STORAGE_ENGINE,
        "params": {
            "database": MONGODB_DATABASE,
            "collection": MONGODB_COLLECTION,
            "indices": {},
        },
    }

if LOCKS == "sherlock" and not MEMCACHED:
    raise ValueError("You need to define MEMCACHED for sherlock locks")

if LOCKS == "shylock" and not MONGODB_CONNECTION_STRING:
    raise ValueError("You need to define MONGODB_CONNECTION_STRING for shylock locks")

# This is mostly pointless inside Docker
AUTORELOAD = False

if STORAGE is None:
    raise ValueError(
        "Missing storage configuration, check settings_docker.py for details."
    )
