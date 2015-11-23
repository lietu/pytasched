# PyTaSched

The name is short for Python Task Scheduler.

Yet another tool to help maintain scheduled tasks in a centralized manner. The
core idea is to empower you to schedule tasks how ever much you want into the
future, using various backend systems for both storage and running the tasks.

The main target is using MongoDB for storage and Celery for running the tasks,
but it supports other storage engines and e.g. unix shell commands. Extending
should also be rather easy.

Tested with Python 2.7, should work with 3.3+.

Licensed under MIT and new BSD licenses, more details in `LICENSE.txt`.


## Dependencies
 
There really aren't any dependencies other than what's required for the engines
you want to use. For MongoDB storage you need `pymongo`, and for Celery tasks
you need `celery` installed.

Anyway to install everything supported by the basic system, just run:

```
pip install -r requirements.txt
```


## Usage

### Server

There is a server component that monitors for tasks that need to be executed.
This needs to be running somewhere, preferably constantly, preferably with
multiple servers sharing the responsibility. There are locks in place to stop
one task from being run by multiple servers at the same time.

To run the server you probably want to use something like
[Supervisor](http://supervisord.org/) to make sure it's always up and gets
restarted in case of errors, etc.

Running the server itself is rather easy, just set up an environment with
[Virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) that
has all the requirements installed, and simply run:

```
python -m pytasched
```


### Client

Managing tasks in the queue is fairly simple, however you have to keep the
task engine in mind when implementing. This typically depends on the 
configuration to be done in `pytasched/settings.py` or 
`pytasched/local_settings.py`, but you can also provide the settings as an
argument to `get_storage_engine()` in case you don't want to edit the
distribution.


*Shell:*

Currently the "Shell" engine uses `os.system`, it should be rather easy to
extend that to use e.g. Popen instead.

```python
from pytasched import get_storage_engine, Task

task = Task("id {name}", kwargs={"name": "root"}, seconds=3)

engine = get_storage_engine()
id = engine.add_task(task)

print("Created task {}".format(id))
```


*Celery:*

```python
from pytasched import get_storage_engine, Task

task = Task("workers.tasks:my_celery_task", seconds=3)

engine = get_storage_engine()
id = engine.add_task(task)

print("Created task {}".format(id))
```