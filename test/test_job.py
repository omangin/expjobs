import os
import shutil
import tempfile
from unittest import TestCase

from joblib.job import Job
from joblib import status


SCRIPT = os.path.join(os.path.dirname(__file__), 'sample_script.py')
CONFIG = '7\n'
RUNNER_OUT = 'Running 7...\n'
RUNNER_ERR = ''
RUNNER_RESULT = 'Done.'


class TestJob(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.job = Job(self.tmpdir, 'test', SCRIPT)
        self.cfg = os.path.join(self.tmpdir, 'test.cfg')
        self.out = os.path.join(self.tmpdir, 'test.out')
        self.err = os.path.join(self.tmpdir, 'test.err')
        self.results = os.path.join(self.tmpdir, 'test.result')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def init_config(self):
        with open(self.cfg, 'w+') as f:
            f.write(CONFIG)

    def test_files(self):
        self.assertEqual(self.job.config, self.cfg)
        self.assertEqual(self.job.out, self.out)
        self.assertEqual(self.job.err, self.err)

    def test_check_config(self):
        self.assertFalse(self.job.check_config())
        self.init_config()
        self.assertTrue(self.job.check_config())

    def test_run_writes_files(self):
        self.init_config()
        self.job.run()
        self.assertTrue(os.path.exists(self.out))
        self.assertTrue(os.path.exists(self.err))

    def test_run_out(self):
        self.init_config()
        self.job.run()
        self.assertTrue(os.path.exists(self.out))
        with open(self.out, 'r+') as f:
            self.assertEqual(f.read(), RUNNER_OUT)

    def test_run_err(self):
        self.init_config()
        self.job.run()
        with open(self.err, 'r+') as f:
            self.assertEqual(f.read(), RUNNER_ERR)

    def test_run_writes_results(self):
        self.init_config()
        self.job.run()
        self.assertTrue(os.path.exists(self.results))

    def test_run_results(self):
        self.init_config()
        self.job.run()
        with open(self.results, 'r+') as f:
            self.assertEqual(f.read(), RUNNER_RESULT)

    def test_run_status(self):
        self.init_config()
        self.job.run()
        self.assertEqual(self.job.status, status.DONE)

    def test_fails(self):
        self.init_config()
        self.job = Job(self.tmpdir, 'test', '/bin/false')
        self.job.run()
        self.assertEqual(self.job.status, status.FAILED)
