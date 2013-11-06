from unittest import TestCase

from joblib.job import Job
from joblib.torque import TorquePool, TorqueJob


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
        print PBS
        print OK_PBS
        self.assertEqual(PBS, OK_PBS)
