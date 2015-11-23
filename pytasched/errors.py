class PytashcedError(Exception):
    pass


class TaskEngineError(PytashcedError):
    pass


class StorageEngineNotAvailableError(PytashcedError):
    pass
