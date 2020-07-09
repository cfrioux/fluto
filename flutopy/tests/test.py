import json
from subprocess import PIPE
from flutopy.fluto import run_fluto
from flutopy.__init__ import arg_parser
import sys
sys.path.append('../')


def test_fluto1():
    args = arg_parser().parse_args(
        ['-m', 'data/toy/draft.xml',
         '-r', 'data/toy/repairdb.xml',
         '--no-fba', '--json'])
    print(args)
    result = run_fluto(args)
    assert result['Topological criterium'] == 'Handorf'
    assert result['Flux balance criterium'] == 'OFF'
    assert result['Objective reactions'] == ["R5"]
    assert set(result['Solutions'][0]['Producible targets']) == set(["a", "c"])
    assert set(result['Solutions'][0]['Added reactions']) == set(["R7", "R6"])
    assert result['Solutions'][0]['Accumulating metabolites'] == []


def test_fluto2():
    args = arg_parser().parse_args(
        ['-m', 'flutopy/tests/testdata/testdraft.xml',
         '-r', 'flutopy/tests/testdata/testrepairdb.xml',
         '--sagot',
         '--brave', '--no-fba', '--json'])
    print(args)
    result = run_fluto(args)
    assert result['Reasoning mode'] == 'BRAVE'
    assert result['Flux balance criterium'] == 'OFF'
    assert result['Objective reactions'] == ["R_exportT"]
    assert result['Solutions'][0]['Producible targets'] == ["T"]
    assert set(result['Solutions'][0]['Added reactions']) == set(["A1", "A2"])
    assert result['Solutions'][0]['Accumulating metabolites'] == []


def test_fluto3():
    args = arg_parser().parse_args(
        ['-m', 'flutopy/tests/testdata/testdraft.xml',
         '-r', 'flutopy/tests/testdata/testrepairdb.xml',
         '--sagot',
         '--cautious', '--no-fba', '--json'])
    print(args)
    result = run_fluto(args)
    assert result['Reasoning mode'] == 'CAUTIOUS'
    assert result['Flux balance criterium'] == 'OFF'
    assert result['Objective reactions'] == ["R_exportT"]
    assert result['Solutions'][0]['Producible targets'] == ["T"]
    assert result['Solutions'][0]['Added reactions'] == []
    assert result['Solutions'][0]['Accumulating metabolites'] == []


def test_fluto4():
    args = arg_parser().parse_args(
        ['-m', 'flutopy/tests/testdata/testdraft.xml',
         '-r', 'flutopy/tests/testdata/testrepairdb.xml',
         '--sagot',
         '--enumerate', '2',
         '--no-fba', '--json'])
    print(args)
    result = run_fluto(args)
    assert result['Reasoning mode'] == 'ENUMERATE 2'
    assert result['Flux balance criterium'] == 'OFF'
    assert result['Objective reactions'] == ["R_exportT"]
    assert result['Solutions'][0]['Producible targets'] == ["T"]
    assert result['Solutions'][0]['Added reactions'] == ['A1']
    assert result['Solutions'][0]['Accumulating metabolites'] == []
    assert result['Solutions'][1]['Added reactions'] == ['A2']
