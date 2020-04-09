import subprocess
from subprocess import PIPE
import json


def test_example():
    p = subprocess.run(['python', 'fluto.py', '-m', 'data/toy/draft.xml', '-r', 'data/toy/repairdb.xml'
                        # ,'--json'
                        ], stdout=PIPE, stderr=PIPE)

    print(p.stdout)
    # print(p.stderr)
    # out = json.loads(p.stdout)

    assert (out['Call'][0]['Result'] == 'SATISFIABLE')
