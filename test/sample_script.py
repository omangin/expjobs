#!/usr/bin/env python2


import os
import time

from joblib.helpers import run_class


class DummyWorker(object):

    param = 2

    def load_from_serialized(self, cfg):
        with open(cfg, 'r+') as f:
            self.param = int(f.read())

    def set_out_path_and_name(self, path, name):
        self.out_path = path
        self.out_name = name

    def run(self):
        print 'Running {}...'.format(self.param)
        time.sleep(.01)
        out_file = os.path.join(self.out_path, self.out_name + '.result')
        with open(out_file, 'w+') as f:
            f.write('Done.')


run_class(DummyWorker)
