from unittest2 import TestCase
from pytasched.engines import _setup_engine, get_storage_engine, \
    get_task_engine, _mongo_item_to_task, _MongoDBCursorWrapper, Engine, \
    StorageEngine, TaskEngine, StorageEngineNotAvailableError, \
    FunctionTaskEngine, ShellTaskEngine


class TestFuncs(TestCase):
    def test_setup_engine(self):
        pass

    def test_get_storage_engine(self):
        pass

    def test_get_task_engine(self):
        pass

    def test_mongo_item_to_task(self):
        pass


class Test_MongoDBCursorWrapper(TestCase):
    def test_list(self):
        pass


class TestEngine(TestCase):
    def test_logger(self):
        pass


class TestStorageEngine(TestCase):
    def test_not_implemented(self):
        pass


class TestMongoDBStorageEngine(TestCase):
    def test_get_db(self):
        pass

    def test_setup(self):
        pass

    def test_add_task(self):
        pass

    def test_get_task(self):
        pass

    def test_get_task_list(self):
        pass

    def test_reschedule(self):
        pass

    def test_remove_task(self):
        pass


class TestTaskEngine(TestCase):
    def test_not_implemented(self):
        pass


class TestFunctionTaskEngine(TestCase):
    def test_run(self):
        pass


class TestShellTaskEngine(TestCase):
    def test_styles(self):
        pass

    def test_run(self):
        pass
