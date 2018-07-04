#!python
# -*- coding: utf-8 -*-
from __future__ import print_function
import clingo
import os
import tempfile
from . import sbml_fluto

def clean_up() :
    if os.path.isfile("parser.out"): os.remove("parser.out")
    if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
    if os.path.isfile("asp_py_lextab.py"): os.remove("asp_py_lextab.py")
    if os.path.isfile("asp_py_lextab.pyc"): os.remove("asp_py_lextab.pyc")
    if os.path.isfile("asp_py_parsetab.py"): os.remove("asp_py_parsetab.py")
    if os.path.isfile("asp_py_parsetab.pyc"): os.remove("asp_py_parsetab.pyc")

def print_met(predictions) :
    for p in predictions:
        if p.pred() == "xreaction" : print(' ',str(p.arg(0)))
        if p.pred() == "unproducible_target" : print(' ',str(p.arg(0)))
        if p.pred() == "dscope" : print(' ',str(p.arg(0)))
        if p.pred() == "target" : print(' ',str(p.arg(0)))
        if p.pred() == "needed_rxn" : print(' ',str(p.arg(0)))
        if p.pred() == "needed_mrxn" : print(' ',str(p.arg(0)))
        if p.pred() == "selected" : print(' ',str(p.arg(0)))


def make_instance_fluto(model, seedsfile, repair=None):
    with tempfile.NamedTemporaryFile("w", prefix='fluto_',
                                    suffix='.lp',
                                    delete=False) as tmp:
        #print(tmp.name)
        try:
            draftnet, seeds, targets, obj_rxn = sbml_fluto.readSBMLnetwork(model, 'd')
        except IOError:
            print('Error while opening {0}. Please check the input file'.format(model))
            quit()

        for fact in draftnet:
            # print(fact)
            tmp.write(str(fact) + '.\n')
        try:
            with open(seedsfile,'r') as h:
                seeds = h.read().splitlines()
                lpseeds = [clingo.Function('seed', [seed]) for seed in seeds]
                for fact in lpseeds:
                    tmp.write(str(fact) + '.\n')
            print('{0} topological seed(s) was(were) provided and will be added to the draft'.format(len(seeds)))
        except:
            print("seeds could not be added to the problem. Check the inputs.")

        if repair != None:
            try:
                repairnet = sbml_fluto.readSBMLnetwork(repair, 'r')[0]
            except IOError:
                print('Error while opening {0}. Please check the input file'.format(repair))
                quit()

            for fact in repairnet:
                tmp.write(str(fact) + '.\n')
        else:
            print('No repair SBML file was given as an input')

        return(tmp.name, obj_rxn)
