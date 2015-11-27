"""
Automatically reload code if changes are detected. Based on Tornado's
autoreload module, simplified to not depend on Tornado.

https://github.com/tornadoweb/tornado/blob/master/tornado/autoreload.py
"""

import os
import sys
import types
import subprocess

try:
    import signal
except ImportError:
    signal = None

# os.execv is broken on Windows and can't properly parse command line
# arguments and executable name if they contain whitespaces. subprocess
# fixes that behavior.
# This distinction is also important because when we use execv, we want to
# close the IOLoop and all its file descriptors, to guard against any
# file descriptors that were not set CLOEXEC. When execv is not available,
# we must not close the IOLoop because we want the process to exit cleanly.
_has_execv = sys.platform != 'win32'

_reload_attempted = False
_modify_times = {}
_reload_hooks = []
logger = None


def check():
    """
    Check for code changes, reload if any changes are found.
    """
    _reload_on_update(_modify_times)


def add_reload_hook(callback):
    """
    Add a hook to be run when the code is reloaded. E.g. to release file
    handles or locks.
    :param function callback:
    """
    _reload_hooks.append(callback)


def set_logger(new_logger):
    """
    Set the logger instance to use for, well, logging.
    :param logging.Logger new_logger:
    """
    global logger
    logger = new_logger


def _reload_on_update(modify_times):
    if _reload_attempted:
        # We already tried to reload and it didn't work, so don't try again.
        return
    for module in list(sys.modules.values()):
        # Some modules play games with sys.modules (e.g. email/__init__.py
        # in the standard library), and occasionally this can cause strange
        # failures in getattr.  Just ignore anything that's not an ordinary
        # module.
        if not isinstance(module, types.ModuleType):
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        if path.endswith(".pyc") or path.endswith(".pyo"):
            path = path[:-1]
        _check_file(modify_times, path)


def _check_file(modify_times, path):
    try:
        modified = os.stat(path).st_mtime
    except Exception:
        return
    if path not in modify_times:
        modify_times[path] = modified
        return
    if modify_times[path] != modified:
        if logger:
            logger.info("%s modified; restarting server", path)
        _reload()


def _reload():
    global _reload_attempted
    _reload_attempted = True
    for fn in _reload_hooks:
        fn()
    if hasattr(signal, "setitimer"):
        # Clear the alarm signal set by
        # ioloop.set_blocking_log_threshold so it doesn't fire
        # after the exec.
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
    # sys.path fixes: see comments at top of file.  If sys.path[0] is an empty
    # string, we were (probably) invoked with -m and the effective path
    # is about to change on re-exec.  Add the current directory to $PYTHONPATH
    # to ensure that the new process sees the same path we did.
    path_prefix = '.' + os.pathsep
    if (sys.path[0] == '' and
            not os.environ.get("PYTHONPATH", "").startswith(path_prefix)):
        os.environ["PYTHONPATH"] = (path_prefix +
                                    os.environ.get("PYTHONPATH", ""))
    if not _has_execv:
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    else:
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            # Mac OS X versions prior to 10.6 do not support execv in
            # a process that contains multiple threads.  Instead of
            # re-executing in the current process, start a new one
            # and cause the current process to exit.  This isn't
            # ideal since the new process is detached from the parent
            # terminal and thus cannot easily be killed with ctrl-C,
            # but it's better than not being able to autoreload at
            # all.
            # Unfortunately the errno returned in this case does not
            # appear to be consistent, so we can't easily check for
            # this error specifically.
            os.spawnv(os.P_NOWAIT, sys.executable,
                      [sys.executable] + sys.argv)
            # At this point the IOLoop has been closed and finally
            # blocks will experience errors if we allow the stack to
            # unwind, so just exit uncleanly.
            os._exit(0)
