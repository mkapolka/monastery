from reaction import Reaction, enqueue_event, Event
from properties.properties import Flammable, Burning, ShrinkOnEat
from properties.location_properties import HasStomach

class AlightWhenBurned(Reaction):
    predicates = [Flammable]
    event = "burn"

    @classmethod
    def perform(cls, event):
        event.target.become(Burning)

class BurnNearby(Reaction):
    predicates = [Burning]
    event = "tick"

    @classmethod
    def perform(cls, event):
        neighbors = [t for t in event.target.location.things if t != event.target]
        for neighbor in neighbors:
            event.target.tell_room("%s burns %s" % (event.target.name, neighbor.name))

class DigestContents(Reaction):
    predicates = [HasStomach]
    event = "tick"

    @classmethod
    def perform(cls, event):
        contents = event.target.get_property(HasStomach).get_all_things()
        for thing in contents:
            enqueue_event(Event("digest", thing, digester=event.target))

class ShrinkDigestible(Reaction):
    predicates = [ShrinkOnEat]
    event = "digest"

    @classmethod
    def perform(cls, event):
        event.target.unbecome(ShrinkOnEat)
        # Get the owner of the stomach digesting this
        event.digester.tell("The world feels larger somehow...")
        event.digester.size -= 1
