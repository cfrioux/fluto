# Requirements

* IBM Cplex ILOG optimization suite (version 12.6.3, 12.7 and 12.8 are tested)
* Clingo Python package
* PyASP Python package

## ClingoLP

Clingo is easily installed with `conda install -c potassco -c conda-forge clingolp`

## Cplex

Follow [IBM installation procedure](https://www.ibm.com/support/knowledgecenter/SSSA5P_12.5.1/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html). e.g.

    $ cd /Applications/CPLEX_Studio128/cplex/python/3.6/x86-64_osx/
    $ python setup.py install

A good practice is to perform the Python installations into a [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) or a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html)

## PyASP

`pip install pyasp`
