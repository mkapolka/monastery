from properties.location_properties import HasStomach, get_all_contents
from properties.properties import Flammable, Burning, ShrinkOnEat, TeapotShaped, Boiling, Hot
from reaction import Reaction, enqueue_event, Event
import properties as p
from thing import Thing, destroy_thing


class AlightWhenBurned(Reaction):
    predicates = [Flammable]
    event = "burn"

    @classmethod
    def perform(cls, event):
        event.target.become(Burning)


class BoilBoilable(Reaction):
    predicates = [p.Boilable, Hot]
    anti_predicates = [Boiling]
    event = "tick"

    @classmethod
    def perform(cls, event):
        event.target.tell_room("%s starts boiling!" % event.target.name)
        event.target.become(Boiling)


class BoilOff(Reaction):
    predicates = [Boiling]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if event.target.size > Thing.Size.tiny:
            event.target.tell_room("Some of %s boils away" % event.target.name)
            event.target.size -= 1
        else:
            event.target.tell_room("%s boils away to nothing..." % event.target.name)
            destroy_thing(event.target)


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


class WhistleyTeapot(Reaction):
    predicates = [TeapotShaped]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if thing.is_property(Boiling):
                event.target.tell_room("%s begins whistling furiously!" % event.target.name)


class HeatContents(Reaction):
    predicates = [Hot]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if not thing.is_property(Hot):
                thing.tell_room("%s heats up." % thing.name)
                thing.become(Hot)
