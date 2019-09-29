from .parsetypes import *
import numpy as np

# HELPERS

def op(func):
    return lambda self, *args: Expr.compose(func, self.ctx, args)

def call_get(ctx, var, *args):
    var = var.get(ctx)
    args = tuple(arg.get(ctx) for arg in args)

    if np.ndim(var) > 0:
        return var.item(args)

    elif callable(var):
        return var(*args)

    elif isinstance(var, (list, tuple)):
        if len(args) > 1:
            raise Exception("Can only index list or tuple with a single variable")
        else:
            return var[args[0]]

    else:
        raise Exception(f"Object of type {type(var).__name__} cannot be called")

def call_set(ctx, val, var, *args):
    var = var.get(ctx)
    args = tuple(arg.get(ctx) for arg in args)

    if np.ndim(var) > 0:
        var.itemset(args, val)
        return val

    elif callable(var):
        raise Exception("Cannot assign to function call")

    elif isinstance(var, (list, tuple)):
        if len(args) > 1:
            raise Exception("Can only index list or tuple with a single variable")
        else:
            return var[args[0]]
    
    else:
        raise Exception(f"Object of type {type(var).__name__} cannot be called")

def attr_get(ctx, var, name):
    var = var.get(ctx)

    if hasattr(var, name):
        return getattr(var, name)
    else:
        raise Exception(f"Object of type {type(var).__name__} has no attribute {name}")

def attr_set(ctx, val, var, name):
    var = var.get(ctx)
    
    if hasattr(var, name):
        setattr(var, name, val)
        return val
    else:
        raise Exception(f"Object of type {type(var).__name__} has no attribute {name}")

# OTHERS
def op_evaluate_get(self, *args):
    return Expr.compose_raw(self.ctx, args, call_get)

def op_evaluate(self, *args):
    return Expr.compose_raw(self.ctx, args, call_get, call_set)

def op_attr_get(self, var, name):
    return Expr(getter=lambda ctx: attr_get(ctx, var, name), setter=None, ctx=self.ctx, optimize=var.optimize)

def op_attr(self, var, name):
    return Expr(getter=lambda ctx: attr_get(ctx, var, name), setter=lambda ctx, val: attr_set(ctx, val, var, name), ctx=self.ctx, optimize=var.optimize)

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
    