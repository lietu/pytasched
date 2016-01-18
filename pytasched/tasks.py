import json
from datetime import datetime
from pytasched.tools import get_duration
import pytasched


class Task(object):
    """
    Container for all task specific information
    """

    def __init__(self, task, args=None, kwargs=None, id=None, wait=None,
                 recurring=False, days=0, hours=0, minutes=0, seconds=0,
                 millis=0, when=None):
        """
        Create a new task. Should be used with the configured task engine in
        mind.

        :param str task: The task to be executed
        :param list args: Arguments to pass to the task
        :param dict kwargs: Keyword arguments to pass to the task
        :param str id: Task ID
        :param float wait: Number of seconds from now until execution
        :param bool recurring: If the task should be recurring
        :param float days: Define duration in days
        :param float hours: Define duration in hours
        :param float minutes: Define duration in minutes
        :param float seconds: Define duration in seconds
        :param float millis: Define duration in milliseconds
        :return:
        """
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.id = id
        self.recurring = recurring
        self.when = when

        if wait:
            self.wait = wait
        else:
            self.wait = get_duration(days, hours, minutes, seconds, millis)

    def get_args(self):
        """
        Get the task args to be used in function calling
        :return list:
        """
        return self.args if self.args else []

    def get_kwargs(self):
        """
        Get the task kwargs to be used in function calling
        :return dict:
        """
        return self.kwargs if self.kwargs else {}

    def get_readable_when(self):
        """
        Get a human readable ISO-8601 timestamp in UTC for when the task is
        scheduled to be executed.

        :return str:
        """
        dt = datetime.utcfromtimestamp(self.when)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def add(self):
        """
        Add this Task to the default storage engine and return it's ID
        :return str: ID
        """

        engine = pytasched.get_storage_engine()
        self.id = engine.add_task(self)
        return self.id

    def remove(self):
        """
        Remove this Task from the default storage engine
        :return bool:
        """

        engine = pytasched.get_storage_engine()
        return engine.remove_task(self.id)

    def __str__(self):
        return '<Task ({})>'.format(json.dumps({
            "id": self.id,
            "task": self.task,
            "args": self.args,
            "kwargs": self.kwargs,
            "wait": self.wait,
            "recurring": self.recurring,
            "when": self.get_readable_when()
        }))
