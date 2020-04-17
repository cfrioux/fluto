import json
from subprocess import PIPE
from flutopy.fluto import run_fluto
import subprocess
import sys
sys.path.append('../')


def test_fluto():
    result = run_fluto(
        'data/toy/draft.xml', seeds=None, repairbase='data/toy/repairdb.xml', handorf=True, fluto1=False, no_fba=True, no_accumulation=False, cplex=False, json=True)
    assert result['Topological criterium'] == 'Handorf'


test_fluto()
