from lark import Lark, Transformer, v_args
import math
import numpy as np
from inspect import isclass


with open("parsing/grammar.lark", "r") as f:
    grammar = f.read()

class Ref:
    def __init__(self, set=None, get=None):
        self.set = set
        self.get = get

@v_args(inline=True)
class CalculateTree(Transformer):
    add = lambda _, x, y: np.add(x, y)
    sub = lambda _, x, y: np.subtract(x, y)

    emul = lambda _, x, y: np.multiply(x, y)
    ediv = lambda _, x, y: np.divide(x, y)
    epow = lambda _, x, y: np.power(x, y)

    mul = lambda _, x, y: np.dot(x, y)
    div = lambda _, x, y: x / y
    solve = lambda _, x, y: np.linalg.solve(x, y)

    pow = lambda _, x, y: x ** y

    neg = lambda _, x: np.negative(x)
    abs = lambda _, x: np.abs(x)

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
        "version": "0.0.1",
    })


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
            else:
                return self.builtins[name]
        
        return Ref(set=setter, get=getter)

    def matrix_ref(self, name, N, M=None):
        if M is None:
            def setter(x):
                self.vars[name][0][int(N)] = x

                return self.vars[name]

            getter = lambda: self.vars[name][0][int(N)]
        else:
            def setter(x):
                self.vars[name][int(M)][int(N)] = x

                return self.vars[name]
            
            getter = lambda: self.vars[name][int(M)][int(N)]

        return Ref(set=setter, get=getter)


calc_parser = Lark(grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse


while True:
    s = input('> ')
    try:
        res = calc(s)
    except Exception as e:
        print("Exception:")
        print(e)
    else:
        print(res)
