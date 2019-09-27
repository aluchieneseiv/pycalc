from parsetypes import *
import numpy as np

# HELPERS

def op(func):
    return lambda self, *args: Expr(lambda ctx: func(*[arg.get(ctx) for arg in args]))

def call_get(ctx, var, args):
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

def call_set(ctx, var, args, newval):
    val = var.get(ctx)

    if np.ndim(val) > 0:
        args = list(args)
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
def op_evaluate(self, var, *args):
    return Expr(lambda ctx: call_get(ctx, var, args), lambda ctx, val: call_set(ctx, var, args, val))

# UNARY
op_plus = op(lambda x: +x)
op_neg = op(lambda x: np.negative(x))
op_abs = op(lambda x: np.abs(x))
op_not = op(lambda x: not x)

# BINARY
def op_assign(self, lhs, rhs):
    def setter(ctx):
        lhs.set(ctx, rhs.get(ctx))
        return lhs.get(ctx)

    return Expr(setter)

op_add = op(lambda x, y: np.add(x, y))
op_sub = op(lambda x, y: np.subtract(x, y))
op_mul = op(lambda x, y: np.dot(x, y))
op_emul = op(lambda x, y: np.multiply(x, y))
op_div = op(lambda x, y: x / y)
op_ediv = op(lambda x, y: np.divide(lhs, rhs))
op_solve = op(lambda x, y: np.solve(x, y))
op_modulo = op(lambda x, y: x % y)

@op
def op_pow(x, y):
    if isinstance(x, np.matrix):
        return np.linalg.matrix_power(x, y)

    return lhs ** rhs

op_equals = op(lambda x, y: np.all(np.equal(x, y)))
op_differs = op(lambda x, y: not np.all(np.equal(x, y)))
op_less = op(lambda x, y: np.less(x, y))
op_less_eq = op(lambda x, y: np.less_equal(x, y))
op_greater = op(lambda x, y: np.greater(x, y))
op_greater_eq = op(lambda x, y: np.greater_equal(x, y))

op_and = op(lambda x, y: x and y)
op_or = op(lambda x, y: x or y)

# TERNARY
def op_ternary(self, cond, true, false):
    return Expr(lambda ctx: true.get(ctx) if cond.get(ctx) else false.get(ctx))
    