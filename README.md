# Installation and requirements

## requirements

* Pyasp
`conda install -c bioconda pyasp`
* Cplex
* Clingo compiled with Python support

## install

See INSTALL.md

# Usage

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

## toy example

`python fluto.py -m data/toy/draft.xml -s data/toy/toposeeds.txt -r data/toy/repairdb.xml`