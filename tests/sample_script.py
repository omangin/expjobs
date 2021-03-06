#!/usr/bin/env python


import os
import time

from expjobs.helpers import run_class


class DummyWorker(object):

    param = 2

    def set_out_path_and_name(self, path, name):
        self.out_path = path
        self.out_name = name

    def run(self):
        print('Running {}...'.format(self.param))
        time.sleep(.01)
        out_file = os.path.join(self.out_path, self.out_name + '.result')
        with open(out_file, 'w+') as f:
            f.write('Done.')

    @classmethod
    def load_from_serialized(cls, cfg):
        worker = cls()
        with open(cfg, 'r+') as f:
            cls.param = int(f.read())
        return worker


run_class(DummyWorker)
