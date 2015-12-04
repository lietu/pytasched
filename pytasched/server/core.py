from pytasched.tools import TickManager
from pytasched.engines import get_storage_engine, get_task_engine
from pytasched.autoreload import set_logger, check, add_reload_hook
import pylibmc
import sherlock


class PytaschedServer(object):
    """
    Main server process that monitors for tasks to run and runs them
    """

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self.storageEngine = None
        self.taskEngine = None
        self.current_lock = None
        self.mc_client = None

    def _setup(self):
        """
        Setup the server components
        """

        self.logger.debug("Setting up storage engine {engine}".format(
            engine=self.settings.STORAGE["engine"]
        ))

        self.storageEngine = get_storage_engine()

        self.logger.debug("Setting up task engine {engine}".format(
            engine=self.settings.TASKS["engine"]
        ))

        self.taskEngine = get_task_engine()

        self.storageEngine.set_logger(self.logger)
        self.taskEngine.set_logger(self.logger)

        set_logger(self.logger)
        add_reload_hook(self.release_locks)

        self.mc_client = pylibmc.Client(self.settings.MEMCACHED)

        sherlock.configure(
            backend=sherlock.backends.MEMCACHED,
            client=self.mc_client
        )

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

        while tm.tick():
            if self.settings.AUTORELOAD:
                check()

            tasks = self.storageEngine.get_task_list()

            if tasks:
                self.logger.debug("Found {} task(s) to process".format(
                    len(tasks)
                ))

            for task in tasks:
                name = "scheduler-Task-" + task.id
                lock = sherlock.Lock(name)

                if lock.acquire(False):
                    try:

                        self.logger.info("Running task {} for {}".format(
                            task.id,
                            task.task
                        ))

                        self.taskEngine.run(task)

                        if task.recurring:
                            self.storageEngine.reschedule(task, recur=True)
                        else:
                            self.storageEngine.remove_task(task.id)
                    finally:
                        lock.release()
                else:
                    self.logger.info("Someone else is running task {}".format(
                        task.id
                    ))
