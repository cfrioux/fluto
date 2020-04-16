#!/usr/bin/python
# -*- coding: utf-8 -*-

import clingo
import clingolp
from clingolp.lp_theory import Propagator as LpPropagator
from pyasp.term import TermSet
import logging
logger = logging.getLogger(__name__)


root = __file__.rsplit('/', 1)[0]


def aspsolve_hybride(instance, encoding, handorf: bool, no_accumulation: bool, no_fba: bool, cplex: bool):

    with open(encoding, 'r') as f:
        problem = f.read()
    with open(instance, 'r') as f:
        problem += f.read()

    if handorf:
        problem += "handorf."
    if no_fba:
        problem += "no_fba."
    elif no_accumulation:
        problem += "no_accumulation."

    clingoLP = Control(cplex)
    clingoLP.add(problem)

    last_assignement, sol_model = clingoLP.solve()

    return last_assignement, sol_model


class Control:
    def __init__(self, cplex: bool):
        self.clingo = clingo.Control(['--warn=none', '0'])
        self.clingo.add("base", [], clingolp.lp_theory.theory)
        if cplex:
            solver = 'cplx'
        else:
            solver = 'lps'

        self.prop = LpPropagator(self.clingo, solver,
                                 show=True,
                                 accuracy=1,
                                 epsilon=1*10**-3,
                                 nstrict=True,
                                 trace=False,
                                 core_confl=20,
                                 prop_heur=0,
                                 ilp=False,
                                 debug=0)

        self.clingo.register_propagator(self.prop)
        self.clingo.ground([("base", [])])
        self.model = None
        self.lp_assignment = None

    def add(self, prg):
        self.clingo.add("p", [], prg)

    def solve(self):
        self.clingo.ground([("p", [])])
        solve_result = self.clingo.solve(on_model=self.copy_assignment)
        if solve_result.satisfiable:
            try:
                termsetfrommodel = TermSet.from_string(self.model)
            except Exception as e:
                logger.error('Error parsing solution: {0}'.format(e))
                logger.error('Solution: {0}'.format(self.model))
                quit()

            return (self.lp_assignment, termsetfrommodel)
        else:
            return (None, None)

    def copy_assignment(self, m):
        self.model = m.__repr__()
        self.lp_assignment = self.prop.assignment(m.thread_id)
