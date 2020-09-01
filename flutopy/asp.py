#!/usr/bin/python
# -*- coding: utf-8 -*-

from flutopy.utils import Topology
import clingo
import clingolp
from clingolp.lp_theory import Propagator as LpPropagator
from clyngor.as_pyasp import TermSet, Atom
from clyngor.parsing import Parser
import logging
logger = logging.getLogger(__name__)

# Root
ROOT = __file__.rsplit('/', 1)[0]
DIR_ASP_SOURCES = '/encodings/'

# ASP SOURCES
COMMON_FLUTO = ROOT + DIR_ASP_SOURCES + 'common-fluto.lp'
TOPO_SAGOT = ROOT + DIR_ASP_SOURCES + 'topo-sagot.lp'
TOPO_HANDORF = ROOT + DIR_ASP_SOURCES + 'topo-handorf.lp'
TOPO_FLUTO1 = ROOT + DIR_ASP_SOURCES + 'topo-fluto1.lp'
FBA = ROOT + DIR_ASP_SOURCES + 'fba.lp'


def aspsolve_hybride(instance, topo: Topology, enumerate: int, brave: bool, cautious: bool, no_accumulation: bool, no_fba: bool, cplex: bool):

    with open(COMMON_FLUTO, 'r') as f:
        problem = f.read()
    if topo == Topology.HANDORF:
        with open(TOPO_HANDORF, 'r') as f:
            problem += f.read()
    elif topo == Topology.FLUTO1:
        with open(TOPO_FLUTO1, 'r') as f:
            problem += f.read()
    else:
        with open(TOPO_SAGOT, 'r') as f:
            problem += f.read()

    with open(instance, 'r') as f:
        problem += f.read()

    if not no_fba:
        with open(FBA, 'r') as f:
            problem += f.read()
        if no_accumulation:
            problem += "no_accumulation."

    clingoLP = Control(enumerate, cplex, brave, cautious)
    clingoLP.add(problem)

    solutions = clingoLP.solve()

    return solutions


class Control:
    def __init__(self, n: int, cplex: bool, brave: bool, cautious: bool):
        self.max = n
        self.solutions = []
        if brave:
            self.unique = True
            self.clingo = clingo.Control(['--warn=none', '--project',
                                          '--opt-mode=optN', '--enum-mode=brave'])
        elif cautious:
            self.unique = True
            self.clingo = clingo.Control(['--warn=none', '--project',
                                          '--opt-mode=optN', '--enum-mode=cautious'])
        else:
            self.unique = False
            self.clingo = clingo.Control(['--warn=none', '--project',
                                          '--opt-mode=optN', str(self.max)])

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

    def add(self, prg):
        self.clingo.add("p", [], prg)

    def solve(self):
        self.clingo.ground([("p", [])])

        _solve_result = self.clingo.solve(on_model=self.copy_assignment)
        #    if solve_result.satisfiable:
        return self.solutions

    def copy_assignment(self, m):
        if m.optimality_proven:
            termset_from_model = TermSet(
                Atom.from_tuple_repr(atom) for atom in Parser().parse_terms(str(m)))
            flux = self.prop.assignment(m.thread_id)
            if self.unique:
                self.solutions.clear()
            self.solutions.append((termset_from_model, flux))
        return True
