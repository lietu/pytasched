from __future__ import unicode_literals
from builtins import object
from pytasched.tools import TickManager
from pytasched.engines import get_storage_engine, get_task_engine
from pytasched.autoreload import set_logger, check, add_reload_hook
from pytasched.locking import Lock


class _TaskChanged(Exception):
    """Skip a task"""

    pass


class PytaschedServer(object):
    """
    Main server process that monitors for tasks to run and runs them
    """

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self.storage_engine = None
        self.task_engine = None
        self.current_lock = None

    def _setup(self):
        """
        Setup the server components
        """

        self.logger.debug(
            "Setting up storage engine {engine}".format(
                engine=self.settings.STORAGE["engine"]
            )
        )

        self.storage_engine = get_storage_engine()

        self.logger.debug(
            "Setting up task engine {engine}".format(
                engine=self.settings.TASKS["engine"]
            )
        )

        self.task_engine = get_task_engine()

        self.storage_engine.set_logger(self.logger)
        self.task_engine.set_logger(self.logger)

        set_logger(self.logger)
        add_reload_hook(self.release_locks)

    def release_locks(self):
        """
        Release any lock being held
        """
        if self.current_lock:
            self.current_lock.unlock()

    def run(self):
        """
        Run the monitor
        """

        self._setup()

        tm = TickManager(self.settings.SECONDS_PER_TICK)

        self.logger.info("Waiting for tasks...")

        no_locks = not self.settings.LOCKS
        lock = None

        while tm.tick():
            if self.settings.AUTORELOAD:
                check()

            tasks = self.storage_engine.get_task_list()

            if tasks:
                self.logger.debug("Found {} task(s) to process".format(len(tasks)))

            for task in tasks:
                name = "PyTaSched-Task-" + task.id

                if not no_locks:
                    lock = Lock(name)

                if no_locks or lock.acquire(False):
                    try:
                        if self.storage_engine.has_task_changed(task):
                            raise _TaskChanged()

                        self.logger.info(
                            "Running task {} for {}".format(task.id, task.task)
                        )

                        self.task_engine.run(task)

                        if task.recurring:
                            self.storage_engine.reschedule(task, recur=True)
                        else:
                            self.storage_engine.remove_task(task.id)
                    except _TaskChanged:
                        self.logger.debug(
                            "Seems like task {} was changed, "
                            "skipping for now".format(task.id)
                        )
                    finally:
                        if not no_locks:
                            lock.release()
                else:
                    self.logger.debug("Someone else is running task {}".format(task.id))
