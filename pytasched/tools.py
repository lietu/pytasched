import sys
import importlib
from time import time, sleep


def get_duration(days=0, hours=0, minutes=0, seconds=0, millis=0):
    """
    Get the given duration in seconds

    :param float|int days:
    :param float|int hours:
    :param float|int minutes:
    :param float|int seconds:
    :param float|int millis:
    :return float: Number of seconds in the duration, incl. fractions
    """

    duration = 0.0

    duration += float(days) * 24 * 60 * 60
    duration += float(hours) * 60 * 60
    duration += float(minutes) * 60
    duration += float(seconds)
    duration += millis / 1000.0

    return duration


class TickManager(object):
    """
    Makes tick-rate limiting of loops easy
    """

    def __init__(self, seconds_per_tick):
        self.seconds_per_tick = seconds_per_tick
        self.sleep_duration = seconds_per_tick / 10
        self.running = True
        self.last_tick = 0

    def tick(self):
        """
        Check if we should still be running, if so, wait until it's time for
        the next tick.

        :return bool: If the iteration should be run or not
        """

        next_tick = self.last_tick + self.seconds_per_tick

        while self.running:
            current_time = time()

            if current_time > next_tick:
                break

            sleep(self.sleep_duration)

        if not self.running:
            return False

        self.last_tick = current_time

        return True

    def stop(self):
        """
        Stop the iterations
        """
        self.running = False


def load_from_module(search_definition):
    """
    Dynamically load the module property as defined by the search parameter.

    :param str search_definition: module.path:property_name
    :raises ValueError: In case configuration is invalid
    :return *: The property searched for
    """

    try:
        module_name, property_name = search_definition.split(":")
    except:
        raise ValueError("Search definition \"{}\" is not valid.".format(
            search_definition
        ))

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ValueError(
            "Search definition \"{}\" is not valid. The module specified "
            "({}) was not found. Original error: {}".format(
                search_definition, module_name, str(e)
            )
        )

    if "." in property_name:
        container, attribute = property_name.split(".")
        try:
            property = getattr(getattr(module, container), attribute)
        except AttributeError:
            raise ValueError(
                "Search definition \"{}\" is not valid. The module does not "
                "contain the specified property.".format(
                    search_definition
                )
            )
    else:
        try:
            property = getattr(module, property_name)
        except AttributeError:
            raise ValueError(
                "Search definition \"{}\" is not valid. The module does not "
                "contain the specified property.".format(
                    search_definition
                )
            )

    return property