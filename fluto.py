#!/usr/bin/python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@gmail.com>
#
# This file is part of fluto.
#
# meneco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# meneco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fluto.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

import time
import argparse
import logging
from flutopy import utils, asp, commons

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


###############################################################################
#
message = """
Performs hybrid (topological/flux) gap-filling"""

requires = """
requires Python Clingo, PyASP and CPLEX packages. See README and INSTALL
"""
#
###############################################################################


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
                        help='use topological seeds that are not defined via reactions in the model. \
                        Txt file with one seed ID per line ', required=False)

    parser.add_argument('--handorf',
                        help='use scope notion of Handorf & Ebenhöh \
                        for the topological produciblity criterium.\
                        Default is the notion of Sagot & Acuna.', required=False, action="store_true", default=False)

    parser.add_argument("--no-accumulation",
                        help="allow the accumulation of metabolites.\
                            Per default the accumulation of metabolites is allowed.",
                        required=False, action="store_true", default=False)

    parser.add_argument("--no-fba",
                        help="turn off flux balance constraints.",
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

    result = {}
    lpoutput, objective_reactions = utils.make_instance_fluto(
        args.model, args.seeds, args.repairbase)

    result['Model file'] = args.model
    if not args.json:
        print("Model file: {0}".format(args.model))

    result['Seeds file'] = args.seeds
    if not args.json:
        print("Seeds file: {0}".format(args.seeds))

    result['Objective reactions'] = objective_reactions
    if not args.json:
        print("Objective reaction(s): " + ",".join(objective_reactions))

    if args.repairbase != None:

        result['Repair DB'] = args.repairbase
        if not args.json:
            print("Repair DB: {0}".format(args.repairbase))

        lp_assignment, solumodel = asp.aspsolve_hybride(
            lpoutput, commons.ASP_SRC_FLUTO, args.handorf, args.no_accumulation, args.no_fba, args.cplex)

        if not args.no_fba and lp_assignment == None:
            logger.info("No positive flux solution was found")
            result['Result'] = 'NO POSITIVE FLUX SOLUTION'
            print(result)
            quit()

        prodtargets = []
        unprodtargets = []
        chosen_rxn = []
        exports = []

        for elem in solumodel:
            if elem.pred() == 'producible_target':
                prodtargets.append(elem.arg(0)[1:-1])
            elif elem.pred() == 'unreachable':
                unprodtargets.append(elem.arg(0)[1:-1])
            elif elem.pred() == 'completion':
                chosen_rxn.append(elem.arg(0)[1:-1])
            elif elem.pred() == 'acc':
                exports.append(elem.arg(0)[1:-1])
            else:
                print(elem)

        if not args.no_fba:
            try:
                result['Flux'] = lp_assignment[0]
            except Exception as e:
                logger.error(
                    'Unexpected solver value: {0}'.format(lp_assignment[0]))
                logger.error(e)
                quit()

            if lp_assignment[0] > 1e-5:
                logger.info(
                    "Flux value in objective function(s): {0}".format(lp_assignment[0]))
            else:
                print('No flux in objective reaction: {0}'.format(
                    lp_assignment[0]))

        result['Producible targets'] = prodtargets
        if len(prodtargets) > 0:
            if not args.json:
                print("There are {0} producible targets:\n\t{1}".format(
                    len(prodtargets), "\n\t".join(prodtargets)))
        else:
            if not args.json:
                print("No target is producible.")

        result['Unproducible targets'] = unprodtargets
        if len(unprodtargets) > 0:
            if not args.json:
                print("There are still {0} unproducible targets:\n\t{1}".format(
                    len(unprodtargets), "\n\t".join(unprodtargets)))
        else:
            if not args.json:
                print("All targets are producible.")

        result['Added reactions'] = chosen_rxn
        if len(chosen_rxn) > 0:
            if not args.json:
                print("{0} reactions to be added:\n\t{1}".format(
                    len(chosen_rxn), "\n\t".join(chosen_rxn)))
        else:
            if not args.json:
                print("No reactions to be added.")

        result['Accumulating metabolites'] = exports
        if len(exports) > 0:
            if not args.json:
                print("{0} metabolites are accumulating:\n\t{1}".format(
                    len(exports), "\n\t".join(exports)))
        else:
            if not args.json:
                print("No metabolites are accumulating.")

        if args.json:
            print(result)
    pass


if __name__ == '__main__':
    # start_time = time.time()
    main()
    utils.clean_up()
