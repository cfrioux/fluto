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
requires Python Clingo, PyASP and Cplex packages. See README and INSTALL
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
                        help='topological seeds to unblock \
                        circular dependencies in the graph. \
                        Txt file with one seed ID per line', required=False)
    parser.add_argument("-e", "--export",
                        help="enabling export of compounds to prevent metabolite accumulation",
                        required=False, action="store_true", default=False)
    parser.add_argument("--cplex",
                        help="use CPLEX solver",
                        required=False, action="store_true", default=False)

    parser.add_argument("--json",
                        help="produce json output",
                        required=False, action="store_true", default=False)

    # TODO deal with export options
    args = parser.parse_args()

    return args


def main():

    args = parsing()
    # get models from inputs
    sbml_model = args.model
    # get repairbase from inputs
    repairdb = args.repairbase
    # get seeds if given
    seeds_sbml = args.seeds
    # get export behaviour
    exportbool = args.export

    lpoutput, objective_reactions = utils.make_instance_fluto(
        sbml_model, seeds_sbml, repairdb)

    logger.info("Objective reaction(s): " + ",".join(objective_reactions))

    if repairdb != None:
        lp_assignment, solumodel = asp.aspsolve_hybride(
            lpoutput, commons.ASP_SRC_FLUTO, exportbool, args.cplex)

        if lp_assignment == None:
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

        if lp_assignment[0] > 1e-5:
            flux = True
        else:
            flux = False

        if len(unprodtargets) == 0:
            topo = True
        else:
            topo = False

        if not flux:
            logger.info("No flux in objective reaction")
            logger.info(str(len(chosen_rxn)) + " reactions to be added")
            logger.info("\n".join(chosen_rxn))
        if not topo:
            logger.info("There are still " + str(len(unprodtargets)) +
                        " topologically unproducible reactants in objective reaction")
            logger.info(str(len(chosen_rxn)) + " reactions to be added")
            logger.info("\n".join(chosen_rxn))
            logger.info("Flux value in objective function(s): " +
                        str(lp_assignment[0]))

        if flux and topo:
            logger.info("sucessful gap-filling")
            logger.info(str(len(chosen_rxn)) + " reactions to be added")
            logger.info("\n".join(chosen_rxn))
            logger.info("Flux value in objective function(s): " +
                        str(lp_assignment[0]))

    pass


if __name__ == '__main__':
    start_time = time.time()
    main()
    utils.clean_up()
    print("--- %s seconds ---" % round(((time.time()) - start_time), 2))
