#!/usr/bin/python
# -*- coding: utf-8 -*-

import clingo
import clingolp
from clingolp.lp_theory import Propagator as LpPropagator
from pyasp.term import *

root = __file__.rsplit('/', 1)[0]


def aspsolve_hybride(instance, encoding, export):

    if export:
        problem = "#const export=1."
    else:
        problem = "#const export=0."
    with open(encoding, 'r') as f:
        problem += f.read()
    with open(instance, 'r') as f:
        problem += f.read()

    # print(problem)

    clingoLP = Control()
    clingoLP.add(problem)

    last_assignement, sol_model = clingoLP.solve()

    return last_assignement, sol_model


class Control:
    def __init__(self):
        self.clingo = clingo.Control(['--warn=none'])
        self.clingo.add("base", [], clingolp.lp_theory.theory)
        self.prop = LpPropagator(self.clingo)
        self.clingo.register_propagator(self.prop)
        self.clingo.ground([("base", [])])
        self.model = None
        self.lp_assignment = None

    def add(self, prg):
        self.clingo.add("p", [], prg)

    def solve(self):
        self.clingo.ground([("p", [])])
        self.clingo.solve(on_model = self.copy_assignment)

        try:
            termsetfrommodel = TermSet.from_string(self.model)
            return(self.lp_assignment,termsetfrommodel)
        except NameError as e:
            print('Error parsing solution:', e)
            exit()


    def copy_assignment(self,m):
        self.model = m.__repr__()
        # self.prop.print_assignment(m.thread_id)
        self.lp_assignment = self.prop.assignment(m.thread_id)

