class AIState(object):
    Done = 1
    InProgress = 2
    Fail = 3

    Error = 100


class AIContext(object):
    def __init__(self, thing):
        self.thing = thing

        self.hunger = 0
        self.anger = 0
        self.tiredness = 0

        self.aggressors = []
        self.friends = []


class AINode(object):
    def __init__(self, context):
        self.context = context

    @property
    def thing(self):
        return self.context.thing

    def begin(self):
        pass

    def tick(self):
        return AIState.Done


# Swizzle with context
def create_ai(struct, ctx):
    from ais import aliases
    ai_class = struct[0]
    has_kwargs = isinstance(struct[-1], dict)
    if has_kwargs:
        args = struct[1:-1]
        kwargs = struct[-1]
    else:
        args = struct[1:]
        kwargs = {}

    # aliases
    if isinstance(ai_class, str):
        return create_ai(aliases[ai_class](*args, **kwargs), ctx)

    args = [create_ai(a, ctx) if isinstance(a, tuple) else a for a in args]
    for key, value in kwargs:
        if isinstance(value, tuple):
            kwargs[key] = create_ai(value)
    return ai_class(ctx, *args, **kwargs)
