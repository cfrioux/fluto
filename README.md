# fluto

## Installation and requirements

Python3.6

So far only level 2 [SBML](http://sbml.org/Documents/Specifications) files are supported

### Pyasp

* `pip install  pyasp`

### Cplex for [python](https://www.ibm.com/support/knowledgecenter/SSSA5P_12.5.1/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html) (`conda install -c ibmdecisionoptimization cplex ` provides a promotional version sufficient to solve the toy example)

* `clingolp` ( `conda install -c sthiele -c potassco -c conda-forge clingolp`)

For more information see INSTALL.md.

## Usage

    python fluto.py -h

    usage: fluto.py [-h] -m MODEL [-r REPAIRBASE] [-s SEEDS] [-e]

    Performs hybrid (topological/flux) gap-filling

    optional arguments:
    -h, --help            show this help message and exit
    -m MODEL, --model MODEL
                        organism metabolic model in SBML format
    -r REPAIRBASE, --repairbase REPAIRBASE
                        database of reactions for gap-filling
    -s SEEDS, --seeds SEEDS
                        topological seeds to unblock circular dependencies in
                        the graph. Txt file with one seed ID per line
    -e, --export          enabling export of compounds to prevent metabolite
                        accumulation

    requires Python Clingo, PyASP and Cplex packages. See README and INSTALL

### Example

`python fluto.py -m data/toy/draft.xml -s data/toy/toposeeds.txt -r data/toy/repairdb.xml`
