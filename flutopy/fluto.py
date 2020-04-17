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


def run_fluto(model, seeds, repairbase, handorf, fluto1, no_fba, no_accumulation, cplex, json):

    result = {}
    lpoutput, objective_reactions = utils.make_instance_fluto(
        model, seeds, repairbase)

    result['Model file'] = model
    result['Objective reactions'] = objective_reactions
    result['Seeds file'] = seeds
    result['Repair DB'] = repairbase

    if handorf:
        topo = Topology.HANDORF
    elif fluto1:
        topo = Topology.FLUTO1
    else:
        topo = Topology.SAGOT
    result['Topological criterium'] = topo

    if no_fba:
        result['Flux balance criterium'] = 'OFF'
    else:
        result['Flux balance criterium'] = 'ON'
        if no_accumulation:
            result['Accumulation'] = 'FORBIDDEN'
        else:
            result['Accumulation'] = 'ALLOWED'

    if not json:
        print("Model file: {0}".format(model))
        print("Objective reaction(s): " + ",".join(objective_reactions))
        print("Seeds file: {0}".format(seeds))
        print("Repair DB: {0}\n".format(repairbase))
        print('Topological criterium: {0}'.format(
            result['Topological criterium']))

        print('Flux balance criterium: {0}'.format(
            result['Flux balance criterium']))

        if not no_fba:
            print('Accumulation: {0}'.format(result['Accumulation']))
    print()

    lp_assignment, solumodel = asp.aspsolve_hybride(
        lpoutput, topo, no_accumulation, no_fba, cplex)

    if not no_fba and lp_assignment == None:
        logger.info("No positive flux solution was found")
        result['Result'] = 'NO POSITIVE FLUX SOLUTION'
        print(json.dumps(result))
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
            logger.warning('Unexpected atom in solution {0}'.format(elem))

    if not no_fba:
        try:
            result['Flux'] = lp_assignment[0]
        except Exception as e:
            logger.error(
                'Unexpected solver value: {0}'.format(lp_assignment[0]))
            logger.error(e)
            return result

        if not json:
            print("Flux value in objective function(s): {0}\n".format(
                lp_assignment[0]))
        if lp_assignment[0] <= 1e-5:
            logger.warning('No flux in objective reaction: {0}\n'.format(
                lp_assignment[0]))

    result['Producible targets'] = prodtargets
    if len(prodtargets) > 0:
        if not json:
            print("There are {0} producible targets:\n\t{1}\n".format(
                len(prodtargets), "\n\t".join(prodtargets)))
    else:
        if not json:
            print("No target is producible.\n")

    result['Unproducible targets'] = unprodtargets
    if len(unprodtargets) > 0:
        if not json:
            print("There are still {0} unproducible targets:\n\t{1}\n".format(
                len(unprodtargets), "\n\t".join(unprodtargets)))
    else:
        if not json:
            print("All targets are producible.\n")

    result['Added reactions'] = chosen_rxn
    if len(chosen_rxn) > 0:
        if not json:
            print("{0} reactions to be added:\n\t{1}\n".format(
                len(chosen_rxn), "\n\t".join(chosen_rxn)))
    else:
        if not json:
            print("No reactions to be added.\n")

    result['Accumulating metabolites'] = exports
    if len(exports) > 0:
        if not json:
            print("{0} metabolites are accumulating:\n\t{1}\n".format(
                len(exports), "\n\t".join(exports)))
    else:
        if not json:
            print("No metabolites are accumulating.\n")

    return result
