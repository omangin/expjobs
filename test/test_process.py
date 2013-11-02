import os
import shutil
import tempfile
from unittest import TestCase

from joblib.job import Job
from joblib.process import MultiprocessPool
from joblib import status


SCRIPT = os.path.join(os.path.dirname(__file__), 'sample_script.py')
CONFIG = '7\n'
RUNNER_OUT = 'Running 7...\n'
RUNNER_ERR = ''
RUNNER_RESULT = 'Done.'


class TestMultiprocessPool(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.jobs = [Job(self.tmpdir, 'test' + str(i), SCRIPT)
                     for i in range(10)]
        self.pool = MultiprocessPool(4, refresh_period=.005)
        self.pool.extend(self.jobs)
        for j in self.jobs:
            with open(j.config, 'w+') as f:
                f.write(CONFIG)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_job_statuses(self):
        self.assertEqual(self.pool.statuses, [status.READY for _ in range(10)])
        self.pool.run()
        self.pool.wait()
        self.assertEqual(self.pool.statuses, [status.DONE for _ in range(10)])

    def test_pool_status(self):
        self.assertEqual(self.pool.status, status.READY)
        self.pool.run()
        self.pool.wait()
        self.assertEqual(self.pool.status, status.DONE)

    def test_pool_status_is_failed(self):
        self.pool.append(Job(self.tmpdir, 'loser', '/bin/false'))
        self.pool.run()
        self.pool.wait()
        self.assertEqual(self.pool.status, status.FAILED)
