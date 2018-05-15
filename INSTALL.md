# Requirements

* IBM Cplex ILOG optimization suite (version 12.6.3 is tested)
* Clingo Python package
* PyASP Python package



## Cplex

Follow [IBM installation procedure](https://www.ibm.com/support/knowledgecenter/SSSA5P_12.5.1/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html). e.g.

    $ cd /Users/myself/Applications/IBM/ILOG/CPLEX_Studio1263/cplex/python/2.7/x86-64_osx/
    $ python setup.py install

A good practice is to perform the Python installations into a [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) or a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html)

# PyASP

## Conda users

`conda install -c bioconda pyasp`

## Pip install

`pip install pyasp`

### Troubleshooting

**There are some known issues with the pyasp package if installed with python pip. If obtaining such an error when running fluto:**

``OSError: Grounder '/Users/cfrioux/wd/asp/mohycom/venv/lib/python2.7/site-packages/pyasp/bin/gringo4' not found``

It means that the binaries were not correctly installed for pyasp.
These two command lines should be an efficient workaround:
1. uninstall pyasp
``pip uninstall pyasp``
2. reinstall pyasp without cache
``pip install pyasp --no-cache-dir``




# Clingo

## Conda users

Clingo is easily installed with `conda install -c potassco clingo`

## Linux installation

Clingo can be obtained from [Potassco official website](https://potassco.org/clingo/) or [Github](https://github.com/potassco/clingo/releases) and has to be compiled with Python support. Clingo 5 is tested. Newer versions should work.

Do not forget to set the Python path with clingo Python module. For example:
`export PYTHONPATH=/home/.../bin/linux/64/lib/pyclingo`



## MacOS installation

Clingo can be obtained from [Potassco official website](https://potassco.org/clingo/) or [Github](https://github.com/potassco/clingo/releases)
Download the release for MacOS e.g. `clingo-5.2.0-macos-10.9.tar.gz`
Clingo 5 is tested. Newer versions should work

Extract the files.

Export `clingo-python` to your `$PATH` (`export PATH=$PATH:/path/to/folder/containing/clingo-python`) or do not forget to input the path to `clingo-python` when calling the program