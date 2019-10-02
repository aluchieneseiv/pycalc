class Context:
    def __init__(self, var_map=None):
        self.var_map = var_map or dict()

    def get(self, name):
        return self.var_map[name]

    def contains(self, name):
        return name in self.var_map

    def set(self, name, val):
        self.var_map[name] = val

    def clear(self):
        self.var_map.clear()

    def update(self, var_map):
        self.var_map.update(var_map)

    def with_parent(self, parent):
        return NestedContext(parent, self.var_map)

class NestedContext(Context):
    def __init__(self, parent, var_map=None):
        self.parent = parent
        self.var_map = var_map or dict()
    
    def get(self, name):
        if name in self.var_map:
            return self.var_map[name]

        return self.parent.get(name)

    def contains(self, name):
        return name in self.var_map or self.parent.contains(name)

class EmptyContext:
    @classmethod
    def get(self, name):
        raise Exception("Empty context")
    
    @classmethod
    def contains(self, name):
        return False

    @classmethod
    def set(self, name):
        pass

    @classmethod
    def clear(self):
        pass
    
    @classmethod
    def with_parent(self, parent):
        return parent

class Const:
    def __init__(self, val):
        self.val = val

    def get(self, ctx):
        return self.val
    
    def set(self, ctx, val):
        raise Exception("Cannot assign value to constant")

class Var:
    def __init__(self, name):
        self.name = name

    def get(self, ctx):
        if ctx.contains(self.name):
            return ctx.get(self.name)
        
        raise Exception(f"Variable {self.name} is not defined")

    def set(self, ctx, val):
        ctx.set(self.name, val)

        return ctx.get(self.name)

class Expr:
    def __init__(self, getter, setter=None):
        self.getter = getter
        self.setter = setter
    
    def set(self, ctx, val):
        if not self.setter:
            raise Exception("Cannot assign value to expression")

        self.setter(ctx, val)

    def get(self, ctx):
        if ctx is EmptyContext:
            raise Exception("Cannot evaluate")

        return self.getter(ctx)

    @classmethod
    def compose(self, func, ctx, args):
        return Expr(lambda ctx: func(*[arg.get(ctx) for arg in args]))

    @classmethod
    def compose_raw(self, ctx, args, getter, setter=None):
        def get(ctx):
            return getter(ctx, *args)
        
        def set(ctx, val):
            return setter(ctx, val, *args)
        
        if setter:
            return Expr(get, set)
        else:
            return Expr(get, None)

class Function:
    def __init__(self, args, expr):
        self.expr = expr
        self.args = args

    def get(self, ctx):
        def func(*args):
            child_ctx = Context().with_parent(ctx)

            if len(args) != len(self.args):
                raise Exception("Function called with different number of arguments")

            for i, name in enumerate(self.args):
                child_ctx.set(name, args[i])
                
            return self.expr.get(child_ctx)

        return func

    def set(self, ctx, val):
        raise Exception("Cannot assign to function")

class NoOutput:
    pass

class Parameter:
    pass