import random

from ai import AINode, AIState, AliasNode
from actions import attack, walk_thing
from location import get_path, locations_within
from properties.location_properties import get_accessible_things
from templates import instantiate_template
from utils import pick_random
import properties.location_properties as lp
import actions as a
import properties.materials as m
import properties as p
import templates as t


def do_once(func):
    def inner(*args, **kwargs):
        self = args[0]
        rvalue = getattr(self, '__retval', None)
        if rvalue:
            return rvalue

        new_rvalue = func(*args, **kwargs)
        if new_rvalue != AIState.InProgress:
            self.__retval = new_rvalue
        return new_rvalue
    return inner


class DoOnceNode(AINode):
    # AIState equivalent for "I did this action, it took my turn, but i
    # completed it and next time don't tick me
    Completed = 'completed'

    def __init__(self, ctx, *args, **kwargs):
        super(DoOnceNode, self).__init__(ctx, *args, **kwargs)
        self.cached_result = None

    def begin(self):
        self.cached_result = None

    def tick(self):
        if self.cached_result is not None:
            return self.cached_result

        rvalue = self.perform()

        if rvalue == DoOnceNode.Completed:
            self.cached_result = AIState.Done
            return AIState.InProgress

        if rvalue != AIState.InProgress:
            self.cached_result = rvalue

        return rvalue

    def perform(self):
        raise NotImplementedError()


class AddNearbyTargets(AINode):
    def __init__(self, ctx, func):
        super(AddNearbyTargets, self).__init__(ctx)
        self.func = func

    def tick(self):
        for thing in get_accessible_things(self.thing):
            if self.func(self.context, thing) and thing not in self.context.targets:
                self.context.targets.append(thing)
        return AIState.Done


class AttackTargets(AINode):
    def tick(self):
        target = None
        if self.context.focus_target:
            target = self.context.focus_target
        else:
            accessible_things = get_accessible_things(self.thing)
            accessible_targets = [
                t for t in self.context.targets if t in accessible_things
            ]
            if accessible_targets:
                target = accessible_targets[0]
        if target:
            if not target.alive:
                return AIState.Done
            attack(self.thing, target)
            return AIState.InProgress
        return AIState.Fail


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


class Eat(DoOnceNode):
    def __init__(self, ctx, filter_func):
        super(Eat, self).__init__(ctx)
        self.filter_func = filter_func

    def perform(self):
        if not self.thing.is_property(lp.HasStomach):
            return AIState.Fail

        # Check for things already in belly
        okay = any(t for t in self.thing.get_property(lp.HasStomach).get_all_things() if self.filter_func(self.context, t))
        if okay:
            return AIState.Done

        things = [th for th in get_accessible_things(self.thing) if self.filter_func(self.context, th)]
        if things:
            target = pick_random(things)
            if a.EatAction.can_perform(target, self.thing):
                a.EatAction.perform(target, self.thing)
                return DoOnceNode.Completed
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


class FilterTargets(AINode):
    def __init__(self, ctx, func):
        super(FilterTargets, self).__init__(ctx, func)
        self.func = func

    def tick(self):
        self.context.targets = filter(self.context.targets, self.func)
        return AIState.Done


class Gas(DoOnceNode):
    def perform(self):
        liquid_things = [t for t in self.thing.location.things if t.is_property(p.Liquid)]
        thing = pick_random(liquid_things)
        if thing:
            gas = thing.duplicate()
            gas.remove_properties_of_types(['mechanical', 'physical'])
            gas.become(p.Gas)
            gas.name = 'some mist'
            self.thing.location.add_thing(gas)
            self.thing.broadcast("%s takes a big gulp of %s and burps it out as a mist" % (self.thing.name, thing.name))
            self.thing.tell("You take a gulp of %s and belch it out as mist" % thing.name)
            return DoOnceNode.Completed
        return AIState.Fail


class Go(AINode):
    def __init__(self, ctx, getty):
        super(Go, self).__init__(ctx)
        self.getty = getty
        self.destination = None

    def tick(self):
        self.destination = self.getty(self.context)
        if not self.destination:
            return AIState.Fail
        if self.thing.location == self.destination:
            return AIState.Done
        path = get_path(self.thing.location, self.destination, self.thing)
        if path is None:
            return AIState.Fail
        elif path == []:
            return AIState.Done
        else:
            exit = next((e for e in self.thing.location.get_all_exits() if e.to_location == path[0]), None)
            if exit:
                walk_thing(self.thing, exit)
                return AIState.InProgress
            else:
                return AIState.Fail


class Message(DoOnceNode):
    def __init__(self, ctx, message, to_whom='others'):
        super(Message, self).__init__(ctx)
        self.message = message
        self.to_whom = to_whom

    def perform(self):
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


class Nibble(DoOnceNode):
    def __init__(self, ctx, filter_func):
        super(Nibble, self).__init__(ctx)
        self.filter_func = filter_func

    def perform(self):
        if not self.thing.is_property(lp.HasStomach):
            return AIState.Fail

        things = [th for th in get_accessible_things(self.thing) if self.filter_func(self.context, th)]
        if things:
            nibble_target = pick_random(things)
            self.thing.broadcast("%s nibbles on %s" % (self.thing.name, nibble_target.name))
            bolus = instantiate_template(t.Bolus, self.thing.get_property(lp.HasStomach))
            bolus.name = 'a %s bolus' % nibble_target.material.name
            for key, prop in nibble_target.properties.items():
                bolus.properties[key] = prop.clone(bolus)
            return DoOnceNode.Completed
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


class Search(AINode):
    def __init__(self, ctx, done_func, max_distance=10):
        super(Search, self).__init__(ctx)
        self.done_func = done_func
        self.max_distance = max_distance
        self.searched_rooms = []
        self.next_room = None

    def begin(self):
        self.searched_rooms = []
        self.rooms_to_search = filter(lambda l: not l.is_dangerous(self.thing), locations_within(self.thing.location, self.max_distance, self.thing))
        self.next_room = pick_random(self.rooms_to_search)

    def tick(self):
        if self.thing.location not in self.searched_rooms:
            self.searched_rooms.append(self.thing.location)
        if self.thing.location in self.rooms_to_search:
            self.rooms_to_search.remove(self.thing.location)

        if self.done_func(self.context):
            return AIState.Done
        elif not self.rooms_to_search:
            return AIState.Fail
        else:
            next_leg = None
            while not next_leg:
                path_to_next = get_path(self.thing.location, self.next_room, self.thing)
                if path_to_next:
                    next_leg = path_to_next[0]
                else:  # either already in target room or else no path to target room
                    if self.next_room in self.rooms_to_search:
                        self.rooms_to_search.remove(self.next_room)
                    if self.rooms_to_search:
                        self.next_room = pick_random(self.rooms_to_search)
                    else:  # Out of rooms
                        return AIState.Fail
            next_exits = [
                e for e in self.thing.location.get_all_exits()
                if e.can_traverse(self.thing) and e.to_location == next_leg
            ]
            if next_exits:
                walk_thing(self.thing, next_exits[0])
                return AIState.InProgress


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


class Test(AINode):
    def __init__(self, ctx, func):
        super(Test, self).__init__(ctx)
        self.func = func

    def tick(self):
        return AIState.Done if self.func(self.context) else AIState.Fail


class Wander(AINode):
    def begin(self):
        self.has_wandered = False

    def tick(self):
        if self.has_wandered:
            return AIState.Done

        entrances = [e for e in self.thing.location.get_all_exits() if e.can_traverse(self.thing) and not e.to_location.is_dangerous(self.thing)]
        if entrances:
            entrance = entrances[random.randint(0, len(entrances) - 1)]
            walk_thing(self.thing, entrance)
            self.has_wandered = True
            return AIState.InProgress
        else:
            return AIState.Error


class WithFocus(AINode):
    def __init__(self, ctx, chooser, subnode):
        super(WithFocus, self).__init__(ctx)
        self.subnode = subnode
        self.chooser = chooser
        self.focus_target = None

    def begin(self):
        self.focus_target = None

    def tick(self):
        if not self.focus_target:
            things = filter(lambda x: not x.destroyed, get_accessible_things(self.thing))
            target = self.chooser(self.context, things)
            self.focus_target = target
            if not target:
                return AIState.Fail
        else:
            if self.focus_target.destroyed:
                self.focus_target = None
                self.context.focus_target = None
                return AIState.Fail
        self.context.focus_target = self.focus_target
        return self.subnode.tick()


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


class Hunt(AliasNode):
    alias = lambda ffunc: (Selector, (WithFocus, lambda ctx, options: next((o for o in options if ffunc(ctx, o)), None),
                                      (Sequence,
                                       (Go, lambda ctx: ctx.focus_target.location),
                                       (AttackTargets,))),
                                     (Search, lambda ctx: any([t for t in ctx.thing.location.things if ffunc(ctx, t)])))


class Poisoned(AliasNode):
    alias = (Test, lambda ctx: ctx.thing.is_property(p.Poisoned))


class SearchForThing(AliasNode):
    alias = lambda f: (Search, lambda ctx: any(f(ctx, t) for t in get_accessible_things(ctx.thing)))


def is_tasty_to_cat(ctx, thing):
    return thing.material == m.Flesh and thing.size < ctx.thing.size


cat_ai = (Random, (Meander,),
                  (Sleep,),
                  (Sequence, (Hunt, is_tasty_to_cat),
                             (Eat, lambda ctx, t: not t.alive and is_tasty_to_cat(ctx, t))),
                  (WanderUntilCan, (Selector, (Eat, is_tasty_to_cat),
                                              (Fail, (Message, "%(thing)s leers around hungrily")))))

mouse_ai = (Random, (Meander,),
                    (Sequence, (WanderUntilCan, (RoomMatches, lambda ctx, r: (r.size - ctx.thing.size) <= 3)),
                               (Sleep,)),
                    (WanderUntilCan, (Nibble, lambda ctx, t: t.material == m.Plant)))

wolf_ai = (Selector, (Sequence, (Poisoned,),
                                (SearchForThing, lambda ctx, thing: thing.is_property(p.Antidote)),
                                (Nibble, lambda ctx, t: t.is_property(p.Antidote))),
                     (Random, (Sequence, (Meander,), (Meander,), (Meander,)),
                              (Sequence, (Go, lambda ctx: ctx.home),
                                         (Sleep,)),
                              (Sequence, (Hunt, is_tasty_to_cat),
                                         (Eat, is_tasty_to_cat))))


def location_contains_liquid(context):
    location = context.thing.location
    return bool([t for t in location.things if t.is_property(p.Liquid)])


frog_ai = (Sequence, (Search, location_contains_liquid),
                     (Random, (Sleep,),
                              (Gas,)))
