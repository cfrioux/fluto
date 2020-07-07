"""
The flutopy module contains functions to perform hybrid (topological/flux) gap-filling.
Functions:
main  -- Main function starting the fluto application.
"""

from flutopy.fluto import run_fluto
import flutopy.utils as utils
import json
import argparse

message = """
Performs hybrid (topological/flux) gap-filling"""

requires = """
requires Python, ClingoLP and CPLEX packages, see README.md
"""


def parsing():
    parser = argparse.ArgumentParser(
        description=message, epilog=requires, prog='fluto')  # , usage=msg()
    parser.add_argument("-m", "--model",
                        help="organism metabolic model in SBML format",
                        required=True)
    parser.add_argument("-r", "--repairbase",
                        help="database of reactions for gap-filling",
                        required=False)
    parser.add_argument('-s', '--seeds',
                        help='use topological seeds that are not defined via reactions in the model,\
                        txt file with one seed ID per line', required=False)

    topo_group = parser.add_mutually_exclusive_group()
    topo_group.add_argument('--handorf',
                            help='use scope notion of Handorf & Ebenhöh \
                                for the topological produciblity criterium,\
                                default is the notion of Sagot & Acuna',
                            required=False, action="store_true", default=False)

    topo_group.add_argument('--fluto1',
                            help='use scope notion of the first fluto version\
                                for the topological produciblity criterium,\
                                default is the notion of Sagot & Acuna',
                            required=False, action="store_true", default=False)

    parser.add_argument("--no-accumulation",
                        help="allow the accumulation of metabolites,\
                            per default the accumulation of metabolites is allowed",
                        required=False, action="store_true", default=False)

    parser.add_argument("--no-fba",
                        help="turn off flux balance constraints",
                        required=False, action="store_true", default=False)

    parser.add_argument("--cplex",
                        help="use CPLEX solver",
                        required=False, action="store_true", default=False)

    parser.add_argument("--json",
                        help="produce JSON output",
                        required=False, action="store_true", default=False)

    args = parser.parse_args()

    return args


def main():

    args = parsing()

    result = run_fluto(args.model, args.seeds, args.repairbase,
                       args.handorf, args.fluto1, args.no_fba, args.no_accumulation, args.cplex, args.json)
    if args.json:
        print(json.dumps(result))

    utils.clean_up()
