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

    lpoutput, objective_reactions = utils.make_instance_fluto(
        args.model, args.seeds, args.repairbase)

    logger.info("Objective reaction(s): " + ",".join(objective_reactions))

    if args.repairbase != None:
        lp_assignment, solumodel = asp.aspsolve_hybride(
            lpoutput, commons.ASP_SRC_FLUTO, args.handorf, args.no_accumulation, args.no_fba, args.cplex)

        if lp_assignment == None and not args.no_fba:
            logger.info("No positive flux solution was found")
            quit()

        unprodtargets = []
        chosen_rxn = []
        exports = []

        for elem in solumodel:
            if elem.pred() == 'unreachable':
                unprodtargets.append(elem.arg(0))
            elif elem.pred() == 'completion':
                chosen_rxn.append(elem.arg(0))
            elif elem.pred() == 'exp':
                exports.append(elem.arg(0))
            else:
                print(elem)

        flux = False
        if not args.no_fba:
            try:
                if lp_assignment[0] > 1e-5:
                    flux = True
            except Exception as e:
                logger.error(
                    'Unexpected solver value: {0}'.format(lp_assignment[0]))
                logger.error(e)
                quit()

        if len(unprodtargets) > 0:
            logger.info("There are still {0} topologically unproducible targets".format(
                len(unprodtargets)))
        else:
            logger.info("sucessful gap-filling")

        logger.info("{0} reactions to be added".format(len(chosen_rxn)))
        logger.info("\n".join(chosen_rxn))

        if flux:
            logger.info(
                "Flux value in objective function(s): {0}".format(lp_assignment[0]))
        elif not args.no_fba:
            logger.info("No flux in objective reaction")

    pass


if __name__ == '__main__':
    # start_time = time.time()
    main()
    utils.clean_up()
