from newlang import State
from collections import namedtuple
import numpy as np

BT = namedtuple("BasicTest", "line res")

empty_state = State()

basic_tests = [
    BT('1 + 1', 2),
    BT('1 - 1', 0),
    BT('-1', -1),
    BT('1e+10', 1e10),
    BT('-1e-10', -1e-10),
    BT('1 * 2', 2),
    BT('1 * e', np.e),
    BT('1/2', 0.5),
    BT('2 ^ 2', 4),
    BT('2 ^ 3 ^ 2', 512),
    BT('2 + 3 * 2', 8),
    BT('sin(0)', 0),
    BT('sin(pi)', np.sin(np.pi)),
    BT('1 + 1j', complex(1, 1)),
    BT('sqrt(-1 + 0j)', complex(0, 1)),
    BT('(@x x + 5)(10)', 15),
    BT('(@x 20 + sin(x)^2)(0)', 20)
]

failed = False

def basic_fail(test, res, err):
    print('Test failed:')
    print(f'\tinput: {test.line}')
    print(f'\texpected: {test.res}')
    if err:
        print(f"\terror: {err}")
    else:
        print(f'\tgot: {res}')

    global failed
    failed = True

for test in basic_tests:
    res, err = empty_state.parse(test.line)
    if err or not np.all(np.equal(res, test.res)):
        basic_fail(test, res, err)


if not failed:
    print('All tests passed!')