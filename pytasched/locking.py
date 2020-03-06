from settings import LOCKS, MEMCACHED, MONGODB_CONNECTION_STRING, MONGODB_DATABASE

try:
    import shylock
except ImportError:
    shylock = None

try:
    import sherlock
except ImportError:
    sherlock = None

try:
    import pylibmc
except ImportError:
    pylibmc = None

try:
    import pymongo
except ImportError:
    pymongo = None


class Lock(object):
    def __init__(self):
        raise NotImplementedError("Trying to use locks but no lock backend configured.")


if LOCKS == "shylock":
    if not shylock:
        raise ValueError("Cannot use shylock locks, shylock is not installed")
    if not pymongo:
        raise ValueError("Cannot use shylock locks, pymongo driver is not available")
    if not MONGODB_CONNECTION_STRING:
        raise ValueError(
            "Cannot use shylock locks, MongoDB connection string is not configured"
        )
    client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
    shylock.configure(shylock.ShylockPymongoBackend.create(client, MONGODB_DATABASE))
    Lock = shylock.Lock
elif LOCKS == "sherlock":
    if not sherlock:
        raise ValueError("Cannot use sherlock locks, sherlock is not installed")
    if not pylibmc:
        raise ValueError("Cannot use sherlock locks, pylibmc is not installed")

    sherlock.configure(
        backend=sherlock.backends.MEMCACHED,
        client=pylibmc.Client(MEMCACHED),
        expire=5 * 60,
    )
    Lock = sherlock.MCLock
