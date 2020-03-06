#!/usr/bin/env python
from __future__ import print_function
from builtins import str
from argparse import ArgumentParser
from pytasched import get_storage_engine, Task

if __name__ == "__main__":
    ap = ArgumentParser()

    ap.add_argument("task", help="Task to be run, module.path:function")
    ap.add_argument(
        "--seconds",
        type=float,
        help="In how many seconds to run the task at, if"
        "recurring determines the frequency.",
    )
    ap.add_argument(
        "--when", type=float, help="The Unix timestamp for when to run the task"
    )
    ap.add_argument("--recurring", action="store_true", help="Make the task recurring")
    ap.add_argument("--args", help="Comma separated list of arguments")
    ap.set_defaults(recurring=False, args=[])

    options = ap.parse_args()
    if not (options.when or options.seconds):
        ap.error("Either seconds or when must be specified.")

    if options.recurring and not options.seconds:
        ap.error("Seconds must be specified for recurring tasks.")

    # Create new task according to spec
    task = Task(
        options.task,
        args=options.args.split(","),
        recurring=options.recurring,
        seconds=options.seconds if options.seconds else 0,
        when=options.when,
    )

    # Schedule and reload
    engine = get_storage_engine()
    id = engine.add_task(task)
    task = engine.get_task(id)

    print("Created task: {}".format(str(task)))
    print("")
    print("Task scheduled for {}".format(task.get_readable_when()))
