import time
import logging

from . import status


class Pool(object):

    def __init__(self):
        self.jobs = []

    def run(self):
        for j in self.jobs:
            j.run()

    def wait(self):
        for j in self.jobs:
            j.wait()

    def append(self, job):
        self.jobs.append(job)

    def extend(self, jobs):
        for j in jobs:
            self.append(j)

    @property
    def status(self):
        return min(self.statuses)

    @property
    def statuses(self):
        return [j.status for j in self.jobs]

    @property
    def status_counts(self):
        statuses = self.statuses
        return [(s, statuses.count(s)) for s in set(statuses)]

    def get_stats(self):
        return "{} ({})".format(
            self.status, ', '.join(["%s: %s" % x for x in self.status_counts]))

    def log_refreshed_stats(self, log=None, period=1):
        if log is None:
            log = logging.warning
        while self.status < status.FAILED:
            last_printed = self.get_stats()
            log(last_printed)
            time.sleep(period)
        log(self.get_stats())
