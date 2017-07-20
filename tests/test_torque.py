import io
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from expjobs.job import Job
from expjobs.torque import TorqueJob, TorquePool


SCRIPT = '/bin/false'

OK_PBS = """\
#!/bin/sh

#PBS -N test0
#PBS -l walltime=1:00:00

(python /bin/false /dev/null/test0.cfg /dev/null test0 1>/dev/null/test0.out \
2>/dev/null/test0.err)
EXIT_CODE=$?
echo $EXIT_CODE > /dev/null/test0.$(echo $PBS_JOBID | cut -d"." -f1).exitcode
exit $EXIT_CODE
"""


class TestTorqueJob(TestCase):

    def test_walltime_string(self):
        job = TorqueJob('/dev/null', 'test', SCRIPT, walltime=195)
        self.assertEqual(job.get_walltime_str(), '3:15:00')

    def test_walltime_string_more_than_one_day(self):
        job = TorqueJob('/dev/null', 'test', SCRIPT, walltime=1999)
        self.assertEqual(job.get_walltime_str(), '33:19:00')

    def test_id(self):
        try:
            path = mkdtemp()
            with io.open(os.path.join(path, 'test.pbs.id'), 'w') as f:
                f.write(u'43\n')
            job = TorqueJob(path, 'test', SCRIPT, walltime=1999)
            self.assertEqual(job.job_id, 43)
        finally:
            rmtree(path)


class TestTorquePool(TestCase):

    def setUp(self):
        self.jobs = [Job('/dev/null', 'test' + str(i), SCRIPT)
                     for i in range(10)]
        self.pool = TorquePool()
        self.pool.extend(self.jobs)

    def test_job_inherits_walltime(self):
        pool = TorquePool(default_walltime=3.)
        pool.append(Job('/dev/null', 'test1', SCRIPT))
        self.assertEqual(pool.jobs[0].walltime, 3.)

    def test_torquejob_do_not_inherits_walltime(self):
        pool = TorquePool(default_walltime=3.)
        pool.append(TorqueJob('/dev/null', 'test2', SCRIPT, walltime=2.))
        self.assertEqual(pool.jobs[0].walltime, 2.)

    def test_job_PBS(self):
        PBS = self.pool.jobs[0].get_PBS()
        self.assertEqual(PBS, OK_PBS)
