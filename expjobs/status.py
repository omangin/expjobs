class Status(tuple):

    def __new__(_cls, i, n):
        return tuple.__new__(_cls, (i, n))

    def __repr__(self):
        return str(self[1])


NOT_READY = Status(0, 'not-ready')
READY = Status(1, 'ready')
RUNNING = Status(2, 'running')
QUEUED = Status(3, 'queued')
FAILED = Status(4, 'failed')
DONE = Status(5, 'done')
