from lark import Lark, Transformer, v_args
from lark.exceptions import VisitError, UnexpectedInput
import math
import numpy as np
from inspect import isclass
from parsetypes import Context, Const, Var, Expr, EmptyContext


with open("newlang/grammar.lark", "r") as f:
    grammar = f.read()


@v_args(inline=True)
class CalculateTree(Transformer):
    from operations import op_plus, op_neg, op_not, op_add, op_sub, \
        op_mul, op_div, op_modulo, op_pow, op_greater, op_greater_eq, \
        op_less, op_less_eq, op_assign, op_equals, op_differs, op_and, \
        op_or, op_ternary, op_evaluate
    

    def make_variable(self, name):
        return Var(name)

    def form_decimal(self, x):
        try:
            return Const(int(x))
        except:
            return Const(np.float64(x))

    def form_decimalj(self, x):
        return Const(complex(x))

    def form_matrix_row(self, *args):
        return Expr(lambda ctx: [arg.get(ctx) for arg in args])

    def form_matrix(self, *args):
        return Expr(lambda ctx: np.matrix([arg.get(ctx) for arg in args]))

    def form_array(self, expr):
        return Expr(lambda ctx: np.array(expr.get(ctx)))


class State:
    GlobalCtx = Context({o: getattr(np, o) for o in np.__all__ if not isclass(getattr(np, o))})
    GlobalCtx.update({
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

    def __init__(self):
        self.rules = Lark(grammar, parser='lalr', transformer=CalculateTree())
        self.ctx = self.GlobalCtx.spawn_child()

    def clear(self):
        self.ctx.clear()

    def parse(self, line):
        tree = self.rules.parse(line)

        return tree.get(self.ctx)

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
            print("Exception:")
            print(e)
        else:
            print(res)
