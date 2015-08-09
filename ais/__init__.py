import random

from ai import AINode, AIState
from properties.location_properties import get_accessible_things
import actions as a
import properties.materials as m


class FinderNode(AINode):
    def get_result(self):
        return None

    def tick(self):
        return AIState.Done


class AccessibleThings(FinderNode):
    def get_result(self):
        return get_accessible_things(self.thing)


class FilterThings(FinderNode):
    def __init__(self, ctx, sub_node, filter_method=None):
        super(FilterThings, self).__init__(ctx)
        self.sub_node = sub_node
        if filter_method is None:
            filter_method = lambda ctx, t: True
        self.filter_method = filter_method

    def begin(self):
        self.sub_node.begin()

    def tick(self):
        return self.sub_node.tick()

    def get_result(self):
        result = self.sub_node.tick()
        if result == AIState.Done:
            return [t for t in self.sub_node.get_result() if self.filter_method(self.context, t)]
        return []


class Message(AINode):
    def __init__(self, ctx, message, to_whom='others'):
        super(Message, self).__init__(ctx)
        self.message = message
        self.to_whom = to_whom

    def tick(self):
        message = self.message % self.get_parameters()
        if self.to_whom == 'self':
            self.thing.tell(message)
        elif self.to_whom == 'room':
            self.thing.tell_room(message)
        else:
            self.thing.broadcast(message)
        return AIState.Done

    def get_parameters(self):
        return {
            'thing': self.thing.name
        }


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
    def __init__(self, ctx, finder_ai):
        super(Eat, self).__init__(ctx)
        self.finder = finder_ai
        self.done = False

    def begin(self):
        self.finder.begin()
        self.done = False

    def tick(self):
        if self.done:
            return AIState.Done

        result = self.finder.tick()
        if result == AIState.Done:
            target = self.finder.get_result()
            if target:
                target = target[0]
                if a.EatAction.can_perform(target, self.thing):
                    a.EatAction.perform(target, self.thing)
                    return AIState.InProgress
            return AIState.Error
        else:
            return result


class Random(AINode):
    def __init__(self, ctx, *options):
        super(Random, self).__init__(ctx)
        self.options = options
        self.choice = None

    def begin(self):
        self.choice = None
        for option in self.options:
            option.begin()

    def tick(self):
        if self.choice is None:
            self.choice = random.randint(0, len(self.options) - 1)
        return self.options[self.choice].tick()


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
        if self.time_remaining < 0:
            return AIState.Done
        else:
            return AIState.InProgress


cat_ai = (Random, (Sequence, (Wander,), (Random, (Wait, 2), (Wait, 4), (Wait, 6))),
                  (Sequence, (Message, "%(thing)s falls asleep"),
                             (Random, (Wait, 2), (Wait, 4), (Wait, 6), (Wait, 8), (Wait, 10)),
                             (Message, "%(thing)s wakes up")),
                  (Eat, (FilterThings, (AccessibleThings,), lambda ctx, t: t.material == m.Flesh and a.EatAction.can_perform(t, ctx.thing))))
