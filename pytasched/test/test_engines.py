from unittest2 import TestCase
from mock import Mock
import mongomock
from pytasched.tasks import Task
from pytasched.engines import _setup_engine, get_storage_engine, \
    get_task_engine, _mongo_item_to_task, _MongoDBCursorWrapper, Engine, \
    StorageEngine, TaskEngine, StorageEngineNotAvailableError, \
    FunctionTaskEngine, ShellTaskEngine, MongoDBStorageEngine


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
    def setUp(self):
        client = mongomock.MongoClient()
        params = {
            "collection": "tasks"
        }

        self.engine = MongoDBStorageEngine(params, db=client.biddl)

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

    def test_has_task_changed(self):
        original = Task("foo", seconds=5)

        # Test that if it's not changed it looks fine
        task_id = self.engine.add_task(original)

        loaded = self.engine.get_task(task_id)
        self.assertFalse(self.engine.has_task_changed(loaded))

        # Deleting should say it's been changed
        self.engine.remove_task(task_id)
        self.assertTrue(self.engine.has_task_changed(loaded))

        task_id = self.engine.add_task(original)

        # Rescheduling should say it's been changed
        loaded = self.engine.get_task(task_id)
        loaded2 = self.engine.get_task(task_id)

        self.engine._get_now = Mock(return_value=999999999)
        self.engine.reschedule(loaded2)

        self.assertTrue(self.engine.has_task_changed(loaded))


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
