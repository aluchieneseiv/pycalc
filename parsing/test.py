from lark import Lark, Transformer, v_args
import math

with open("grammar.lark", "r") as f:
    grammar = f.read()

@v_args(inline=True)
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = float
    pow = lambda _, a, b: a ** b

    builtins = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "cot": lambda x: 1 / math.tan(x),
        "arcsin": math.asin,
        "arccos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "acot": lambda x: math.atan(1 / x),
        "version": "0.0.1"
    }

    def evaluate(self, fname, *args):
        return self.var(fname)(*args)

    def __init__(self):
        self.vars = {}

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        if name in self.vars:
            return self.vars[name]
        
        return self.builtins[name]

    def clear_vars(self, *args):
        if not args:
            self.vars.clear()
            return "All variables cleared"
        else:
            for name in args:
                del self.vars[name]

            v = ", ".join(args)
            
            return f"Variables {v} cleared"

    def show_vars(self):
        s = "\n".join(map(lambda i: f"  {i[0]} = {i[1]}", self.vars.items()))

        return s


calc_parser = Lark(grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse


while True:
    s = input('> ')
    try:
        res = calc(s)
    except Exception as e:
        print(e)
    else:
        print(res)
