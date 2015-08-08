import random


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
        pass


class FinderNode(AINode):
    def get_result(self):
        return None


class Message(AINode):
    def __init__(self, ctx, message, to_self=False):
        super(Message, self).__init__(ctx)
        self.message = message

    def tick(self):
        if self.to_self:
            self.thing.tell(self.message)
        else:
            self.thing.tell_room(self.message)
        return AIState.Done


class Sequence(AINode):
    def __init__(self, ctx, *tasks):
        self.tasks = tasks
        self.idx = 0

    def begin(self):
        self.idx = 0
        for task in self.tasks:
            task.begin()

    def tick(self):
        if self.idx >= len(self.tasks):
            return AIState.Done

        result = self.tasks[self.idx].tick()
        if result == AIState.Done:
            self.idx += 1
            return self.tick()
        else:
            return result


class Eat(AINode):
    def __init__(self, finder_ai):
        pass


class Wander(AINode):
    def begin(self):
        self.has_wandered = False

    def tick(self):
        if self.has_wandered:
            return AIState.Done

        entrances = [e for e in self.thing.location.get_all_exits() if e.can_traverse(self.thing) and e.to_location.can_contain(self.thing)]
        if entrances:
            entrance = entrances[random.randint(0, len(entrances) - 1)]
            from_location = self.thing.location
            self.thing.tell_room("%s goes %s" % (self.thing.name, entrance.description))
            entrance.to_location.add_thing(self.thing)
            self.thing.tell_room("%s arrives from %s" % (self.thing.name, from_location.name))
            self.has_wandered = True
            return AIState.InProgress
        else:
            return AIState.Error


class Wait(AINode):
    def __init__(self, ctx, time):
        super(Wait, self).__init__(ctx)
        self.time = time
        self.time_remaining = time

    def begin(self):
        self.time_remaining = self.time

    def tick(self):
        self.time_remaining -= 1
        if self.time_remaining <= 0:
            return AIState.Done
        else:
            return AIState.InProgress


# Swizzle with context
def create_ai(struct, ctx):
    ai_class = struct[0]
    has_kwargs = isinstance(struct[-1], dict)
    if has_kwargs:
        args = struct[1:-1]
        kwargs = struct[-1]
    else:
        args = struct[1:]
        kwargs = {}

    args = [create_ai(a, ctx) if isinstance(a, tuple) else a for a in args]
    for key, value in kwargs:
        if isinstance(value, tuple):
            kwargs[key] = create_ai(value)
    return ai_class(ctx, *args, **kwargs)

cat_ai = (Sequence, (Wander,), (Wait, 2))
