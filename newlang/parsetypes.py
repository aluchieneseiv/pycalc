class Context:
    def __init__(self, dict=dict()):
        self.dict = dict

    def get(self, name):
        return self.dict[name]

    def contains(self, name):
        return name in self.dict

    def set(self, name, val):
        self.dict[name] = val

    def clear(self):
        self.dict.clear()

    def spawn_child(self):
        return NestedContext(self)

    def update(self, dict):
        self.dict.update(dict)

class NestedContext(Context):
    def __init__(self, parent, dict = dict()):
        self.parent = parent
        self.dict = dict
    
    def get(self, name):
        if name in self.dict:
            return self.dict[name]

        return self.parent.get(name)

    def contains(self, name):
        return name in self.dict or self.parent.contains(name)

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
    def spawn_child(self, dict=dict()):
        return Context(dict)

class Callable:
    def call(self, ctx, args):
        val = self.get(ctx)

        if callable(val):
            return val(*[arg.get(ctx) for arg in args])
        else:
            args = list(args)
            i = args.pop(-1)
            while args:
                val = val[args.pop(0)]

            return val[i]

    def setcall(self, ctx, args, newval):
        val = self.get(ctx)

        if callable(val):
            raise Exception("Cannot assign to function call")
        else:
            args = list(args)
            i = args.pop(-1)
            while args:
                val = val[args.pop(0)]

            val[i] = newval

        #TODO: MOVE CALL/SETCALL TO OPERATIONS.PY AND HAVE SEPARATE CHECK FOR MATRICES


class Const(Callable):
    def __init__(self, val):
        self.val = val

    def get(self, ctx):
        return self.val
    
    def set(self, ctx, val):
        raise Exception("Cannot assign value to constant")

class Var(Callable):
    def __init__(self, name):
        self.name = name

    def get(self, ctx):
        if ctx.contains(self.name):
            return ctx.get(self.name)
        
        raise Exception(f"Variable {self.name} is not defined")

    def set(self, ctx, val):
        ctx.set(self.name, val)

        return ctx.get(self.name)

class Expr(Callable):
    def __new__(cls, func, setter=None, ctx=EmptyContext):
        if not setter:
            try:
                return Const(func(ctx))
            except:
                pass

        return object.__new__(Expr)

    def __init__(self, func, setter=None):
        self.getter = func
        self.setter = setter
    
    def set(self, ctx, val):
        if not self.setter:
            raise Exception("Cannot assign value to expression")

        self.setter(ctx, val)

    def get(self, ctx):
        if ctx is EmptyContext:
            raise Exception("Cannot evaluate")

        return self.getter(ctx)