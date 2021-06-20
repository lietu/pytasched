# PyTaSched

The name is short for Python Task Scheduler.

Yet another tool to help maintain scheduled tasks in a centralized manner. The
core idea is to empower you to schedule tasks how ever much you want into the
future, using various backend systems for both storage and running the tasks.

The main target is using MongoDB for storage and Celery for running the tasks.
However, extending is rather easy and the "Celery support" is just generic
Python function call and using it for other purposes should be extremely simple.

Tested with Python 2.7, should work with 3.3+.

Licensed under MIT and new BSD licenses, more details in `LICENSE.txt`.


## Dependencies
 
You can install the dependencies easily with [poetry](https://python-poetry.org):

```bash
poetry install
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

However, to launch it for testing purposes just run

```
poetry run python -m pytasched
```


## Deploying to Kubernetes

For Kubernetes you should create the necessary secrets in advance:

```bash
kubectl create secret generic pytasched-secrets "--from-literal=MONGODB_CONNECTION_STRING=mongodb://localhost"
```

You might want to use [sealed-secrets](https://github.com/bitnami-labs/sealed-secrets) to manage them safely.

Check out the `pytasched-config` in `kube_example/pytasched.yaml` for configuration options.

If you're going to need to call code from Celery, copy the relevant code to the Docker container by e.g. prior to running `docker build` copying the content as subfolders here, then modify the `Dockerfile` or `docker-runtime-entrypoint.sh` to append `PYTHONPATH` appropriately. If you use a custom Docker build, update the image in `kube_example/pytasched.yaml` appropriately.

E.g. if you have Celery workers in a package called `workers`, you could do something like

```bash
# In Dockerfile's runtime environment add
ENV PYTHONPATH="workers"

# build.sh
cp -r ../workers .
docker build . -t pytasched
```

You will likely have to update the image in the Kubernetes deployment to point to your private registry.


### Minikube

For local testing and development, you can use [minikube](https://github.com/kubernetes/minikube), and ensure your Docker environment is configured appropriately:

```bash
minikube docker-env
# and follow instructions
```

Then you can build the Docker image:

```bash
docker build . -t pytasched
```

And either run the image as is:

```bash
docker run --rm -e "MONGODB_CONNECTION_STRING=mongodb://..." -it pytasched
```

Or deploy it in your Kubernetes

```bash
kubectl apply -f kube_example/pytasched.yaml
```

In minikube you should see 1/2 pods launching successfully - the other will refuse to launch because in minikube you only have one host node, and there is little benefit in running more than 1 instance per host pod.


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


##### Functions

With `FunctionTaskEngine` you specify the tasks as `module.path:function_name`
or `module.path:container.attribute`. So if it's possible to import 
`workers.tasks` and it has the task `my_celery_task` in it, you can use the 
following:

```python
from pytasched import get_storage_engine, Task

task = Task("workers.tasks:my_celery_task.delay", seconds=3)

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

You can also set it to recur at a specific interval starting at a specific time
by also defining `when`.

```python
from pytasched import get_storage_engine
from time import time

task = Task("id {}", args=[root], seconds=15, when=time() + 60, recurring=True)
engine = get_storage_engine()
id = engine.add_task(task)
```


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


# Financial support

This project has been made possible thanks to [Cocreators](https://cocreators.ee) and [Lietu](https://lietu.net). You can help us continue our open source work by supporting us on [Buy me a coffee](https://www.buymeacoffee.com/cocreators).

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cocreators)

