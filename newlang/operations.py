from parsetypes import *
import numpy as np

# HELPERS
def unary_op(func):
    def unary_wrapper(self, rhs):
        return Expr(lambda ctx: func(rhs.get(ctx)))

    return unary_wrapper

def binary_op(func):
    def binary_wrapper(self, lhs, rhs):
        return Expr(lambda ctx: func(lhs.get(ctx), rhs.get(ctx)))

    return binary_wrapper

# OTHERS
def op_evaluate(self, var, *args):
    return Expr(lambda ctx: var.call(ctx, args), lambda ctx, val: var.setcall(ctx, args, val))

# UNARY
op_plus = unary_op(lambda x: +x)
op_neg = unary_op(lambda x: np.negative(x))
op_abs = unary_op(lambda x: np.abs(x))
op_not = unary_op(lambda x: not x)

# BINARY
def op_assign(self, lhs, rhs):
    def setter(ctx):
        lhs.set(ctx, rhs.get(ctx))
        return lhs.get(ctx)

    return Expr(setter)

op_add = binary_op(lambda x, y: np.add(x, y))
op_sub = binary_op(lambda x, y: np.sub(x, y))
op_mul = binary_op(lambda x, y: np.dot(x, y))
op_emul = binary_op(lambda x, y: np.multiply(x, y))
op_div = binary_op(lambda x, y: x / y)
op_ediv = binary_op(lambda x, y: np.divide(lhs, rhs))
op_solve = binary_op(lambda x, y: np.solve(x, y))
op_modulo = binary_op(lambda x, y: x % y)

@binary_op
def op_pow(x, y):
    if isinstance(x, np.matrix):
        return np.linalg.matrix_power(x, y)

    return lhs ** rhs

op_equals = binary_op(lambda x, y: np.all(np.equal(x, y)))
op_differs = binary_op(lambda x, y: not np.all(np.equal(x, y)))
op_less = binary_op(lambda x, y: np.less(x, y))
op_less_eq = binary_op(lambda x, y: np.less_equal(x, y))
op_greater = binary_op(lambda x, y: np.greater(x, y))
op_greater_eq = binary_op(lambda x, y: np.greater_equal(x, y))

op_and = binary_op(lambda x, y: x and y)
op_or = binary_op(lambda x, y: x or y)

# TERNARY
def op_ternary(self, cond, true, false):
    return Expr(lambda ctx: true.get(ctx) if cond.get(ctx) else false.get(ctx))
    