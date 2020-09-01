# fluto

Metabolic network completion with respect to topological and linear reaction rate constraints based on the stoichiometry.

Tested with Python 3.6.10 and 3.7.6.

So far only level 2 [SBML](http://sbml.org/Documents/Specifications) files are supported.

## Installation and requirements

A good practice is to perform the Python installations into a [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) or a [conda environment](https://conda.io/docs/user-guide/tasks/manage-environments.html)

Create a conda environment for fluto from the `environment.yml`.

- `conda env create -f environment.yml`

Activate conda environment.

- `conda activate fluto`

### ClingoLP

- `conda install -c potassco -c conda-forge clingo-lp`

### CPLEX

IBM provides a promotional version sufficient to solve the toy example.

- `conda install -c ibmdecisionoptimization cplex`

For the full version follow the [IBM installation procedure](https://www.ibm.com/support/knowledgecenter/SSSA5P_12.10.0/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html). e.g.

- `cd /Applications/CPLEX_Studio128/cplex/python/3.6/x86-64_osx/`
- `python setup.py install`

### Package install

Install the Fluto package:

- `python setup.py install`

## Usage

```text
❯ fluto -h
usage: fluto [-h] -m MODEL [-r REPAIRBASE] [-s SEEDS] [-e N | -b | -c]
             [--handorf | --fluto1] [--no-accumulation] [--no-fba] [--cplex]
             [--json]

Performs hybrid (topological/flux) gap-filling

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        organism metabolic model in SBML format
  -r REPAIRBASE, --repairbase REPAIRBASE
                        database of reactions for gap-filling
  -s SEEDS, --seeds SEEDS
                        use topological seeds that are not defined via
                        reactions in the model, txt file with one seed ID per
                        line
  -e N, --enumerate N   enumerate at most N solutions, default is 1, use 0 for
                        all solutions
  -b, --brave           compute the union of all solutions
  -c, --cautious        compute the intersection of all solutions
  --handorf             use scope notion of Handorf & Ebenhöh for the
                        topological produciblity criterium, default is the
                        notion of Sagot & Acuna
  --fluto1              use scope notion of the first fluto version for the
                        topological produciblity criterium, default is the
                        notion of Sagot & Acuna
  --no-accumulation     allow the accumulation of metabolites, per default the
                        accumulation of metabolites is allowed
  --no-fba              turn off flux balance constraints
  --cplex               use CPLEX solver
  --json                produce JSON output

requires Python, ClingoLP and CPLEX packages, see README.md
```

### Example

`fluto -m data/toy/draft.xml -s data/toy/toposeeds.txt -r data/toy/repairdb.xml`

## Publication

- [Hybrid metabolic network completion, Frioux, C., Schaub, T., Schellhorn, S., Siegel, A., Wanko, P. (2019),  TPLP, 19(1), 83–108](https://www.cs.uni-potsdam.de/wv/publications/DBLP_journals/tplp/FriouxSSSW19.pdf)
