import sys
import os
import subprocess

from . import status


class BaseJob(object):

    def __init__(self, path, name, script):
        self.path = path
        self.name = name
        self.script = script
        self.last_status = status.READY

    @property
    def config(self):
        return self._file('cfg')

    @property
    def out(self):
        return self._file('out')

    @property
    def err(self):
        return self._file('err')

    @property
    def status(self):
        return self.last_status

    def run(self):
        raise NotImplemented

    def check_config(self):
        return os.path.exists(self.config)

    def _file(self, ext):
        return os.path.join(self.path, self.name + '.' + ext)

    @classmethod
    def from_job(cls, job, *args, **kwargs):  # Basic conversion
        if isinstance(job, cls):
            return job
        return cls(job.path, job.name, job.script, *args, **kwargs)


class Job(BaseJob):
    """Basic job runner.
    """

    def __init__(self, *args):
        super(Job, self).__init__(*args)
        self._process = None

    @property
    def _call_args(self):
        return [sys.executable, self.script, self.config, self.path, self.name]

    def run(self):
        try:
            with open(self.out, 'w+') as out:
                with open(self.err, 'w+') as err:
                    self._process = subprocess.call(self._call_args,
                                                    stdout=out, stderr=err)
        except IOError as e:
            self._process = e

    def wait(self):
        pass

    def _process_status(self):
        if self._process != 0:
            return status.FAILED
        else:
            return status.DONE

    @property
    def status(self):
        if self._process is None:
            return self.last_status
        elif isinstance(self._process, Exception):
            return status.FAILED
        else:
            return self._process_status()
