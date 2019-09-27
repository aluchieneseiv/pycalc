from lark import Lark, Transformer, v_args
from lark.exceptions import VisitError, UnexpectedInput
import math
import numpy as np
from inspect import isclass


class Ref:
    def __init__(self, set=None, get=None):
        self.set = set
        self.get = get

    def index(self, args):
        args = list(args)
        i = args.pop(-1)
        ref = self.get()
        while args:
            ref = ref[args.pop(0)]

        def set(x):
            ref[i] = x
            return x

        return Ref(set=set, get=lambda: ref[i])

@v_args(inline=True)
class CalculateTree(Transformer):
    solve = lambda _, x, y: np.linalg.solve(x, y)

    pow = lambda _, x, y: np.linalg.matrix_power(x, y) if x is np.ndarray else x ** y

    equals = lambda _, x, y: np.all(np.equal(x, y))
    differs = lambda _, x, y: not np.all(np.equal(x, y))

    builtins = {o: getattr(np, o) for o in np.__all__ if not isclass(getattr(np, o))}

    builtins.update({
        # numpy matrix
        "rank": np.linalg.matrix_rank,
        "det": np.linalg.det,
        "norm": np.linalg.norm,
        "inv": np.linalg.inv,
        "zeros": lambda *shape: np.zeros(shape),
        "ones": lambda *shape: np.ones(shape),
        'j': np.complex(0, 1),
        'complex': np.complex,

        # misc
        "valinterp": lambda f, a, b: a + (b - a) * f,
        "__version__": "0.1",
    })

    def _call_userfunc(self, tree, new_children=None):
        f = getattr(np, tree.data, False)
        if f:
            return f(*new_children)

        return super(CalculateTree, self)._call_userfunc(tree, new_children)

    def decimal(self, x):
        try:
            return int(x)
        except:
            return np.float64(x)

    def decimalj(self, x):
        return complex(x)

    def evaluate(self, var, *args):
        return var.get()(*args)

    def __init__(self):
        self.vars = {}

    def set_var(self, ref, value):
        return ref.set(value)

    def get_var(self, ref):
        return ref.get()

    def clear_vars(self, *args):
        if not args:
            self.vars.clear()
            return "All variables cleared"
        else:
            for name in args:
                del self.vars[name]

            v = ", ".join(args)
            
            return f"Variables cleared: {v}"

    def show_vars(self):
        s = "\n".join(map(lambda i: f"{i[0]} = \n{i[1]}\n", self.vars.items()))

        return s

    def matrix_row(self, *args):
        return [*args]

    def form_matrix(self, *args):
        return np.matrix([*args])

    def form_array(self, arr):
        return np.array(arr)

    def var_ref(self, name):
        def setter(x):
            self.vars[name] = x

            return self.vars[name]
        
        def getter():
            if name in self.vars:
                return self.vars[name]
            elif name in self.builtins:
                return self.builtins[name]
            else:
                raise Exception(f"Variable {name} is not defined")
        
        return Ref(set=setter, get=getter)

    def index_ref(self, name, *args):
        ref = self.var_ref(name)

        return ref.index(args)


class State:
    def __init__(self):
        self.rules = Lark.open("lang/grammar.lark", parser='lalr')
        self.reset()

    def reset(self):
        self.ctx = CalculateTree()

    def parse(self, line):
        tree = self.rules.parse(line)

        return self.ctx.transform(tree)

if __name__ == "__main__":
    state = State()
    while True:
        s = input('> ')
        try:
            res = state.parse(s)
        except VisitError as e:
            print("Exception:")
            print(e.orig_exc)
        except UnexpectedInput as e:
            print("Parsing error:")
            print(e.get_context(s))
        except Exception as e:
            print(e)
        else:
            print(res)
