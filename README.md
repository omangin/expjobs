ExpJobs
=======

*Basic tools to run groups of jobs in an easy way.*

Each job must correspond to a python script that needs to be run with, as arguments:

- a path where output file (but also st{out,err} captures are stored).
- a name mainly used for output files.
- the path to a configuration file.

The code provides tools to run jobs as separate jobs or on clusters using the torque job manager.

Distribution
------------
This code is provided mainly as an example resource without any guarantee (the code organization and API are susceptible to change without notice). Feel free to use it in any way if it is helpful.

The code is distributed under the new BSD license. Please see LICENSE for more details.
