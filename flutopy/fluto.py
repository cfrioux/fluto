#!/usr/bin/python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@gmail.com>
#
# This file is part of fluto.
#
# fluto is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fluto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fluto.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

import json
import logging
from flutopy import utils, asp
from flutopy.utils import Topology

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_fluto(args):
    result = {}
    if not args.json:
        print("# Fluto analysis\n")
    lpoutput, objective_reactions = utils.make_instance_fluto(
        args.model, args.seeds, args.repairbase)

    result['Model file'] = args.model
    result['Objective reactions'] = objective_reactions
    result['Seeds file'] = args.seeds
    result['Repair DB'] = args.repairbase

    if args.sagot:
        topo = Topology.SAGOT
    elif args.fluto1:
        topo = Topology.FLUTO1
    else:
        topo = Topology.HANDORF
    result['Topological criterium'] = topo

    if args.no_fba:
        result['Flux balance criterium'] = 'OFF'
    else:
        result['Flux balance criterium'] = 'ON'
        if args.no_accumulation:
            result['Accumulation'] = 'FORBIDDEN'
        else:
            result['Accumulation'] = 'ALLOWED'

    if args.brave:
        result['Reasoning mode'] = 'BRAVE'
    elif args.cautious:
        result['Reasoning mode'] = 'CAUTIOUS'
    else:
        result['Reasoning mode'] = f"ENUMERATE {args.enumerate}"

    if not args.json:
        print(f"Model file: {args.model}")
        print("Objective reaction(s): " + ",".join(objective_reactions))
        print("Seeds file: {args.seeds}")
        print("Repair DB: {args.repairbase}\n")
        print('Topological criterium: {0}'.format(
            result['Topological criterium']))
        if args.brave:
            print("Reasoning mode: BRAVE")
        elif args.cautious:
            print("Reasoning mode: CAUTIOUS")
        else:
            print("Reasoning mode: ENUMERATE {args.enumerate}")

        print('Flux balance criterium: {0}'.format(
            result['Flux balance criterium']))

        if not args.no_fba:
            print('Accumulation: {0}'.format(result['Accumulation']))

    logger.info("Solving ...\n")
    solve_results = asp.aspsolve_hybride(
        lpoutput, topo, args.enumerate, args.brave, args.cautious, args.no_accumulation, args.no_fba, args.cplex)

    if not args.json:
        if len(solve_results) > 0:
            logger.info("%s solutions found\n", str(len(solve_results)))
        else:
            logger.info("No solutions found\n")

    if args.cautious:
        (solumodel, lp_assignment) = solve_results[0]
        if not args.json:
            print(
                "\n## Reactions occurring in all minimal solutions (intersection):\n\n- ", end="")
        if not args.no_fba and lp_assignment is None:
            logger.info("No positive flux solution was found")
            result['Result'] = 'NO POSITIVE FLUX SOLUTION'
            print(json.dumps(result))
            quit()

        chosen_rxn = []

        for elem in solumodel:
            if elem.predicate == 'completion':
                chosen_rxn.append(elem.arguments[0][1:-1])

        result['Intersection'] = chosen_rxn
        if len(chosen_rxn) > 0:
            if not args.json:
                print("\n- ".join(chosen_rxn))
        else:
            if not args.json:
                print("the intersection is empty\n")
    elif args.brave:
        (solumodel, lp_assignment) = solve_results[0]
        if not args.json:
            print(
                "\n## Reactions occurring in at least one minimal solution (union):\n\n- ", end="")
        if not args.no_fba and lp_assignment == None:
            logger.info("No positive flux solution was found")
            result['Result'] = 'NO POSITIVE FLUX SOLUTION'
            print(json.dumps(result))
            quit()

        chosen_rxn = []

        for elem in solumodel:
            if elem.predicate == 'completion':
                chosen_rxn.append(elem.arguments[0][1:-1])

        result['Union'] = chosen_rxn
        if len(chosen_rxn) > 0:
            if not args.json:
                print("\n- ".join(chosen_rxn))
        else:
            if not args.json:
                print("the union is empty\n")
    else:
        solutions = []
        scounter = 1
        for (solumodel, lp_assignment) in solve_results:
            solution = {}
            if not args.json:
                print(f"\n## Solution {scounter}\n")
                scounter += 1
            if not args.no_fba and lp_assignment is None:
                logger.info("No positive flux solution was found")
                result['Result'] = 'NO POSITIVE FLUX SOLUTION'
                print(json.dumps(result))
                quit()

            prodtargets = []
            unprodtargets = []
            chosen_rxn = []
            exports = []

            for elem in solumodel:
                if elem.predicate == 'producible_target':
                    prodtargets.append(elem.arguments[0][1:-1])
                elif elem.predicate == 'unreachable':
                    unprodtargets.append(elem.arguments[0][1:-1])
                elif elem.predicate == 'completion':
                    chosen_rxn.append(elem.arguments[0][1:-1])
                elif elem.predicate == 'acc':
                    exports.append(elem.arguments[0][1:-1])
                else:
                    logger.warning(
                        "Unexpected atom in solution %s", elem)

            if not args.no_fba:
                try:
                    solution['Flux'] = lp_assignment[0]
                except Exception as e:
                    logger.error(
                        'Unexpected solver value: %s', lp_assignment[0])
                    logger.error(e)
                    return result

                if not args.json:
                    print("- flux value in objective function(s): {0}\n".format(
                        lp_assignment[0]))
                if lp_assignment[0] <= 1e-5:
                    logger.warning(
                        'No flux in objective reaction: %s\n', lp_assignment[0])

            solution['Producible targets'] = prodtargets
            if len(prodtargets) > 0:
                if not args.json:
                    print("- {0} producible targets:\n  - {1}\n".format(
                        len(prodtargets), "\n  - ".join(prodtargets)))
            else:
                if not args.json:
                    print("- no target is producible\n")

            solution['Unproducible targets'] = unprodtargets
            if len(unprodtargets) > 0:
                if not args.json:
                    print("- there are still {0} unproducible targets:\n  - {1}\n".format(
                        len(unprodtargets), "\n  - ".join(unprodtargets)))
            else:
                if not args.json:
                    print("- all targets are producible\n")

            solution['Added reactions'] = chosen_rxn
            if len(chosen_rxn) > 0:
                if not args.json:
                    print("- {0} reactions to be added:\n  - {1}\n".format(
                        len(chosen_rxn), "\n  - ".join(chosen_rxn)))
            else:
                if not args.json:
                    print("- no reactions to be added\n")

            solution['Accumulating metabolites'] = exports
            if len(exports) > 0:
                if not args.json:
                    print("- {0} metabolites are accumulating:\n  - {1}\n".format(
                        len(exports), "\n  - ".join(exports)))
            else:
                if not args.json:
                    print("- no metabolites are accumulating")
            solutions.append(solution)
        result['Solutions'] = solutions
    return result
