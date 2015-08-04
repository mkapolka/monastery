import collections


class Reaction(object):
    predicates = []
    anti_predicates = []
    event = ""

    @classmethod
    def should_perform(cls, event):
        if event.name == cls.event:
            matches_predicates = all(map(lambda x: event.target.is_property(x), cls.predicates))
            matches_anti_predicates = all(map(lambda x: not event.target.is_property(x), cls.anti_predicates))
            return matches_predicates and matches_anti_predicates
        return False

    @classmethod
    def perform(cls, event):
        raise NotImplementedError("I'm a %s" % cls)


class Event(object):
    def __init__(self, name, target, **kwargs):
        self.name = name
        self.target = target
        for key, value in kwargs.items():
            setattr(self, key, value)


event_queue = collections.deque()


def enqueue_event(event):
    event_queue.append(event)

from reactions import reaction_table


def process_event(event):
    for reaction in reaction_table:
        if reaction.should_perform(event):
            reaction.perform(event)


def process_event_queue(world):
    while len(event_queue) > 0:
        event = event_queue.popleft()
        process_event(event)


def process_tick_events(world):
    e = Event("tick", None)
    for thing in world.get_all_things():
        e.target = thing
        process_event(e)
