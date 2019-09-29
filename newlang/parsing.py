import re
from inspect import isclass
import numpy as np
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, VisitError
from .operations import op
from .parsetypes import *
from importlib import import_module

@v_args(inline=True)
class CalculateTree(Transformer):
    from .operations import op_plus, op_div, op_pow, op_assign, op_equals, \
        op_differs, op_evaluate, op_evaluate_get
    
    numpy_regex = re.compile(r"np_(\w[\w\d]*)")

    def _call_userfunc(self, tree, new_children=None):
        match = self.numpy_regex.search(tree.data)

        if match:
            f = getattr(np, match.group(1), None)

            if f:
                return op(f)(self, *new_children)
            else:
                raise Exception(f"Numpy function {match.group(1)} does not exist")
        else:
            return super(CalculateTree, self)._call_userfunc(tree, new_children)

    def make_variable(self, name):
        return Var(name)

    def var_eval(self, var):
        if isinstance(var, Expr) and var.optimize:
            return Const(var.get(self.ctx))
        elif isinstance(var, Var) and self.ctx.contains(var.name):
            return Const(var.get(self.ctx))
        else:
            return var

    def form_decimal(self, x):
        try:
            return Const(int(x))
        except:
            return Const(np.float64(x))

    def form_decimalj(self, x):
        return Const(complex(x))

    def form_matrix_row(self, *args):
        return Expr.compose(lambda *args: list(args), self.ctx, args)

    def form_matrix(self, *args):
        return Expr.compose(lambda *args: np.matrix(list(args)), self.ctx, args)

    def form_array(self, expr):
        return Expr.compose(lambda expr: np.array(list(expr)), self.ctx, (expr,))

    def form_function(self, *args):
        args = list(args)
        expr = args.pop(-1)

        return Function(expr, args)

    def form_string(self, arg):
        return Const(str(arg))

    def set_ctx(self, ctx):
        self.ctx = ctx

class State:
    global_ctx = Context({o: getattr(np, o) for o in np.__all__ if not isclass(getattr(np, o))})
    global_ctx.update({f"linalg_{o}" : getattr(np.linalg, o) for o in dir(np.linalg) if not isclass(getattr(np.linalg, o))})
    global_ctx.update({f"emath_{o}" : getattr(np.emath, o) for o in dir(np.emath) if not isclass(getattr(np.emath, o))})
    global_ctx.update({
        'true': True,
        'false': False,
        'null': None,
 
        # numpy matrix
        "zeros": lambda *shape: np.zeros(shape),
        "ones": lambda *shape: np.ones(shape),
        "rank": np.linalg.matrix_rank,
        "det": np.linalg.det,

        "vectorize": np.vectorize,
        "map": lambda f, arr: np.vectorize(f)(arr),

        # numpy complex
        'j': np.complex(0, 1),
        'complex': np.complex,

        # misc
        "version": "0.5.0",
    })
    rules = Lark.open("newlang/grammar.lark", parser='lalr')
    transformer = CalculateTree()

    def __init__(self, ctx=None, global_ctx=None):
        ctx = ctx or Context()

        if not global_ctx:
            self.ctx = ctx.with_parent(self.global_ctx)
        else:
            self.ctx = ctx.with_parent(global_ctx)

    def parse(self, line):
        self.transformer.set_ctx(self.ctx)

        try:
            tree = self.rules.parse(line)
            tree = self.transformer.transform(tree)

            val = tree.get(self.ctx)

            return val, None
        except VisitError as e:
            return None, e.orig_exc
        except UnexpectedInput as e:
            return None, e.get_context(line)
        except Exception as e:
            return None, e