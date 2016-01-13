import time
import subprocess
from threading import Thread

from . import status
from .job import Job
from .pool import Pool


class ProcessJob(Job):
    """To run a job as an external (async) process.
    """

    def _process_status(self):
        return_code = self._process.poll()
        if return_code is None:
            return status.RUNNING
        elif return_code != 0:
            return status.FAILED
        else:
            return status.DONE

    def run(self):
        try:
            out = open(self.out, 'w+')
            err = open(self.err, 'w+')
            self._process = subprocess.Popen(self._call_args, stdout=out,
                                             stderr=err)
        except IOError as e:
            self._process = e

    def wait(self):
        self._process.wait()


class PoolRefreshThread(Thread):

    def __init__(self, jobs, processes, refresh_period=.1):
        super(PoolRefreshThread, self).__init__()
        self.job_queue = jobs
        self.running_jobs = [None] * processes
        self.refresh_period = refresh_period

    def _has_running_jobs(self):
        return (len(self.job_queue) > 0 or
                any([j is not None for j in self.running_jobs]))

    def _clean_finished_jobs(self):
        self.running_jobs = [j if j is None or j.status == status.RUNNING
                             else None for j in self.running_jobs]

    def _get_started_new_job_or_None(self):
        try:
            job = self.job_queue.pop()
            job.run()
            return job
        except IndexError:
            return None

    def _fill_running(self):
        self.running_jobs = [self._get_started_new_job_or_None() if j is None
                             else j for j in self.running_jobs]

    def run(self):
        for job in self.job_queue:
            job.last_status = status.QUEUED
        while self._has_running_jobs():
            self._clean_finished_jobs()
            self._fill_running()
            time.sleep(self.refresh_period)


class MultiprocessPool(Pool):
    """Launch jobs as separate subprocesses.
    """

    def __init__(self, processes=2, refresh_period=.1):
        super(MultiprocessPool, self).__init__()
        self.processes = processes
        self.refresh_period = refresh_period

    def append(self, job):
        super(MultiprocessPool, self).append(ProcessJob.from_job(job))

    def run(self):
        self._thread = PoolRefreshThread(self.jobs[::-1], self.processes,
                                         refresh_period=self.refresh_period)
        self._thread.start()

    def wait(self):
        self._thread.join()
