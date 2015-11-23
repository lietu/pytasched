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


#### Examples of different task engines

##### Shell

Currently the `ShellTaskEngine` uses `os.system`, it should be rather easy to
extend that to use e.g. Popen instead.

```python
from pytasched import get_storage_engine, Task

task = Task("id {name}", kwargs={"name": "root"}, seconds=3)

engine = get_storage_engine()
id = engine.add_task(task)

print("Created task {}".format(id))
```


##### Celery

With `CeleryTaskEngine` you specify the tasks as `module.path:function_name`.
So if it's possible to import `workers.tasks` and it has the task
`my_celery_task` in it, you can use the following:

```python
from pytasched import get_storage_engine, Task

task = Task("workers.tasks:my_celery_task", seconds=3)

engine = get_storage_engine()
id = engine.add_task(task)

print("Created task {}".format(id))
```

You can add stuff to your PYTHONPATH easily in the configuration for this
engine to make this easier.


## Task features

There's a few task-specific things available regardless of storage/task engine.


### Rescheduling and cancelling

It's fairly convenient to reschedule or cancel tasks. For now you'll have
to save the ID somewhere yourself or write your own search logic, but I doubt 
that's going to take a lot of effort.
 
```python
from pytasched import get_storage_engine

engine = get_storage_engine()

task_id = "abcd1234"
task = engine.get_task(task_id)

# Rescheduled to now + previously specified delay
engine.reschedule(task)

# Cancel the task
engine.remove_task(task_id)
```


### Recurring tasks

If you want a task to be automatically rescheduled after it has been completed,
there's a convenience feature that does it for you.
 
```python
from pytasched import get_storage_engine

task = Task("id {name}", kwargs={"name": "root"}, seconds=5, recurring=True)
engine = get_storage_engine()
id = engine.add_task(task)
```

WARNING: It might not be obvious that setting delay to e.g. 5 seconds will NOT
make the task to be automatically run every 5 seconds. Instead, when the task
completes it will be rescheduled to be run 5 seconds later. Also there's delays
between scheduling and execution. If the task takes 5 seconds to run, it will 
be run roughly every 10 seconds.


### Setting delay

You can set the delay in various ways. You can simply set the `wait` time in
seconds (float precision is ok).

```python
Task("w", wait=1.5)
```

Alternatively you can use the various levels of precision to define a time
delay. The options available are `days`, `hours`, `minutes`, `seconds` and
`millis`, all are optional, support floats, and you can freely combine them.
Don't specify the `wait` time if you plan on using these instead.

```python
# Will be run after 14 days
Task("w", days=13.5, hours=11.5, minutes=29.5, seconds=29.5, millis=500)
```
