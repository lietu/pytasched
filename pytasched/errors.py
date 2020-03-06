from __future__ import unicode_literals


class PytashcedError(Exception):
    pass


class TaskEngineError(PytashcedError):
    pass


class StorageEngineNotAvailableError(PytashcedError):
    pass
