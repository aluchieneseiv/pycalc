from lark import Lark, Transformer, v_args
import math

with open("grammar.lark", "r") as f:
    grammar = f.read()

@v_args(inline=True)
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = float
    pow = lambda _, a, b: a ** b

    def evaluate(self, fname, *args):
        return self.vars[fname](*args)

    def __init__(self):
        self.vars = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "cot": lambda x: 1 / math.tan(x),
            "arcsin": math.asin,
            "arccos": math.acos,
            "atan": math.atan,
            "atan2": math.atan2,
            "acot": lambda x: math.atan(1 / x),
            "version" : "0.0.1"
        }

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        return self.vars[name]


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
