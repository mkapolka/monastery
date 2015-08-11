import random

from ai import AINode, AIState, AliasNode
from properties.location_properties import get_accessible_things
from templates import instantiate_template
from utils import pick_random
import properties.location_properties as lp
import actions as a
import properties.materials as m
import properties as p
import templates as t


class Description(AINode):
    def __init__(self, ctx, message):
        super(Description, self).__init__(ctx)
        self.done = False
        self.message = message

    def begin(self):
        self.done = False

    def tick(self):
        if not self.done:
            self.done = True
            self.context.description = self.message
        return AIState.Done


class Eat(AINode):
    def __init__(self, ctx, filter_func):
        super(Eat, self).__init__(ctx)
        self.filter_func = filter_func

    def begin(self):
        self.eaten = False

    def tick(self):
        if not self.thing.is_property(lp.HasStomach):
            return AIState.Fail

        if self.eaten:
            return self.eaten

        # Check for things already in belly
        okay = any(t for t in self.thing.get_property(lp.HasStomach).get_all_things() if self.filter_func(t))
        if okay:
            self.eaten = AIState.Done
            return self.eaten

        things = [th for th in get_accessible_things(self.thing) if self.filter_func(self.context, th)]
        if things:
            target = pick_random(things)
            if a.EatAction.can_perform(target, self.thing):
                a.EatAction.perform(target, self.thing)
                self.eaten = AIState.Done
                return AIState.InProgress
        self.eaten = AIState.Fail
        return AIState.Fail


class Fail(AINode):
    def __init__(self, ctx, child):
        super(Fail, self).__init__(ctx)
        self.child = child

    def begin(self):
        self.child.begin()

    def tick(self):
        if self.child.tick() == AIState.InProgress:
            return AIState.InProgress
        return AIState.Fail


class Message(AINode):
    def __init__(self, ctx, message, to_whom='others'):
        super(Message, self).__init__(ctx)
        self.message = message
        self.to_whom = to_whom
        self.fired = False

    def begin(self):
        self.fired = False

    def tick(self):
        if self.fired:
            return AIState.Done

        message = self.message % self.get_parameters()
        if self.to_whom == 'self':
            self.thing.tell(message)
        elif self.to_whom == 'room':
            self.thing.tell_room(message)
        else:
            self.thing.broadcast(message)
        self.fired = True
        return AIState.Done

    def get_parameters(self):
        return {
            'thing': self.thing.name
        }


class Nibble(AINode):
    def __init__(self, ctx, filter_func):
        super(Nibble, self).__init__(ctx)
        self.filter_func = filter_func

    def begin(self):
        self.nibbled = False

    def tick(self):
        if not self.thing.is_property(lp.HasStomach):
            return AIState.Fail

        if self.nibbled:
            return AIState.Done

        things = [th for th in get_accessible_things(self.thing) if self.filter_func(self.context, th)]
        if things:
            nibble_target = pick_random(things)
            self.thing.broadcast("%s nibbles on %s" % (self.thing.name, nibble_target.name))
            bolus = instantiate_template(t.Bolus)
            bolus.name = 'a %s bolus' % nibble_target.material.name
            bolus.become(p.Digestible)
            for key, prop in nibble_target.properties.items():
                bolus.properties[key] = prop.clone(bolus)
            self.thing.get_property(lp.HasStomach).add_thing(bolus)
            self.nibbled = True
            return AIState.InProgress
        return AIState.Fail


class Random(AINode):
    def __init__(self, ctx, *options):
        super(Random, self).__init__(ctx)
        self.options = options
        self.choice = None

    def begin(self):
        self.choice = pick_random(self.options)
        for option in self.options:
            option.begin()

    def tick(self):
        return self.choice.tick()


class RepeatUntilDone(AINode):
    def __init__(self, ctx, subnode):
        super(RepeatUntilDone, self).__init__(ctx)
        self.subnode = subnode

    def begin(self):
        self.subnode.begin()

    def tick(self):
        result = self.subnode.tick()
        if result == AIState.Fail:
            self.begin()
            return AIState.InProgress
        else:
            return result


class RoomMatches(AINode):
    def __init__(self, ctx, room_lambda):
        super(RoomMatches, self).__init__(ctx)
        self.filter_func = room_lambda

    def tick(self):
        if self.filter_func(self.context, self.thing.location):
            return AIState.Done
        else:
            return AIState.Fail


class Sequence(AINode):
    def __init__(self, ctx, *tasks):
        self.tasks = tasks

    def begin(self):
        for task in self.tasks:
            task.begin()

    def tick(self):
        for task in self.tasks:
            result = task.tick()
            if result != AIState.Done:
                return result
        return AIState.Done


class Selector(AINode):
    def __init__(self, ctx, *tasks):
        super(Selector, self).__init__(ctx)
        self.tasks = tasks

    def begin(self):
        for task in self.tasks:
            task.begin()

    def tick(self):
        for task in self.tasks:
            result = task.tick()
            if result != AIState.Fail:
                return result
        return AIState.Fail


class Wander(AINode):
    def begin(self):
        self.has_wandered = False

    def tick(self):
        if self.has_wandered:
            return AIState.Done

        entrances = [e for e in self.thing.location.get_all_exits() if e.can_traverse(self.thing)]
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


# Aliases
class Meander(AliasNode):
    alias = (Sequence, (Description, "is wandering"),
                       (Random, (Wait, 2), (Wait, 4), (Wait, 6)),
                       (Wander,))


class Sleep(AliasNode):
    alias = (Sequence, (Message, "%(thing)s falls asleep"),
                       (Description, "is asleep"),
                       (Random, (Wait, 2), (Wait, 4), (Wait, 6), (Wait, 8), (Wait, 10)),
                       (Message, "%(thing)s wakes up"))


class WanderUntilCan(AliasNode):
    alias = lambda thing: (RepeatUntilDone, (Selector, thing,
                                             (Fail, (Wander,)),))

cat_ai = (Random, (Meander,),
                  (Sleep,),
                  (WanderUntilCan, (Selector, (Eat, lambda ctx, x: x.material == m.Flesh and x.size < ctx.thing.size),
                                              (Fail, (Message, "%(thing)s leers around hungrily")))))

mouse_ai = (Random, (Meander,),
                    (Sequence, (WanderUntilCan, (RoomMatches, lambda ctx, r: (r.size - ctx.thing.size) <= 3)),
                               (Sleep,)),
                    (WanderUntilCan, (Nibble, lambda ctx, t: t.material == m.Plant)))
