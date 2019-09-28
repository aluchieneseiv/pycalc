from parsetypes import *
import numpy as np

# HELPERS

def op(func):
    return lambda self, *args: Expr.compose(func, self.ctx, args)

def call_get(ctx, var, *args):
    val = var.get(ctx)

    if np.ndim(val) > 0:
        args = list(args)
        i = args.pop(-1).get(ctx)

        while args:
            val = val[args.pop(0).get(ctx)]

        return val[i]
    elif callable(val):
        return val(*[arg.get(ctx) for arg in args])
    else:
        raise Exception(f"Object of type {type(val).__name__} cannot be called")

def call_set(ctx, newval, var, *args):
    args = list(args)
    val = var.get(ctx)

    if np.ndim(val) > 0:
        i = args.pop(-1).get(ctx)
        while args:
            val = val[args.pop(0).get(ctx)]

        val[i] = newval

        return newval
    elif callable(val):
        raise Exception("Cannot assign to function call")
    else:
        raise Exception(f"Object of type {type(val).__name__} cannot be called")

# OTHERS
def op_evaluate_get(self, *args):
    return Expr.compose_raw(self.ctx, args, call_get)

def op_evaluate(self, *args):
    return Expr.compose_raw(self.ctx, args, call_get, call_set)

# UNARY
op_plus = op(lambda x: +x)

# BINARY
def op_assign(self, lhs, rhs):
    def func(ctx):
        lhs.set(ctx, rhs.get(ctx))
        return lhs.get(ctx)

    return Expr(func, ctx=self.ctx, optimize=rhs.optimize)

op_div = op(lambda x, y: x / y)
op_solve = op(lambda x, y: np.linalg.solve(x, y))

@op
def op_pow(x, y):
    if isinstance(x, np.matrix):
        return np.linalg.matrix_power(x, y)

    return x ** y

op_equals = op(lambda x, y: np.all(np.equal(x, y)))
op_differs = op(lambda x, y: not np.all(np.equal(x, y)))
    