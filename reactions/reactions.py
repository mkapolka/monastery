import random

from enums import Size
from properties.location_properties import HasStomach, get_all_contents, are_touching
from properties.properties import Flammable, Burning, ShrinkOnEat, TeapotShaped, Boiling, Hot
from reaction import Reaction, enqueue_event, Event
from thing import destroy_thing, calc_hp
from utils import sentence
from templates import instantiate_template
import properties as p
import properties.spawner as sp


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
        if random.random() < .25:
            event.target.broadcast("%s starts boiling!" % event.target.name)
            event.target.become(Boiling)


class BoilOff(Reaction):
    predicates = [Boiling]
    event = "tick"

    @classmethod
    def perform(cls, event):
        event.target.attack(max(event.target.max_hp / 10, 1), 'boil')
        if event.target.hp <= calc_hp(event.target, size=event.target.size - 1):
            if event.target.size > Size.tiny:
                event.target.broadcast("Some of %s boils away" % event.target.name)
                event.target.size -= 1
            else:
                event.target.broadcast("%s boils away to nothing..." % event.target.name)
                destroy_thing(event.target)


class BurnNearby(Reaction):
    predicates = [Burning]
    event = "tick"

    @classmethod
    def perform(cls, event):
        neighbors = [t for t in event.target.location.things if t != event.target]
        for neighbor in neighbors:
            event.target.broadcast("%s burns %s" % (event.target.name, neighbor.name))


class CutOpen(Reaction):
    anti_predicates = [p.Open, p.Hard]
    event = "slash"

    @classmethod
    def perform(cls, event):
        if event.target.locations:
            thing = event.target
            thing.become(p.Open, custom_description='has been slashed open')
            thing.unbecome(p.Openable)
            event.attacker.tell("You slash open %s!" % thing.name)


class DigestContents(Reaction):
    predicates = [HasStomach]
    event = "tick"

    @classmethod
    def perform(cls, event):
        contents = event.target.get_property(HasStomach).get_all_things()
        for thing in contents:
            enqueue_event(Event("digest", thing, digester=event.target))


class DigestDigestibles(Reaction):
    predicates = [p.Digestible]
    event = "digest"

    @classmethod
    def perform(cls, event):
        event.target.tell_room("%s dissolves into mush" % event.target.name)
        destroy_thing(event.target)


class DissolveIntoLiquid(Reaction):
    predicates = [p.Dissolvable]
    event = "tick"

    @classmethod
    def perform(cls, event):
        liquid_neighbors = [t for t in event.target.location.things if t.is_property(p.Liquid) and are_touching(event.target, t)]
        if liquid_neighbors:
            into = liquid_neighbors[0]
            event.target.broadcast("%s dissolves into %s" % (event.target.name, into.name))
            liquid_neighbors[0].transfer_properties(event.target, event.target.get_properties_of_types(['chemical']))
            destroy_thing(event.target)


class HeatContents(Reaction):
    predicates = [Hot]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if not thing.is_property(Hot):
                thing.broadcast("%s heats up." % thing.name)
                thing.become(Hot)


class Rot(Reaction):
    predicates = [p.Decomposable]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if not event.target.alive:
            event.target.hp -= 1
            if event.target.hp <= 0:
                event.target.broadcast("%s decomposes into nothing" % (event.target.name))
                destroy_thing(event.target)


class ShrinkDigestible(Reaction):
    predicates = [ShrinkOnEat]
    event = "digest"

    @classmethod
    def perform(cls, event):
        if event.digester.size > Size.small:
            event.target.unbecome(ShrinkOnEat)
            # Get the owner of the stomach digesting this
            event.digester.tell("The world feels larger somehow...")
            event.digester.broadcast("%s shrinks!" % event.digester.name)
            event.digester.size -= 1
            for thing in get_all_contents(event.digester):
                thing.size -= 1
                if thing.size < 0:
                    thing.tell_room("%s winks out of existence!" % thing.name)
                    thing.tell("You wink out of existence!")
                    destroy_thing(thing)


class SpawnMice(Reaction):
    predicates = [sp.SpawnsMice]
    event = "tick"

    @classmethod
    def perform(cls, event):
        prop = event.target.get_property(sp.SpawnsMice)
        if random.random() < .25 and len(prop.spawned_things) < prop.max_things:
            created = instantiate_template(sp.SpawnsMice.template)
            prop.add_thing(created)
            event.target.location.add_thing(created)
            event.target.tell_room("%s crawls out of %s" % (created.name, event.target.name))


class MergeLiquids(Reaction):
    predicates = [p.Liquid]
    event = "tick"

    @classmethod
    def perform(cls, event):
        if not event.target.destroyed:
            neighbors = [t for t in event.target.location.things if t != event.target
                         and are_touching(event.target, t)
                         and t.is_property(p.Liquid)]
            if neighbors:
                neighbor_names = [name for name in map(lambda x: x.name, neighbors) if name != event.target.name]
                if neighbor_names:
                    event.target.broadcast('%s mixes with %s' % (event.target.name, sentence(neighbor_names)))
                for neighbor in neighbors:
                    event.target.size = max(event.target.size, neighbor.size)
                    event.target.transfer_properties(neighbor, neighbor.get_properties_of_types(['physical', 'chemical']))
                    destroy_thing(neighbor)


class WhistleyTeapot(Reaction):
    predicates = [TeapotShaped]
    event = "tick"

    @classmethod
    def perform(cls, event):
        for thing in get_all_contents(event.target):
            if thing.is_property(Boiling):
                event.target.broadcast("%s whistles!" % event.target.name)
