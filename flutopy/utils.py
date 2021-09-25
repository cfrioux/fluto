#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import tempfile
from enum import Enum, unique

import clingo

from flutopy import sbml

logger = logging.getLogger(__name__)


@unique
class Topology(str, Enum):
    HANDORF = "Handorf"
    FLUTO1 = "Fluto1"
    SAGOT = "Sagot"


def clean_up():
    if os.path.isfile("parser.out"):
        os.remove("parser.out")
    if os.path.isfile("parsetab.py"):
        os.remove("parsetab.py")
    if os.path.isfile("asp_py_lextab.py"):
        os.remove("asp_py_lextab.py")
    if os.path.isfile("asp_py_lextab.pyc"):
        os.remove("asp_py_lextab.pyc")
    if os.path.isfile("asp_py_parsetab.py"):
        os.remove("asp_py_parsetab.py")
    if os.path.isfile("asp_py_parsetab.pyc"):
        os.remove("asp_py_parsetab.pyc")


def make_instance_fluto(model, seeds_sbml, repair=None):
    with tempfile.NamedTemporaryFile("w", prefix='fluto_',
                                     suffix='.lp',
                                     delete=False) as tmp:
        try:
            draftnet, seeds, _targets, obj_rxn = sbml.readSBMLnetwork(
                model, 'd')
        except IOError:
            logger.error(
                'Error while opening %s. Please check the input file', model)
            sys.exit()

        for fact in draftnet:
            tmp.write(str(fact) + '.\n')
        if seeds_sbml != None:
            try:
                with open(seeds_sbml, 'r') as h:
                    seeds = h.read().splitlines()
                    lpseeds = [clingo.Function('seed', [seed])
                               for seed in seeds]
                    for fact in lpseeds:
                        tmp.write(str(fact) + '.\n')
                logger.info(
                    '%s topological seed(s) was(were) provided', len(seeds))
            except:
                logger.warning(
                    "seeds could not be added to the problem. Check the inputs.")

        if repair is not None:
            try:
                repairnet = sbml.readSBMLnetwork(repair, 'r')[0]
            except IOError:
                logger.error(
                    'Error while opening %s. Please check the input file', repair)
                sys.exit()

            for fact in repairnet:
                tmp.write(str(fact) + '.\n')
        else:
            logger.warning('No repair SBML file was given as an input')

        return(tmp.name, obj_rxn)
