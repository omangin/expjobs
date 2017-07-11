"""Tools to launch jobs on a torque cluster.
"""


import os
import stat
import subprocess

from . import status
from . import qstat
from .job import BaseJob
from .pool import Pool


def has_qsub():
    with open(os.devnull) as devnull:
        return subprocess.call(['which', 'qsub'], stdout=devnull,
                               stderr=devnull) == 0


class TorqueJob(BaseJob):

    """walltime in minutes.
    """

    PREAMBLE = '#!/bin/sh\n\n'\
               '#PBS -N {}\n'\
               '#PBS -l walltime={}\n\n'
    PYTHON = 'python'

    def __init__(self, path, name, script, walltime=60, job_id=None):
        super(TorqueJob, self).__init__(path, name, script)
        self.walltime = walltime
        # _job_id: (bool, None or int or str)
        # _job_id[0]: qsub success
        # _job_id[1]: if success job id, if failed error code or stdout
        if job_id is None:
            self.load_job_id()
        else:
            self.job_id = job_id

    @property
    def pbs(self):
        return self._file('pbs')

    @property
    def id_file(self):
        return self._file('pbs.id')

    @property
    def qsub_success(self):
        return self._job_id[0]

    @property
    def job_id(self):
        assert(self.qsub_success)
        return self._job_id[1]

    @job_id.setter
    def job_id(self, i):
        self._job_id = (True, i)

    def set_qsub_error(self, err):
        self._job_id = (False, err)

    def load_job_id(self):
        try:
            with open(self.id_file, 'r+') as f:
                self.job_id = int(f.read())
        except IOError:
            self._job_id = (False, None)  # Means qsub has not been called

    def get_exit_code_file(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        return self._file("{}.exitcode".format(job_id))

    def get_exit_code(self):
        with open(self.get_exit_code_file(), 'r+') as f:
            return int(f.read())

    def get_walltime_str(self):
        return "{:d}:{:02d}:00".format(self.walltime // 60, self.walltime % 60)

    def _format_preamble(self):
        return self.PREAMBLE.format(self.name, self.get_walltime_str())

    def get_PBS(self):
        # Code to launch experiment
        code = self._format_preamble()
        code += "({} {} {} {} {} 1>{} 2>{})\n".format(self.PYTHON, self.script,
                                                      self.config, self.path,
                                                      self.name, self.out,
                                                      self.err)
        code += "EXIT_CODE=$?\n"
        code += "echo $EXIT_CODE > {}\n".format(self.get_exit_code_file(
            '$(echo $PBS_JOBID | cut -d"." -f1)'))
        code += "exit $EXIT_CODE\n"
        return code

    def write_PBS(self):
        # Write script
        script_file = self.pbs
        with open(script_file, 'w+') as f:
            f.write(self.get_PBS())
        # Add execution rights
        os.chmod(script_file, os.stat(script_file).st_mode | stat.S_IEXEC)

    def submit_job(self):
        if self.qsub_success:
            raise ValueError('Job already submitted.')
        try:
            out = subprocess.check_output(['qsub', self.pbs])
            self.job_id = int(out.split('.')[0])
            with open(self.id_file, 'w+') as id_file:
                id_file.write(out.split('.')[0] + '\n')
        except subprocess.CalledProcessError as e:
            self.set_qsub_error(e.returncode)
        except ValueError:  # from int cast
            self.set_qsub_error(out)

    def run(self):
        self.write_PBS()
        self.submit_job()

    @property
    def status(self):
        if self.qsub_success:
            try:
                return qstat.get_status(self.job_id)
            except qstat.UnknownJob:
                try:
                    code = self.get_exit_code()
                    if code == 0:
                        return status.DONE
                except:
                    pass
                return status.FAILED
        elif self._job_id[1] is None:
            return status.READY
        else:
            return status.FAILED


class TorquePool(Pool):
    """Launch each job as a standalone Torque job."""

    def __init__(self, default_walltime=60):
        super(TorquePool, self).__init__()
        self._walltime = default_walltime

    def append(self, job):
        super(TorquePool, self).append(
            TorqueJob.from_job(job, walltime=self._walltime))
