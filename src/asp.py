#!python
# -*- coding: utf-8 -*-

import clingo
from __fluto__ import pyclingoLP
from pyasp.term import *

root = __file__.rsplit('/', 1)[0]


theory = """
#theory lp {
    lin_term {
    - : 2, unary;
    * : 1, binary, left;
    + : 0, binary, left;
    - : 0, binary, left
    };
    bounds{
    - : 4, unary;
    * : 3, binary, left;
    / : 2, binary, left;
    + : 1, binary, left;
    - : 1, binary, left;
    .. : 0, binary, left
    };

    &lp/0   : lin_term, {<=,>=,>,<,=,!=}, bounds, any;
    &sum/0   : lin_term, {<=,>=,>,<,=,!=}, bounds, any;
    &objective/1 : lin_term, head;
    &minimize/0 : lin_term, head;
    &maximize/0 : lin_term, head;
    &dom/0 : bounds, {=}, lin_term, head
}.
"""

options = """
% option data defaults
#const show=0.
#const accuracy=1.
#const epsilon=(1,3). % similar to cplex default
#const nstrict=1.
#const solver=cplx.
#const trace=0.
#const core_confl=20.
#const prop_heur=0.
#const debug=0.
#const ilp=0.
"""


def aspsolve_hybride(instance, encoding, export):
    problem = options
    problem += theory
    if export:
        problem += "#const export=1."
    else:
        problem += "#const export=0."
    with open(encoding, 'r') as f:
        problem += f.read()
    with open(instance, 'r') as f:
        problem += f.read()

    # print(problem)

    clictrl = clingo.Control(['--warn=none'])
    # clictrl.configuration.configuration = "trendy"
    clictrl.add("p", [], problem)

    last_assignement, sol_model = pyclingoLP.main(clictrl)
    #print("plopi")
    # print(last_assignement)
    # print(sol_model)

    return last_assignement, sol_model

#def aspsolve_topo(instance, encoding):
#    with open(encoding, 'r') as f:
#        problem = f.read()
#    with open(instance, 'r') as f:
#        problem += f.read()
#
#    prg = clingo.Control() #['--warn=none']
#    prg.add("p", [], problem)
#    prg.ground([("p",[])])
#    with prg.solve(on_model=on_model, on_finish=on_finish, yield_=True) as handle:
#        for m in handle: print(m)
#        print(handle.get())
#
#    prg.cleanup()
#
#    return

    # with open(theory, 'r') as f:
    #     problem = f.read()
    # with open(propagator, 'r') as f:
    #     problem = problem + ''.join(f.readlines()[1:])
    # with open(eco_prg, 'r') as f:
    #     problem = problem + ''.join(f.readlines()[1:])
    # with open(instance, 'r') as f:
    #     problem = problem + f.read()
    # # print(problem)
    # # # prg.ground([("p", [])])
    # # # with prg.solve(yield_=True) as handle:
    # # #     for m in handle: print m
    # # #     print(handle.get())
    # # prg.ground([("p", [])])
    # # ret = prg.solve()
    # # print(ret)
    # prg = clingo.Control() #['--warn=none']
    # prg.add("p", [], problem)
    # prg.ground([("p",[])])
    # with prg.solve(on_model=on_model, on_finish=on_finish, yield_=True) as handle:
    #     for m in handle: print m
    #     print(handle.get())
    #
    # prg.cleanup()


# prg.add("p", "{a;b;c}.")
#     prg.ground([("p", [])])
#     with prg.solve(yield_=True) as handle:
#         for m in handle: print m
#         print(handle.get())
