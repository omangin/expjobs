import os
import subprocess
from xml.etree import ElementTree

from . import status


QSTAT_BIN = 'qstat'
STATUS = {'C': status.DONE,
          'R': status.RUNNING,
          'E': status.RUNNING,
          'H': status.RUNNING,
          'T': status.RUNNING,
          'W': status.RUNNING,
          'S': status.RUNNING,
          'Q': status.QUEUED,
          }


class UnknownJob(ValueError):
    pass


def get_status(job_id):
    try:
        with open(os.devnull, 'w+') as devnull:
            xmljob = subprocess.check_output([QSTAT_BIN, '-x', str(job_id)],
                                             stderr=devnull)
        et = ElementTree.fromstring(xmljob)
        state = et.find('Job').find('job_state').text
        return STATUS[state]
    except subprocess.CalledProcessError, e:
        if e.returncode == 153:
            raise UnknownJob(job_id)
        else:
            raise e
