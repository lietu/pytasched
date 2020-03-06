from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from builtins import next
from builtins import object
from builtins import str
from copy import copy
from logging import DEBUG, INFO
from time import time

import settings as global_settings
from pytasched.errors import StorageEngineNotAvailableError, TaskEngineError
from pytasched.tasks import Task
from pytasched.tools import load_from_module

try:
    import pymongo
    from bson import ObjectId
except ImportError:
    pymongo = None


def _setup_engine(class_definition, params):
    """
    Find an engine based on the definition and return a configured instance

    :param str class_definition:
    :param dict params:
    :return type: Instance of the class based on class_definition
    """

    cls = load_from_module(class_definition)
    return cls(params)


def get_storage_engine(settings=None):
    """
    Get a storage engine for tasks based on settings

    :param module settings: If you want to override global settings
    :return pytasched.engines.StorageEngine: Instance of the engine that's
                                             already configured
    """
    if not settings:
        settings = global_settings

    return _setup_engine(settings.STORAGE["engine"], settings.STORAGE["params"])


def get_task_engine(settings=None):
    """
    Get a task engine for processing tasks based on settings

    :param module settings: If you want to override global settings
    :return TaskEngine: Instance of the engine that's already configured
    """
    if not settings:
        settings = global_settings

    return _setup_engine(settings.TASKS["engine"], settings.TASKS["params"])


def _mongo_item_to_task(item):
    """
    Convert a MongoDB entry to a Task

    :param dict item:
    :return pytasched.tasks.Task:
    """
    return Task(
        id=str(item["_id"]),
        task=item["task"],
        args=item["args"],
        kwargs=item["kwargs"],
        wait=item["wait"],
        recurring=item["recurring"],
        when=item["when"],
    )


class _MongoDBCursorWrapper(object):
    """
    Wraps MongoDB cursor to make it look a bit more like a list of Tasks
    """

    def __init__(self, cursor):
        """
        :param pymongo.cursor.Cursor cursor:
        :return:
        """
        self.cursor = cursor

    def __len__(self):
        return self.cursor.count()

    def __getitem__(self, index):
        return _mongo_item_to_task(self.cursor[index])

    def __iter__(self):
        return self

    def __next__(self):
        return _mongo_item_to_task(next(self.cursor))


class Engine(object):
    """
    Logic common to all engines
    """

    def __init__(self):
        self.logger = None

    def set_logger(self, logger):
        """
        Set a logger instance
        """
        self.logger = logger

    def log(self, level, msg, *args, **kwargs):
        """
        Log something, assuming a logger was set up
        """

        if self.logger:
            self.logger.log(level, msg, *args, **kwargs)


class StorageEngine(Engine):
    """
    Base class for storage engines. Storage engines are responsible for storing
    the information about the tasks, and allow convenient functions to add,
    search, and remove tasks from the schedule.
    """

    def __init__(self, params):
        self.params = params
        super(StorageEngine, self).__init__()

    def setup(self):
        """
        Set up the storage engine, e.g. tables, indexes, etc.
        """
        pass

    def add_task(self, task):
        """
        Add a new task to be processed

        :param pytasched.task.Task task:
        :param float|int days:
        :param float|int hours:
        :param float|int minutes:
        :param float|int seconds:
        :param float|int millis:
        """
        raise NotImplementedError()

    def get_task(self, id):
        """
        Get the specific task

        :param str id:
        :return pytasched.tasks.Task:
        """
        raise NotImplementedError()

    def get_task_list(self):
        """
        Get a list of tasks that need to be run
        :return list:
        """
        raise NotImplementedError()

    def remove_task(self, id):
        """
        Remove a task from the queue

        :param str id: The task ID
        :return bool:
        """
        raise NotImplementedError()

    def has_task_changed(self, task):
        """
        Check if the task has changed / been deleted since it was loaded.

        :param pytasched.tasks.Task task:
        :return bool:
        """
        raise NotImplementedError()

    def reschedule(self, task, recur=False):
        """
        Update task to be rescheduled

        :param pytasched.task.Task task:
        :param bool recur: If this is for recurring and we should try and keep
                           the same schedule
        """
        raise NotImplementedError()


class MongoDBStorageEngine(StorageEngine):
    """
    Storage engine that uses MongoDB to store tasks
    """

    def __init__(self, params, db=None):
        if not pymongo:
            raise StorageEngineNotAvailableError("Could not find pymongo")

        self._db = db
        super(MongoDBStorageEngine, self).__init__(params)

    def _get_db(self):
        if not self._db:
            self.log(DEBUG, "Connecting to MongoDB")

            params = copy(self.params)
            del params["indices"]

            client = pymongo.MongoClient(**params)
            self._db = getattr(client, global_settings.MONGODB_DATABASE)
            self.setup()

        return self._db

    def _get_collection(self):
        """
        Get the collection our tasks are stored in
        :return pymongo.collection.Collection:
        """
        db = self._get_db()
        return getattr(db, global_settings.MONGODB_COLLECTION)

    def _get_now(self):
        """
        Get current time
        """
        return time()

    def set_db(self, db):
        """
        Override the database, if you already have a connection made so we
        don't need to make another one.

        :param pymongo.database.Database db:
        """
        self._db = db

    def setup(self):
        """
        Set up the storage engine, e.g. tables, indexes, etc.
        """
        collection = self._get_collection()

        indices = copy(self.params["indices"])

        if "when" not in indices:
            indices["when"] = {}

        for index in indices:
            self.log(DEBUG, "Ensuring we have index for {}".format(index))

            options = indices[index]
            collection.create_index(index, *options)
            self.log(DEBUG, "Done.")

    def add_task(self, task):
        """
        Add a new task to be processed

        :param pytasched.tasks.Task task:
        :returns str: The ID of the task
        """

        self.log(INFO, "Adding task {} in {}s".format(task.task, task.wait))

        collection = self._get_collection()

        if not task.when:
            task.when = self._get_now() + task.wait

        result = collection.insert_one(
            {
                "task": task.task,
                "args": task.args,
                "kwargs": task.kwargs,
                "wait": task.wait,
                "when": task.when,
                "recurring": task.recurring,
            }
        )

        return str(result.inserted_id)

    def get_task(self, id):
        """
        Get the specific task

        :param str id:
        :return pytasched.tasks.Task:
        """

        collection = self._get_collection()

        item = collection.find_one({"_id": ObjectId(id)})

        if item:
            return _mongo_item_to_task(item)
        else:
            return None

    def get_task_list(self):
        """
        Get the tasks that should be run

        :return list:
        """

        collection = self._get_collection()

        now = self._get_now()

        tasks = collection.find({"when": {"$lt": now}})

        return _MongoDBCursorWrapper(tasks)

    def has_task_changed(self, task):
        """
        Check if the task has changed / been deleted since it was loaded.

        :param pytasched.tasks.Task task:
        :return bool:
        """

        reloaded = self.get_task(task.id)

        if reloaded is None:
            return True

        if reloaded.when != task.when:
            return True

        return False

    def reschedule(self, task, recur=False):
        """
        Update task to be rescheduled

        :param pytasched.task.Task task:
        :param bool recur: If this is for recurring and we should try and keep
                           the same schedule
        """

        if recur:
            task.when = task.when + task.wait
        else:
            task.when = self._get_now() + task.wait

        self.log(
            INFO,
            "Rescheduling task {} for {}".format(task.id, task.get_readable_when()),
        )

        collection = self._get_collection()
        result = collection.update_one(
            {"_id": ObjectId(task.id)}, {"$set": {"when": task.when}}
        )

        return bool(result.modified_count)

    def remove_task(self, id):
        """
        Remove a task from the queue

        :param str id: The task ID
        :return bool:
        """

        self.log(INFO, "Removing task {}".format(id))

        collection = self._get_collection()
        result = collection.delete_one({"_id": ObjectId(id)})

        return bool(result.deleted_count)


class TaskEngine(Engine):
    """
    Engine to execute tasks
    """

    def __init__(self, params):
        self.params = params
        super(TaskEngine, self).__init__()

    def run(self, task):
        """
        Run a task
        :param pytasched.tasks.Task task:
        """
        raise NotImplementedError()


class FunctionTaskEngine(TaskEngine):
    """
    Forward tasks to Python functions
    """

    def __init__(self, params):
        super(FunctionTaskEngine, self).__init__(params)
        self.configured = False

    def _setup(self):
        if not self.configured:
            if "paths" in self.params:
                for path in self.params["paths"]:
                    self.log(DEBUG, "Adding {} to PYTHONPATH".format(path))
                    sys.path.append(path)

            self.configured = True

    def run(self, task):
        """
        Run the given task

        :param pytasched.tasks.Task task:
        """

        self._setup()

        runnable = load_from_module(task.task)
        runnable(*task.get_args(), **task.get_kwargs())


class ShellTaskEngine(TaskEngine):
    """
    Execute tasks as shell commands
    """

    STYLES = ("system",)

    def __init__(self, params):
        super(ShellTaskEngine, self).__init__(params)

        if "style" not in params:
            raise TaskEngineError("Shell style not defined")

        if not params["style"] in self.STYLES:
            raise TaskEngineError(
                "Shell style {} not supported".format(params["style"])
            )

    def run(self, task):
        """
        Run the given task

        :param pytasched.tasks.Task task:
        """
        f = getattr(self, "_run_" + self.params["style"])
        f(task)

    @staticmethod
    def _run_system(task):
        """
        Run commands via os.system

        :param pytasched.tasks.Task task:
        :return:
        """

        cmd = task.task.format(*task.get_args(), **task.get_kwargs())

        print("Running: {}".format(cmd))
        os.system(cmd)
