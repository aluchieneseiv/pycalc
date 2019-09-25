from lark import Lark, Transformer, v_args
import math
import numpy as np

with open("grammar.lark", "r") as f:
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

    mul = lambda _, x, y: x * y
    div = lambda _, x, y: x / y
    solve = lambda _, x, y: np.linalg.solve(x, y)

    def pow(self, x, y):
        if isinstance(x, np.matrix):
            return np.linalg.matrix_power(x, int(y))
        else:
            return x ** y

    neg = lambda _, x: np.negative(x)
    pos = lambda _, x: np.positive(x)

    equals = lambda _, x, y: np.all(np.equal(x, y))
    differs = lambda _, x, y: not np.all(np.equal(x, y))

    decimal = np.float64

    builtins = {
        # numpy scalars
        "sin": np.sin,
        "sinh": np.sinh,
        "cos": np.cos,
        "cosh": np.cosh,
        "tan": np.tan,
        "tanh": np.tanh,
        "arcsin": np.arcsin,
        "arcsinh": np.arcsinh,
        "arccos": np.arccos,
        "arccosh": np.arccosh,
        "arctan": np.arctan,
        "arctanh": np.arctanh,
        "atan2": np.arctan2,
        "sqrt": np.sqrt,
        "exp": np.exp,
        "log": np.log,
        "log10": np.log10,
        "log1p": np.log1p,
        "floor": np.floor,
        "ceil": np.ceil,
        "round": np.round,
        "abs": np.abs,
        "interp": np.interp,
        "pi": np.pi,
        "e": np.e,

        # numpy matrix
        "eye": lambda n, m = None: np.eye(int(n), int(m) if m else None),
        "rank": np.linalg.matrix_rank,
        "det": np.linalg.det,
        "dot": np.dot,
        "norm": np.linalg.norm,
        "inv": np.linalg.inv,
        "zeros": lambda *shape: np.zeros([int(x) for x in shape]),
        "ones": lambda *shape: np.ones([int(x) for x in shape]),
        "arange": np.arange,
        "linspace": np.linspace,

        # misc
        "valinterp": lambda f, a, b: a + (b - a) * f,
        "version": "0.0.1",
    }

    def get_ordered_args(self, *args):
        return args

    def evaluate(self, var, args = None):
        if not args:
            return var.get()()
        else:
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
